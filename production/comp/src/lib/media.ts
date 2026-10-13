// What footage exists (scripts/scan-media.mjs writes the list before every render) and where to fetch it:
// the media server (scripts/media-server.mjs) serves the song and production/ from the repo.
import {getInputProps} from 'remotion';
import mediaJson from '../data/media.generated.json';

interface Probe {
	file: string;
	width?: number;
	height?: number;
	fps?: number | null;
	frames?: number | null;
}

/** Where a dancer's figure stands in her matte's frame, as fractions of it (tools/matte.py). */
export interface Figure {
	top: number;
	feet: number;
	cx: number;
}

export interface MediaIndex {
	generated: string;
	clips: Record<string, Probe>;
	mattes: Record<string, Probe & {figure?: Figure | null; still?: string | null}>;
	tracking: Record<string, string>;
	plates: Record<string, {file: string; depth: string | null; thumb?: string | null}>;
}

export const media = mediaJson as unknown as MediaIndex;

const props = getInputProps() as {mediaBase?: string; cards?: boolean};
export const MEDIA_BASE = props.mediaBase ?? 'http://127.0.0.1:8765';
/** Force storyboard cards everywhere (the animatic before any footage exists does this by itself). */
export const FORCE_CARDS = Boolean(props.cards);

export const mediaUrl = (repoPath: string) => `${MEDIA_BASE}/${repoPath.split('/').map(encodeURIComponent).join('/')}`;
export const SONG_URL = mediaUrl('Always Allow.mp3');

export const clipFile = (id: string | null) => (id && !FORCE_CARDS ? media.clips[id] ?? null : null);
export const matteFile = (id: string | null) => (id && !FORCE_CARDS ? media.mattes[id] ?? null : null);
export const plateFile = (id: string | null) => (id && !FORCE_CARDS ? media.plates[id] ?? null : null);
export const trackingFile = (id: string | null) => (id ? media.tracking[id] ?? null : null);

/** Whether a shot shows real footage (its clip, matte or plate) rather than its storyboard card. */
export const hasFootage = (shot: {clip: string | null; plate: string | null}, clipPlate: string | null = null) =>
	Boolean(clipFile(shot.clip) || matteFile(shot.clip) || plateFile(shot.plate ?? clipPlate));
