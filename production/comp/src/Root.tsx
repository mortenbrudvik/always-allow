import React from 'react';
import {Composition} from 'remotion';
import {board} from './lib/data';
import {H, W} from './lib/theme';
import {TEASER_FROM, TEASER_TO, TH, TW, Teaser} from './Teaser';
import {Video} from './Video';

// One composition for the whole song at 1920x1080, 24 fps. The animatic is the same composition rendered
// at a third of the size (scripts/render.mjs passes --scale and proxy: true). The 9:16 teaser is its own
// composition, over the finished master (Teaser.tsx).
export const Root: React.FC = () => (
	<>
		<Composition
			id="Main"
			component={Video}
			durationInFrames={board.frames}
			fps={24}
			width={W}
			height={H}
			defaultProps={{proxy: false}}
		/>
		<Composition
			id="Teaser"
			component={Teaser}
			durationInFrames={TEASER_TO - TEASER_FROM}
			fps={24}
			width={TW}
			height={TH}
			defaultProps={{from: TEASER_FROM}}
		/>
	</>
);
