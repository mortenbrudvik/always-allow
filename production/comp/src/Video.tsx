// The video, layer by layer (BRIEF.md step 6's order): the shots (footage through the print pass, then the
// explaining graphics and tracking), the transitions' overlays, the kinetic lyrics, the chrome, and a light
// grain over everything. The soundtrack is Always Allow.mp3, muxed by the render script, unedited.
import React from 'react';
import {AbsoluteFill, Audio, getRemotionEnvironment, useCurrentFrame} from 'remotion';
import {loadFonts} from './lib/fonts';
import {SONG_URL} from './lib/media';
import {C} from './lib/theme';
import {Chrome} from './layers/Chrome';
import {Grain} from './layers/Grain';
import {Lyrics} from './layers/Lyrics';
import {Overlays, transitionState} from './layers/Transitions';
import {ShotView} from './ShotView';

loadFonts();

export interface VideoProps {
	proxy: boolean;
	[key: string]: unknown;
}

export const Video: React.FC<VideoProps> = ({proxy}) => {
	const frame = useCurrentFrame();
	const {layers, overlays} = transitionState(frame);
	return (
		<AbsoluteFill style={{background: C.black}}>
			{layers.map((l) => (
				<AbsoluteFill key={l.shot.id} style={l.style}>
					<ShotView shot={l.shot} frame={frame} proxy={proxy} />
				</AbsoluteFill>
			))}
			<Overlays overlays={overlays} />
			<Lyrics frame={frame} />
			<Chrome frame={frame} />
			<Grain frame={frame} />
			{getRemotionEnvironment().isStudio && <Audio src={SONG_URL} />}
		</AbsoluteFill>
	);
};
