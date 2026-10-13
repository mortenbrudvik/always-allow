"""Time every lyric word against the vocal stem (PLAN.md phase 1).

Two passes over production/stems/vocals.mp3:
1. Forced alignment gives the times. A wav2vec2 CTC model scores every 20 ms of the stem for
   every letter, and a Viterbi pass fits the known text of `Lyrics (Suno).txt` to those scores,
   so each word starts where its first letter is heard. A filler token between lines soaks up
   vocals that aren't on the lyric sheet, such as a chopped repeat in a chant. Where a line's
   first word is echoed and the alignment lands on the echo, the start moves back to the
   first take.
2. Whisper checks them. faster-whisper transcribes the stem on its own; a lyric word that
   Whisper also heard close to its aligned time is marked confirmed.

Whisper's own timestamps aren't used for timing: after a pause it starts a line up to about
0.7 s early, because its first word absorbs part of the silence. Forced alignment knows the
words, so its starts are good to a frame or two.

Writes production/analysis/words.json: every lyric line and word with its start and end, the
bar each line starts in, an alignment confidence, and whether Whisper confirms it. Whisper's
transcript goes to production/analysis/transcript.json, so --transcript can reuse it.

Both models are downloaded from Hugging Face the first time. A CUDA GPU makes both passes
take about a minute; on a CPU they take several.

Usage, with the project's .venv (it has tools/requirements-align.txt):
  .venv/Scripts/python tools/align_lyrics.py                # both passes on the vocal stem
  .venv/Scripts/python tools/align_lyrics.py --transcript production/analysis/transcript.json   # reuse Whisper
  .venv/Scripts/python tools/align_lyrics.py --model medium.en   # a faster Whisper for the check
  .venv/Scripts/python tools/align_lyrics.py --letters      # only the letters, and the p, b and m, to letters.json
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
LYRICS = ROOT / "Lyrics (Suno).txt"
VOCALS = ROOT / "production" / "stems" / "vocals.mp3"
ANALYSIS = ROOT / "production" / "analysis"
SONG = ANALYSIS / "song.json"
ALIGN_MODEL = "facebook/wav2vec2-large-960h-lv60-self"
SR, HOP = 16000, 320  # wav2vec2 works at 16 kHz and outputs one frame per 320 samples (20 ms)
FILLER = "*"
NUMBERS = {"1": "one", "4": "four", "40": "forty", "1000": "thousand"}


def rel(path):
    path = Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def norm(token):
    """Lowercase, drop punctuation and apostrophes, and spell out the few numbers Whisper writes as digits."""
    t = re.sub(r"[^a-z0-9]", "", token.lower())
    return NUMBERS.get(t, t)


def load_lyrics():
    """Return the lyric lines in order. Parenthesised echoes, such as "(always)", are backing
    vocals in the instrumental stem, so they stay in the line's text but get no words."""
    lines, tag = [], None
    for raw in LYRICS.read_text().splitlines():
        s = raw.strip()
        if not s:
            continue
        if s.startswith("["):
            tag = s.strip("[]")
            continue
        words = re.findall(r"[A-Za-z0-9']+", re.sub(r"\([^)]*\)", "", s))
        if words:
            lines.append({"text": s, "tag": tag, "words": words})
    return lines


def transcribe(audio, model_name):
    from faster_whisper import WhisperModel
    model = WhisperModel(model_name, device="auto", compute_type="auto")
    segments, _ = model.transcribe(str(audio), language="en", beam_size=5, word_timestamps=True,
                                   condition_on_previous_text=False, vad_filter=False)
    words = []
    for seg in segments:
        print(f"  {seg.start:7.2f}-{seg.end:7.2f} {seg.text.strip()}")
        for w in seg.words or []:
            # Whisper can put several words in one token ("1,000", "hand-me"); split them evenly.
            parts = [p for p in re.split(r"[\s\-]+", w.word.strip()) if norm(p)]
            for k, p in enumerate(parts):
                step = (w.end - w.start) / len(parts)
                words.append({"word": p, "start": round(w.start + k * step, 3),
                              "end": round(w.start + (k + 1) * step, 3), "probability": round(w.probability, 3)})
    return words


def emissions(audio, model_name, chunk_s=20, pad_s=1):
    """Letter log-probabilities for every 20 ms frame, computed in overlapping chunks so a long
    song fits in memory. Returns (frames x classes, the vocabulary, the blank id)."""
    import torch
    from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = Wav2Vec2Processor.from_pretrained(model_name)
    model = Wav2Vec2ForCTC.from_pretrained(model_name).to(device).eval()
    vocab = processor.tokenizer.get_vocab()
    blank = processor.tokenizer.pad_token_id
    n = len(audio) // HOP
    em = np.full((n, len(vocab)), -30.0, np.float32)
    em[:, blank] = 0.0  # frames a chunk doesn't reach count as silence
    chunk, pad = chunk_s * SR, pad_s * SR
    for s in range(0, len(audio), chunk):
        a0, a1 = max(0, s - pad), min(len(audio), s + chunk + pad)
        x = processor(audio[a0:a1], sampling_rate=SR, return_tensors="pt").input_values.to(device)
        with torch.inference_mode():
            lp = torch.log_softmax(model(x).logits[0].float(), dim=-1).cpu().numpy()
        f0, g0 = (s - a0) // HOP, s // HOP  # the chunk's own part: skip the left padding
        k = max(0, min(chunk // HOP, n - g0, len(lp) - f0))
        em[g0:g0 + k] = lp[f0:f0 + k]
    return em, vocab, blank


def label_sequence(lines, vocab):
    """The text the audio must follow: each word's letters, '|' between words, and an optional-sounding
    filler between lines. Returns the labels and, per word, the index of its first and last letter."""
    seq, spans = [], []
    for li, line in enumerate(lines):
        if li:
            seq += ["|", FILLER, "|"]
        for wi, w in enumerate(line["words"]):
            if wi:
                seq.append("|")
            letters = [c for c in w.upper() if c in vocab]
            spans.append((len(seq), len(seq) + len(letters) - 1))
            seq += letters
    return seq, spans


def viterbi(em, ids, blank):
    """The most likely CTC path of the labels `ids` through the frame log-probs `em`.
    Returns the state of every frame: state 2i+1 is label i, even states are blanks."""
    T, S = len(em), 2 * len(ids) + 1
    lab = np.full(S, blank)
    lab[1::2] = ids
    skip = np.zeros(S, bool)  # a label may skip the blank before it unless it repeats the previous label
    skip[3::2] = lab[3::2] != lab[1:-2:2]
    neg = np.float32(-1e30)
    score = np.full(S, neg, np.float32)
    score[0], score[1] = em[0, blank], em[0, lab[1]]
    back = np.zeros((T, S), np.int8)  # how each state was reached: 0 stayed, 1 from s-1, 2 from s-2
    pad1, pad2 = np.full(1, neg, np.float32), np.full(2, neg, np.float32)
    for t in range(1, T):
        adv1 = np.concatenate((pad1, score[:-1]))
        adv2 = np.where(skip, np.concatenate((pad2, score[:-2])), neg)
        best = np.maximum(score, np.maximum(adv1, adv2))
        back[t] = np.where(best == score, 0, np.where(best == adv1, 1, 2))
        score = best + em[t, lab]
    s = S - 1 if score[S - 1] >= score[S - 2] else S - 2
    if score[s] <= neg / 2:
        sys.exit("The lyrics don't fit the audio: too many letters for its length.")
    path = np.empty(T, np.int32)
    for t in range(T - 1, -1, -1):
        path[t] = s
        s -= int(back[t, s])  # a Python int: NumPy 2 would keep int8 arithmetic and overflow past state 127
    return path


def earlier_take(heard, word, f_from, f_to, within=0.4):
    """The first frame in [f_from, f_to) where the model clearly hears the word's first letters in
    order, within `within` seconds, or None. `heard` is the greedy decode: (frame, letter) pairs."""
    letters = [c for i, c in enumerate(word.upper()) if c.isalpha() and (i == 0 or c != word.upper()[i - 1])]
    want = letters[:3]
    if len(want) < 2:  # one letter matches too much by chance
        return None
    cand = [(t, c) for t, c in heard if f_from <= t < f_to]
    for i, (t, c) in enumerate(cand):
        if c != want[0]:
            continue
        k = 1
        for t2, c2 in cand[i + 1:]:
            if (t2 - t) * HOP / SR > within:
                break
            if c2 == want[k]:
                k += 1
                if k == len(want):
                    return t
    return None


def force_align(audio, lines, model_name, filler_penalty, letters=None):
    """Start, end, confidence (mean letter log-prob) and a note for every lyric word, in order. Pass a list as
    `letters` to have it filled with each word's letters: [(letter, start, end), ...] per word, in the same order."""
    import time
    t0 = time.time()
    em, vocab, blank = emissions(audio, model_name)
    print(f"  scored {len(em)} frames in {time.time() - t0:.0f} s")
    greedy = em.argmax(1)
    inv = {i: c for c, i in vocab.items()}
    heard = [(t, inv[int(g)]) for t, g in enumerate(greedy) if g != blank and (t == 0 or g != greedy[t - 1])]
    speech = [i for i in range(em.shape[1]) if i != blank]
    # The filler matches any speech at a fixed cost per frame, so a vocal that isn't on the sheet
    # goes to it instead of being forced onto the nearest lyric word; silence stays with blank.
    filler = np.logaddexp.reduce(em[:, speech], axis=1) - filler_penalty
    em = np.concatenate((em, filler[:, None]), axis=1)
    vocab = {**vocab, FILLER: em.shape[1] - 1}
    seq, spans = label_sequence(lines, vocab)
    t0 = time.time()
    path = viterbi(em, np.array([vocab[c] for c in seq]), blank)
    print(f"  aligned {len(seq)} labels in {time.time() - t0:.0f} s")
    lab_of_state = np.full(2 * len(seq) + 1, blank)
    lab_of_state[1::2] = [vocab[c] for c in seq]
    out = []
    for first, last in spans:
        f0 = int(np.searchsorted(path, 2 * first + 1, "left"))
        f1 = int(np.searchsorted(path, 2 * last + 1, "right"))
        frames = [t for t in range(f0, f1) if path[t] % 2]  # the frames on its letters
        conf = float(np.mean([em[t, lab_of_state[path[t]]] for t in frames])) if frames else -99.0
        out.append([f0, f1, round(conf, 2), None])
    # Echoes and delay throws repeat a word after the original, and the alignment can land on a
    # repeat. If the model clearly hears a line's first word in the gap before where it landed,
    # the earlier take is the original.
    shift = [0] * len(out)  # frames a word moved to its first take; its letters move with it
    k, prev_end = 0, 0
    for line in lines:
        f0 = out[k][0]
        t = earlier_take(heard, line["words"][0], prev_end, f0)
        if t is not None and (f0 - t) * HOP / SR <= 1.5:
            out[k][0], out[k][3], shift[k] = t, f"moved {(f0 - t) * HOP / SR:.2f} s earlier, to the first take", f0 - t
        k += len(line["words"])
        prev_end = out[k - 1][1]
    if letters is not None:
        for (first, last), back in zip(spans, shift):
            word = []
            for i in range(first, last + 1):  # label i is state 2i+1; the path is monotonic, so its frames are a run
                a = int(np.searchsorted(path, 2 * i + 1, "left")) - back
                b = int(np.searchsorted(path, 2 * i + 1, "right")) - back
                word.append((seq[i], round(a * HOP / SR, 3), round(b * HOP / SR, 3)))
            letters.append(word)
    return [(round(f0 * HOP / SR, 3), round(f1 * HOP / SR, 3), conf, note) for f0, f1, conf, note in out]


BILABIAL = set("PBM")


def closures(word_letters):
    """The letters where the lips close: every p, b and m, except a p before h (ph sounds f), a b after a final m
    (climb), and the second of two bilabials in a row (mm, mp, mb close once)."""
    cs = [c for c, _, _ in word_letters]
    out = []
    for i, c in enumerate(cs):
        if c not in BILABIAL:
            continue
        if c == "P" and i + 1 < len(cs) and cs[i + 1] == "H":
            continue
        if c == "B" and i == len(cs) - 1 and i and cs[i - 1] == "M":
            continue
        if i and cs[i - 1] in BILABIAL:
            continue
        out.append(i)
    return out


def write_letters(audio, lines, args):
    """The letters-only pass (BRIEF.md step 3's closure check): every letter's time, and the p, b and m where the lips
    close, to production/analysis/letters.json. words.json is left as it is; the word starts are compared with it."""
    per_word = []
    timed = force_align(audio, lines, args.align_model, args.filler_penalty, letters=per_word)
    words = json.loads((ANALYSIS / "words.json").read_text())
    known = [w["start"] for line in words["lines"] for w in line["words"]]
    drift = max(abs(a - t[0]) for a, t in zip(known, timed)) if len(known) == len(timed) else None
    out, bilabials, k = [], [], 0
    for li, line in enumerate(lines):
        ws = []
        for wi, w in enumerate(line["words"]):
            ls = per_word[k]
            ws.append({"word": w, "start": timed[k][0], "letters": [[c.lower(), a, b] for c, a, b in ls]})
            for i in closures(ls):
                bilabials.append({"line": li, "word_index": wi, "word": w, "letter": ls[i][0].lower(),
                                  "start": ls[i][1], "end": ls[i][2]})
            k += 1
        out.append({"line": li, "text": line["text"], "words": ws})
    (ANALYSIS / "letters.json").write_text(json.dumps({
        "method": f"{args.align_model} CTC forced alignment of {LYRICS.name}, the same pass as words.json",
        "max_word_start_difference_s": None if drift is None else round(drift, 3),
        "notes": [
            "Each letter's start and end, in song seconds: the frames the alignment gave it (20 ms each). A letter is "
            "placed where it's heard; the lips close for a p or b just before that.",
            "closures lists the p, b and m where the lips close, skipping ph, a b after a final m, and the second of "
            "two bilabials in a row. tools/closure_check.py checks them in a repaired clip.",
            "max_word_start_difference_s compares this pass's word starts with words.json, which it doesn't change.",
        ],
        "closures": bilabials,
        "lines": out,
    }, indent=1))
    print(f"{len(bilabials)} closures (p, b, m) in {len(lines)} lines; word starts within "
          f"{'?' if drift is None else f'{drift * 1000:.0f} ms'} of words.json. Wrote {(ANALYSIS / 'letters.json').relative_to(ROOT)}")


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--audio", default=str(VOCALS), help="audio to align (default: the vocal stem)")
    p.add_argument("--model", default="large-v3", help="faster-whisper model for the check (default large-v3)")
    p.add_argument("--transcript", help="reuse a saved transcript.json instead of running Whisper")
    p.add_argument("--align-model", default=ALIGN_MODEL, help=f"wav2vec2 CTC model (default {ALIGN_MODEL})")
    p.add_argument("--filler-penalty", type=float, default=3.0,
                   help="cost per frame of filing speech under the filler instead of a lyric word (default 3.0)")
    p.add_argument("--letters", action="store_true",
                   help="only write every letter's time, and the p, b and m, to letters.json; words.json is left alone")
    args = p.parse_args()

    audio_path = Path(args.audio).resolve()
    if args.letters:
        from faster_whisper.audio import decode_audio
        print(f"Aligning the letters to {rel(audio_path)} with {args.align_model}:")
        write_letters(decode_audio(str(audio_path), sampling_rate=SR), load_lyrics(), args)
        return
    if args.transcript:
        saved = json.loads(Path(args.transcript).read_text())
        heard, whisper = saved["words"], saved["model"]
    else:
        print(f"Transcribing {rel(audio_path)} with {args.model} (the first run downloads the model):")
        heard, whisper = transcribe(audio_path, args.model), args.model
        ANALYSIS.mkdir(parents=True, exist_ok=True)
        (ANALYSIS / "transcript.json").write_text(json.dumps(
            {"audio": rel(audio_path), "model": whisper, "words": heard}, indent=1))

    from faster_whisper.audio import decode_audio
    print(f"Aligning the lyrics to {rel(audio_path)} with {args.align_model}:")
    lines = load_lyrics()
    timed = force_align(decode_audio(str(audio_path), sampling_rate=SR), lines, args.align_model, args.filler_penalty)

    # A word is confirmed when Whisper heard it within 1.2 s of its aligned start (Whisper runs early).
    heard_at = {}
    for h in heard:
        heard_at.setdefault(norm(h["word"]), []).append(h["start"])

    def confirmed(word, start):
        return any(abs(t - start) <= 1.2 for t in heard_at.get(norm(word), []))

    song = json.loads(SONG.read_text())
    down, first_bar = song["downbeats_s"], -8  # downbeats_s[0] is bar -8 (see song.json notes)

    def bar(t):
        k = max(i for i in range(len(down)) if down[i] <= t) if t >= down[0] else 0
        nxt = down[k + 1] if k + 1 < len(down) else down[k] + song["bar_s"]
        return round(k + first_bar + (t - down[k]) / (nxt - down[k]), 2)

    def section(t):
        return next((s["label"] for s in song["sections"] if s["start"] <= t < s["end"]), song["sections"][-1]["label"])

    out, k = [], 0
    for line in lines:
        words = []
        for w in line["words"]:
            start, end, conf, note = timed[k]
            words.append({"word": w, "start": start, "end": end, "confidence": conf, "whisper": confirmed(w, start),
                          **({"note": note} if note else {})})
            k += 1
        start, end = words[0]["start"], words[-1]["end"]
        out.append({"text": line["text"], "sheet_section": line["tag"], "start": start, "end": end,
                    "bar": bar(start), "song_json_section": section(start),
                    "confidence": round(float(np.mean([w["confidence"] for w in words])), 2),
                    "whisper": round(sum(w["whisper"] for w in words) / len(words), 2), "words": words})

    total = sum(w["whisper"] for line in out for w in line["words"]) / k
    (ANALYSIS / "words.json").write_text(json.dumps({
        "method": f"{args.align_model} CTC forced alignment of {LYRICS.name} to {rel(audio_path)}, "
                  f"checked against faster-whisper {whisper}",
        "whisper_confirmed_fraction": round(total, 3),
        "notes": [
            "start is when the word's first letter is heard, to about 20-40 ms. end is when its last letter "
            "is recognised; a held vowel can ring on past it.",
            "confidence is the mean log-probability of the word's letters: near 0 is a clean match, below "
            "about -3 is doubtful.",
            "whisper is true when Whisper independently heard the word within 1.2 s of its start; for a line, "
            "it's the fraction of its words. Check a line with low confidence or low whisper by ear.",
            "A word with a note was moved to an earlier take: the vocal repeats it (an echo or delay throw) "
            "and the alignment had landed on the repeat.",
            "'bar' uses the grid in song.json: bar 0 is the first drop.",
        ],
        "lines": out,
    }, indent=1))

    print(f"\nWhisper confirms {100 * total:.0f} % of lyric words. Lines (start, bar, confidence, Whisper, text):")
    for line in out:
        flag = "  <- check" if line["confidence"] < -3 or line["whisper"] < 0.5 else ""
        flag += "  (moved to the first take)" if any("note" in w for w in line["words"]) else ""
        print(f"  {line['start']:7.2f}  bar {line['bar']:6.2f}  {line['confidence']:5.2f}  "
              f"{100 * line['whisper']:3.0f} %  {line['text']}{flag}")
    print(f"Wrote {(ANALYSIS / 'words.json').relative_to(ROOT)}")


if __name__ == "__main__":
    main()
