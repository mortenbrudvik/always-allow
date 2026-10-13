// The UI kit: a generic look-alike of agent permission prompts and the tools around them, never a copy of
// any product's UI (BRIEF.md). All drawn in code; every prop is a value for this frame, so the chapter
// computes it from the time and nothing animates on its own.
import React from 'react';
import {C, FONT} from '../lib/theme';

export const px = (n: number) => `${n}px`;

// ---- the permission window ---------------------------------------------------------------------------

export interface DialogProps {
	x: number; // top-left, frame pixels
	y: number;
	w: number; // width; the window is 16:9 (its size tag says WxH)
	scopes: string[];
	shown?: number; // how many scope lines have typed in (fractional: the last one is part-typed)
	hover?: 'deny' | 'once' | 'always' | null;
	pressed?: number; // 0-1: [Always allow] going down
	footnote?: number; // 0-1: the 97% line appearing
	glow?: number; // 0-1: the window lights the room
	title?: string;
	requester?: string;
	opacity?: number;
	blankBody?: boolean; // the full-screen "Allow?" window: only the buttons
	scale?: number; // extra scale for the content (a wall-sized window keeps readable buttons)
}

export const DIALOG_BASE = 960;
/** The button bar's grey, also the ground the big button sits on. */
export const BUTTON_BAR = '#efefec';

export const Dialog: React.FC<DialogProps> = ({
	x, y, w, scopes, shown = scopes.length, hover = null, pressed = 0, footnote = 0, glow = 0,
	title = 'Permission request', requester = 'agent_01', opacity = 1, blankBody = false, scale = 1,
}) => {
	const h = (w * 9) / 16;
	const s = (w / DIALOG_BASE) * scale;
	const full = Math.floor(shown);
	const part = shown - full;
	const lines = scopes.slice(0, Math.min(scopes.length, full + (part > 0 ? 1 : 0)));
	const btn = (kind: 'deny' | 'once' | 'always', label: string) => {
		const on = hover === kind;
		const primary = kind === 'always';
		const down = primary ? pressed : 0;
		return (
			<div
				style={{
					height: 60 * s,
					padding: `0 ${26 * s}px`,
					display: 'flex',
					alignItems: 'center',
					borderRadius: 11 * s,
					fontFamily: FONT.sans,
					fontWeight: primary ? 650 : 550,
					fontSize: 23 * s,
					letterSpacing: '-0.005em',
					color: primary ? C.paper : kind === 'deny' ? C.ink2 : C.ink,
					background: primary ? (down > 0 ? '#a94f33' : C.terracotta) : on ? 'rgba(11,12,14,0.06)' : 'transparent',
					border: kind === 'once' ? `${1.6 * s}px solid ${on ? C.ink : 'rgba(11,12,14,0.35)'}` : 'none',
					boxShadow: on ? `0 0 0 ${4 * s}px ${primary ? 'rgba(201,100,66,0.28)' : 'rgba(11,12,14,0.1)'}` : primary ? `0 ${2 * s}px ${6 * s}px rgba(201,100,66,0.35)` : 'none',
					transform: `translateY(${down * 3 * s}px) scale(${1 - down * 0.03})`,
				}}
			>
				{label}
			</div>
		);
	};
	return (
		<div
			style={{
				position: 'absolute',
				left: x,
				top: y,
				width: w,
				height: h,
				opacity,
				background: C.white,
				borderRadius: 16 * s,
				border: `${Math.max(1, s)}px solid ${C.hair}`,
				boxShadow: `0 ${30 * s}px ${90 * s}px rgba(0,0,0,0.45)${glow ? `, 0 0 ${220 * s * glow}px ${60 * s * glow}px rgba(207,224,238,${0.35 * glow})` : ''}`,
				overflow: 'hidden',
				display: 'flex',
				flexDirection: 'column',
			}}
		>
			<div style={{height: 64 * s, display: 'flex', alignItems: 'center', padding: `0 ${26 * s}px`, borderBottom: `${Math.max(1, s)}px solid ${C.hair}`, gap: 14 * s}}>
				<span style={{width: 14 * s, height: 14 * s, borderRadius: 7 * s, background: C.terracotta}} />
				<span style={{fontFamily: FONT.sans, fontWeight: 600, fontSize: 24 * s, color: C.ink}}>{title}</span>
				<span style={{flex: 1}} />
				<span style={{fontFamily: FONT.mono, fontSize: 18 * s, color: C.ink2}}>{requester}</span>
				<span style={{fontFamily: FONT.sans, fontSize: 26 * s, color: C.ink2, marginLeft: 16 * s}}>×</span>
			</div>
			<div style={{flex: 1, padding: `${34 * s}px ${40 * s}px 0`, position: 'relative'}}>
				{!blankBody && (
					<>
						<div style={{fontFamily: FONT.sans, fontWeight: 500, fontSize: 30 * s, color: C.ink, marginBottom: 18 * s}}>
							<span style={{fontFamily: FONT.mono, fontSize: 27 * s}}>{requester}</span> wants to:
						</div>
						{lines.map((l, i) => {
							const typed = i < full ? l : l.slice(0, Math.max(1, Math.round(l.length * part)));
							return (
								<div key={i} style={{fontFamily: FONT.mono, fontSize: 22 * s, lineHeight: 1.55, color: i === lines.length - 1 && l === 'everything' ? C.terracotta : C.ink}}>
									<span style={{color: C.ink2}}>{'·  '}</span>
									{typed}
								</div>
							);
						})}
					</>
				)}
				{footnote > 0 && (
					<div style={{position: 'absolute', left: 40 * s, bottom: 18 * s, opacity: footnote, fontFamily: FONT.sans, fontSize: 19 * s, color: C.ink2}}>
						97% of requests like this are approved.<sup>1</sup>
						<div style={{fontFamily: FONT.mono, fontSize: 14 * s, marginTop: 4 * s}}>1 Anthropic, 7 Aug 2026</div>
					</div>
				)}
			</div>
			<div style={{height: 104 * s, display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 14 * s, padding: `0 ${30 * s}px`, borderTop: `${Math.max(1, s)}px solid ${C.hair}`, background: BUTTON_BAR}}>
				{btn('deny', 'Deny')}
				{btn('once', 'Allow once')}
				{btn('always', 'Always allow')}
			</div>
		</div>
	);
};

/** Where the dialog's buttons are, for a cursor that moves to them (frame pixels, their centres). */
export const dialogButtons = (x: number, y: number, w: number, scale = 1) => {
	const h = (w * 9) / 16;
	const s = (w / DIALOG_BASE) * scale;
	const cy = y + h - 52 * s;
	const alwaysW = 190 * s;
	const onceW = 168 * s;
	const right = x + w - 30 * s;
	return {
		always: {x: right - alwaysW / 2, y: cy},
		once: {x: right - alwaysW - 14 * s - onceW / 2, y: cy},
		deny: {x: right - alwaysW - onceW - 28 * s - 50 * s, y: cy},
	};
};

/** [Always allow] alone, big: centred on (cx, cy), w wide; `pressed` 0-1 takes it down. */
export const BigButton: React.FC<{cx: number; cy: number; w: number; pressed?: number; glow?: number}> = ({cx, cy, w, pressed = 0, glow = 1}) => {
	const h = w * 0.28;
	return (
		<div
			style={{
				position: 'absolute',
				left: cx - w / 2,
				top: cy - h / 2,
				width: w,
				height: h,
				borderRadius: w * 0.051,
				background: pressed > 0 ? '#a94f33' : C.terracotta,
				display: 'flex',
				alignItems: 'center',
				justifyContent: 'center',
				fontFamily: FONT.sans,
				fontWeight: 650,
				fontSize: w * 0.121,
				letterSpacing: '-0.02em',
				color: C.paper,
				whiteSpace: 'nowrap',
				boxShadow: `0 0 0 ${w * 0.026 * glow * (1 - pressed)}px rgba(201,100,66,0.22)`,
				transform: `translateY(${pressed * w * 0.012}px) scale(${1 - 0.03 * pressed})`,
			}}
		>
			Always allow
		</div>
	);
};

export const Cursor: React.FC<{x: number; y: number; size?: number; opacity?: number}> = ({x, y, size = 36, opacity = 1}) => (
	<svg width={size} height={size * 1.5} viewBox="0 0 24 36" style={{position: 'absolute', left: x - 2, top: y - 2, opacity, overflow: 'visible'}}>
		<path d="M2 2 L2 28 L9 21.5 L13.5 32 L18 30 L13.6 19.8 L22.5 19.8 Z" fill={C.ink} stroke={C.paper} strokeWidth={2} strokeLinejoin="round" />
	</svg>
);

export const SizeTag: React.FC<{x: number; y: number; text: string; dark?: boolean}> = ({x, y, text, dark = true}) => (
	<div style={{position: 'absolute', left: x, top: y, fontFamily: FONT.mono, fontSize: 17, letterSpacing: '0.08em', color: dark ? 'rgba(216,228,220,0.75)' : 'rgba(11,12,14,0.65)', whiteSpace: 'nowrap'}}>
		<span style={{color: C.terracotta}}>▍</span> {text}
	</div>
);

// ---- chat ------------------------------------------------------------------------------------------

export const ChatBox: React.FC<{x: number; y: number; w: number; text: string; caret: boolean; sendLit?: number; placeholder?: string; scale?: number}> = ({
	x, y, w, text, caret, sendLit = 0, placeholder = 'Message agent_01…', scale = 1,
}) => {
	const s = scale;
	return (
		<div style={{position: 'absolute', left: x, top: y, width: w, minHeight: 78 * s, background: C.paper, borderRadius: 22 * s, border: `1px solid ${C.hair}`, boxShadow: '0 18px 50px rgba(0,0,0,0.35)', display: 'flex', alignItems: 'center', padding: `${14 * s}px ${16 * s}px ${14 * s}px ${28 * s}px`, gap: 16 * s}}>
			<div style={{flex: 1, fontFamily: FONT.sans, fontSize: 27 * s, color: text ? C.ink : C.shadowGrey, lineHeight: 1.3}}>
				{text || placeholder}
				{caret && <span style={{display: 'inline-block', width: 3 * s, height: 30 * s, marginLeft: 2, background: C.ink, verticalAlign: 'text-bottom'}} />}
			</div>
			<div style={{width: 50 * s, height: 50 * s, borderRadius: 25 * s, background: sendLit > 0 ? C.terracotta : C.paleGrey, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${1 + 0.12 * sendLit})`}}>
				<svg width={22 * s} height={22 * s} viewBox="0 0 24 24">
					<path d="M12 20 V5 M5 11 L12 4 L19 11" stroke={C.paper} strokeWidth={2.6} fill="none" strokeLinecap="round" strokeLinejoin="round" />
				</svg>
			</div>
		</div>
	);
};

export const Bubble: React.FC<{x: number; y: number; w: number; text: string; meta?: string; opacity?: number; tone?: 'user' | 'agent'; scale?: number}> = ({x, y, w, text, meta, opacity = 1, tone = 'user', scale = 1}) => (
	<div style={{position: 'absolute', left: x, top: y, width: w, opacity}}>
		<div style={{background: tone === 'user' ? C.paper : C.black, color: tone === 'user' ? C.ink : C.greenWhite, border: tone === 'agent' ? `1px solid rgba(216,228,220,0.25)` : 'none', borderRadius: `${22 * scale}px ${22 * scale}px ${6 * scale}px ${22 * scale}px`, padding: `${16 * scale}px ${22 * scale}px`, fontFamily: FONT.sans, fontSize: 25 * scale, lineHeight: 1.32, boxShadow: '0 14px 40px rgba(0,0,0,0.3)'}}>
			{text}
		</div>
		{meta && <div style={{marginTop: 8, fontFamily: FONT.mono, fontSize: 15 * scale, letterSpacing: '0.06em', color: 'rgba(216,228,220,0.7)', textAlign: 'right'}}>{meta}</div>}
	</div>
);

// ---- windows, terminals, notifications ----------------------------------------------------------------

export const BrowserWindow: React.FC<{x: number; y: number; w: number; h: number; title: string; path?: string; lines?: number; seed?: number; opacity?: number; accent?: boolean; children?: React.ReactNode}> = ({
	x, y, w, h, title, path, lines = 6, seed = 0, opacity = 1, accent = false, children,
}) => (
	<div style={{position: 'absolute', left: x, top: y, width: w, height: h, opacity, background: C.paper, borderRadius: 12, border: `1px solid ${C.hair}`, boxShadow: '0 20px 60px rgba(0,0,0,0.4)', overflow: 'hidden'}}>
		<div style={{height: 38, background: '#e7e8ea', display: 'flex', alignItems: 'center', gap: 8, padding: '0 12px'}}>
			{[0, 1, 2].map((i) => (
				<span key={i} style={{width: 10, height: 10, borderRadius: 5, background: i === 0 && accent ? C.terracotta : C.shadowGrey}} />
			))}
			<div style={{marginLeft: 10, height: 26, padding: '0 14px', borderRadius: '8px 8px 0 0', background: C.paper, display: 'flex', alignItems: 'center', fontFamily: FONT.sans, fontSize: 14, color: C.ink, whiteSpace: 'nowrap', overflow: 'hidden', maxWidth: w - 90}}>
				{title}
			</div>
		</div>
		{path && (
			<div style={{height: 30, margin: '8px 12px', borderRadius: 15, background: '#f1f1ef', fontFamily: FONT.mono, fontSize: 13, color: C.ink2, display: 'flex', alignItems: 'center', padding: '0 14px', whiteSpace: 'nowrap', overflow: 'hidden'}}>
				{path}
			</div>
		)}
		<div style={{padding: '10px 18px'}}>
			{children ??
				Array.from({length: lines}).map((_, i) => (
					<div key={i} style={{height: 12, margin: '10px 0', borderRadius: 6, background: i === 0 ? C.ink : C.paleGrey, width: `${35 + ((seed * 37 + i * 53) % 55)}%`, opacity: i === 0 ? 0.8 : 1}} />
				))}
		</div>
	</div>
);

export const Terminal: React.FC<{x: number; y: number; w: number; h: number; lines: string[]; title?: string; fontSize?: number; opacity?: number; cursor?: boolean}> = ({
	x, y, w, h, lines, title = 'agent_01 — zsh', fontSize = 20, opacity = 1, cursor = true,
}) => {
	const rows = Math.floor((h - 50) / (fontSize * 1.45));
	const shown = lines.slice(-rows);
	return (
		<div style={{position: 'absolute', left: x, top: y, width: w, height: h, opacity, background: 'rgba(11,12,14,0.94)', borderRadius: 12, border: '1px solid rgba(216,228,220,0.22)', boxShadow: '0 24px 70px rgba(0,0,0,0.5)', overflow: 'hidden'}}>
			<div style={{height: 36, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FONT.mono, fontSize: 14, color: 'rgba(216,228,220,0.6)', borderBottom: '1px solid rgba(216,228,220,0.14)'}}>{title}</div>
			<div style={{padding: '10px 18px', fontFamily: FONT.mono, fontSize, lineHeight: 1.45, color: C.greenWhite, whiteSpace: 'pre'}}>
				{shown.map((l, i) => (
					<div key={i} style={{color: l.startsWith('✓') ? C.pass : l.startsWith('$') ? C.greenWhite : 'rgba(216,228,220,0.72)'}}>
						{l}
						{cursor && i === shown.length - 1 && <span style={{background: C.greenWhite, color: C.black}}> </span>}
					</div>
				))}
			</div>
		</div>
	);
};

export const Toast: React.FC<{x: number; y: number; w?: number; title: string; body?: string; opacity?: number; scale?: number; accent?: boolean}> = ({x, y, w = 420, title, body, opacity = 1, scale = 1, accent = true}) => (
	<div style={{position: 'absolute', left: x, top: y, width: w, opacity, transform: `scale(${scale})`, transformOrigin: 'top left', background: 'rgba(244,244,241,0.97)', borderRadius: 16, border: `1px solid ${C.hair}`, boxShadow: '0 14px 40px rgba(0,0,0,0.35)', padding: '14px 18px', display: 'flex', gap: 14}}>
		<span style={{width: 34, height: 34, borderRadius: 9, background: accent ? C.terracotta : C.ink, flexShrink: 0}} />
		<div style={{minWidth: 0}}>
			<div style={{fontFamily: FONT.sans, fontWeight: 600, fontSize: 18, color: C.ink, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>{title}</div>
			{body && <div style={{fontFamily: FONT.sans, fontSize: 16, color: C.ink2, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'}}>{body}</div>}
		</div>
	</div>
);

export const Stamp: React.FC<{x: number; y: number; text: string; k: number; rot?: number; size?: number; colour?: string}> = ({x, y, text, k, rot = -8, size = 120, colour = C.terracotta}) => {
	if (k <= 0) {
		return null;
	}
	const sc = 1 + 0.6 * Math.max(0, 1 - k * 3);
	return (
		<div style={{position: 'absolute', left: x, top: y, transform: `translate(-50%, -50%) rotate(${rot}deg) scale(${sc})`, opacity: Math.min(1, k * 3), border: `${size / 16}px solid ${colour}`, borderRadius: size / 10, padding: `${size / 10}px ${size / 5}px`, fontFamily: FONT.sans, fontWeight: 900, fontSize: size, letterSpacing: '-0.03em', color: colour, whiteSpace: 'nowrap', mixBlendMode: 'multiply'}}>
			{text}
		</div>
	);
};

export const Tag: React.FC<{x: number; y: number; text: string; dark?: boolean; size?: number; accent?: boolean}> = ({x, y, text, dark = true, size = 18, accent = false}) => (
	<div style={{position: 'absolute', left: x, top: y, fontFamily: FONT.mono, fontSize: size, letterSpacing: '0.08em', padding: '6px 10px', color: accent ? C.paper : dark ? C.greenWhite : C.ink, background: accent ? C.terracotta : dark ? 'rgba(11,12,14,0.72)' : 'rgba(244,244,241,0.85)', border: `1px solid ${dark ? 'rgba(216,228,220,0.3)' : 'rgba(11,12,14,0.2)'}`, whiteSpace: 'nowrap'}}>
		{text}
	</div>
);
