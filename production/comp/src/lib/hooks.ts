// Loading helpers that hold the render until their media is ready (Remotion's delayRender).
import {useEffect, useState} from 'react';
import {cancelRender, continueRender, delayRender} from 'remotion';

const cache = new Map<string, HTMLImageElement>();

/** An image from the media server, loaded once per tab; null until it has loaded (the render waits). */
export const useImage = (url: string | null): HTMLImageElement | null => {
	const [img, setImg] = useState<HTMLImageElement | null>(() => (url ? cache.get(url) ?? null : null));
	const [handle] = useState(() => (url && !cache.has(url) ? delayRender(`loading ${url}`) : null));
	useEffect(() => {
		if (!url || cache.has(url)) {
			return;
		}
		const im = new Image();
		im.crossOrigin = 'anonymous';
		im.onload = () => {
			cache.set(url, im);
			setImg(im);
			if (handle !== null) {
				continueRender(handle);
			}
		};
		im.onerror = () => cancelRender(new Error(`couldn't load ${url}: is the media server running (npm run media)?`));
		im.src = url;
	}, [url, handle]);
	return img;
};
