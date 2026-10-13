// A light grain over the whole frame (1.5 %, STYLE_BIBLE.md), so the crisp type sits in the same world as
// the printed footage. One noise tile, made once from a fixed seed, shifted to a new place every frame.
import React, {useMemo} from 'react';
import {random} from 'remotion';

const TILE = 256;

const makeTile = () => {
	const c = document.createElement('canvas');
	c.width = TILE;
	c.height = TILE;
	const ctx = c.getContext('2d')!;
	const img = ctx.createImageData(TILE, TILE);
	for (let i = 0; i < TILE * TILE; i++) {
		const v = Math.floor(random(`grain-${i}`) * 255);
		img.data[i * 4] = v;
		img.data[i * 4 + 1] = v;
		img.data[i * 4 + 2] = v;
		img.data[i * 4 + 3] = 255;
	}
	ctx.putImageData(img, 0, 0);
	return c.toDataURL('image/png');
};

export const Grain: React.FC<{frame: number; strength?: number}> = ({frame, strength = 0.06}) => {
	const url = useMemo(makeTile, []);
	const ox = Math.floor(random(`gx-${frame}`) * TILE);
	const oy = Math.floor(random(`gy-${frame}`) * TILE);
	return (
		<div
			style={{
				position: 'absolute',
				inset: 0,
				backgroundImage: `url(${url})`,
				backgroundPosition: `${ox}px ${oy}px`,
				opacity: strength,
				mixBlendMode: 'overlay',
				pointerEvents: 'none',
			}}
		/>
	);
};
