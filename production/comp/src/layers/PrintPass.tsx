// The print pass (STYLE_BIBLE.md, textures): one WebGL2 shader over the footage layer only, never the
// type or UI. It moves a plate over its depth map (2.5D), lays the screen-space CMYK halftone over the
// frame at 7.5 px cells at 1080p (the 5 px screen of the Seedance inputs, scaled with them), at 15, 75, 0
// and 45 degrees, blended at 35 % (the blend step 0 tested with no moire), then a gentle grade that keeps
// blacks at #0b0c0e and whites at #f4f4f1, and fresh grain from the frame number. It never desaturates.
import React, {useCallback, useLayoutEffect, useRef} from 'react';

export interface Cam {
	zoom: number; // 1 = the plate fills the frame
	x: number; // parallax shift for the nearest depth, in frame widths
	y: number;
	depth: number; // how strongly depth separates the layers (0 = flat)
	rot: number; // radians, for overheads
	fx: number; // the zoom's focus, 0-1
	fy: number;
}

export const STILL: Cam = {zoom: 1, x: 0, y: 0, depth: 0, rot: 0, fx: 0.5, fy: 0.5};

export interface PrintOptions {
	blend: number;
	cell: number; // px at 1080p
	grain: number;
	contrast: number;
	halftone: boolean;
}

export const PRINT: PrintOptions = {blend: 0.35, cell: 7.5, grain: 0.04, contrast: 0.15, halftone: true};

const VERT = `#version 300 es
in vec2 a_pos;
out vec2 v_uv;
void main() {
  v_uv = vec2(a_pos.x * 0.5 + 0.5, 0.5 - a_pos.y * 0.5); // image space: y down
  gl_Position = vec4(a_pos, 0.0, 1.0);
}`;

const FRAG = `#version 300 es
precision highp float;
in vec2 v_uv;
out vec4 outColor;
uniform sampler2D u_src;
uniform sampler2D u_depth;
uniform bool u_hasDepth;
uniform bool u_halftone;
uniform vec2 u_res;      // canvas pixels
uniform vec2 u_srcRes;   // source pixels
uniform vec4 u_fit;      // cover fit: scale.xy, offset.xy (uv)
uniform vec4 u_cam;      // x, y, zoom, depth strength
uniform vec3 u_cam2;     // rotation, focus x, focus y
uniform float u_cell;    // halftone cell in canvas pixels
uniform float u_blend;
uniform float u_grain;
uniform float u_seed;
uniform float u_contrast;

vec2 camUV(vec2 uv) {
  vec2 f = u_cam2.yz;
  vec2 p = uv - f;
  float c = cos(u_cam2.x), s = sin(u_cam2.x);
  p = vec2(p.x * c - p.y * s, p.x * s + p.y * c) / u_cam.z + f;
  if (u_hasDepth) {
    float d = texture(u_depth, p * u_fit.xy + u_fit.zw).r;
    p -= u_cam.xy * (d - 0.5) * u_cam.w;
  }
  return p * u_fit.xy + u_fit.zw;
}

vec3 src(vec2 uv, float lod) {
  return textureLod(u_src, camUV(uv), lod).rgb;
}

float coverage(float v) {
  float touch = 0.78539816;
  return v <= touch ? sqrt(v / 3.14159265) : 0.5 + (v - touch) / (1.0 - touch) * (0.70710678 - 0.5);
}

float ink(vec2 px, float angle, int ch, float lod) {
  float c = cos(angle), s = sin(angle);
  vec2 r = vec2(px.x * c + px.y * s, -px.x * s + px.y * c) / u_cell;
  vec2 cc = floor(r) + 0.5;
  vec2 d = r - cc;
  vec2 cpx = vec2(cc.x * c - cc.y * s, cc.x * s + cc.y * c) * u_cell;
  vec3 rgb = src(cpx / u_res, lod);
  float k = 1.0 - max(max(rgb.r, rgb.g), rgb.b);
  vec3 cmy = (1.0 - rgb - k) / max(1.0 - k, 1e-4);
  float v = ch == 0 ? cmy.x : ch == 1 ? cmy.y : ch == 2 ? cmy.z : k;
  float rad = coverage(clamp(v, 0.0, 1.0));
  float aa = 0.8 / u_cell;
  return 1.0 - smoothstep(rad - aa, rad + aa, length(d));
}

float hash(vec2 p) {
  p = fract(p * vec2(123.34, 456.21));
  p += dot(p, p + 45.32);
  return fract(p.x * p.y);
}

void main() {
  vec2 px = v_uv * u_res;
  vec3 base = src(v_uv, 0.0);
  vec3 col = base;
  if (u_halftone) {
    float srcPerPx = (u_srcRes.y * u_fit.y) / (u_res.y * u_cam.z);
    float lod = max(0.0, log2(max(u_cell * srcPerPx * 0.5, 1.0)));
    float c = ink(px, radians(15.0), 0, lod);
    float m = ink(px, radians(75.0), 1, lod);
    float y = ink(px, radians(0.0), 2, lod);
    float k = ink(px, radians(45.0), 3, lod);
    vec3 paper = vec3(0.965, 0.955, 0.93);
    vec3 printed = paper * vec3(1.0 - c, 1.0 - m, 1.0 - y) * (1.0 - k);
    col = mix(base, printed, u_blend);
  }
  col = col + u_contrast * (col - 0.5) * (1.0 - abs(2.0 * col - 1.0));
  col = mix(vec3(0.0431, 0.0471, 0.0549), vec3(0.9569, 0.9569, 0.9451), clamp(col, 0.0, 1.0));
  col += (hash(px + vec2(u_seed * 17.0, u_seed * 31.0)) - 0.5) * u_grain;
  outColor = vec4(clamp(col, 0.0, 1.0), 1.0);
}`;

interface GL {
	gl: WebGL2RenderingContext;
	prog: WebGLProgram;
	src: WebGLTexture;
	depth: WebGLTexture;
	u: Record<string, WebGLUniformLocation | null>;
	srcKey: unknown;
	depthKey: unknown;
	srcSize: [number, number];
}

const compile = (gl: WebGL2RenderingContext, type: number, code: string) => {
	const s = gl.createShader(type)!;
	gl.shaderSource(s, code);
	gl.compileShader(s);
	if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
		throw new Error(`print pass shader: ${gl.getShaderInfoLog(s)}`);
	}
	return s;
};

const setup = (canvas: HTMLCanvasElement): GL => {
	const gl = canvas.getContext('webgl2', {preserveDrawingBuffer: true, antialias: false, premultipliedAlpha: false});
	if (!gl) {
		throw new Error('the print pass needs WebGL2 (render with --gl=angle)');
	}
	const prog = gl.createProgram()!;
	gl.attachShader(prog, compile(gl, gl.VERTEX_SHADER, VERT));
	gl.attachShader(prog, compile(gl, gl.FRAGMENT_SHADER, FRAG));
	gl.linkProgram(prog);
	if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) {
		throw new Error(`print pass link: ${gl.getProgramInfoLog(prog)}`);
	}
	gl.useProgram(prog);
	const buf = gl.createBuffer();
	gl.bindBuffer(gl.ARRAY_BUFFER, buf);
	gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
	const loc = gl.getAttribLocation(prog, 'a_pos');
	gl.enableVertexAttribArray(loc);
	gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
	const tex = () => {
		const t = gl.createTexture()!;
		gl.bindTexture(gl.TEXTURE_2D, t);
		gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
		gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
		gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
		gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
		return t;
	};
	const names = ['u_src', 'u_depth', 'u_hasDepth', 'u_halftone', 'u_res', 'u_srcRes', 'u_fit', 'u_cam', 'u_cam2', 'u_cell', 'u_blend', 'u_grain', 'u_seed', 'u_contrast'];
	const u = Object.fromEntries(names.map((n) => [n, gl.getUniformLocation(prog, n)]));
	return {gl, prog, src: tex(), depth: tex(), u, srcKey: null, depthKey: null, srcSize: [1, 1]};
};

const sizeOf = (s: CanvasImageSource): [number, number] => {
	if (s instanceof HTMLVideoElement) {
		return [s.videoWidth, s.videoHeight];
	}
	if (s instanceof HTMLImageElement) {
		return [s.naturalWidth, s.naturalHeight];
	}
	const any = s as {width: number; height: number};
	return [any.width, any.height];
};

const upload = (g: GL, tex: WebGLTexture, img: CanvasImageSource) => {
	const {gl} = g;
	gl.bindTexture(gl.TEXTURE_2D, tex);
	gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, false);
	gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img as TexImageSource);
	gl.generateMipmap(gl.TEXTURE_2D);
};

export interface PrintPassHandle {
	draw: (src: CanvasImageSource) => void;
}

/** A canvas that prints `src` (a plate or a video frame) with the camera and the print options. */
export const PrintPass: React.FC<{
	src: CanvasImageSource | null;
	srcKey: unknown; // changes when the source image changes
	depth?: HTMLImageElement | null;
	cam: Cam;
	seed: number;
	width: number;
	height: number;
	options?: Partial<PrintOptions>;
	pxScale?: number; // the render's scale (a 640x360 proxy is 1/3)
	handle?: React.MutableRefObject<PrintPassHandle | null>;
}> = ({src, srcKey, depth, cam, seed, width, height, options, pxScale = 1, handle}) => {
	const canvas = useRef<HTMLCanvasElement>(null);
	const gl = useRef<GL | null>(null);
	const o = {...PRINT, ...options};
	const bw = Math.round(width * pxScale);
	const bh = Math.round(height * pxScale);

	const draw = useCallback(
		(img: CanvasImageSource | null, key: unknown) => {
			if (!canvas.current || !img) {
				return;
			}
			if (!gl.current) {
				gl.current = setup(canvas.current);
			}
			const g = gl.current;
			const x = g.gl;
			if (g.srcKey !== key) {
				upload(g, g.src, img);
				g.srcKey = key;
				g.srcSize = sizeOf(img);
			}
			if (depth && g.depthKey !== depth.src) {
				upload(g, g.depth, depth);
				g.depthKey = depth.src;
			}
			x.viewport(0, 0, bw, bh);
			x.activeTexture(x.TEXTURE0);
			x.bindTexture(x.TEXTURE_2D, g.src);
			x.uniform1i(g.u.u_src, 0);
			x.activeTexture(x.TEXTURE1);
			x.bindTexture(x.TEXTURE_2D, g.depth);
			x.uniform1i(g.u.u_depth, 1);
			x.uniform1i(g.u.u_hasDepth, depth ? 1 : 0);
			x.uniform1i(g.u.u_halftone, o.halftone ? 1 : 0);
			x.uniform2f(g.u.u_res, bw, bh);
			const [sw, sh] = g.srcSize;
			x.uniform2f(g.u.u_srcRes, sw, sh);
			// cover the frame: crop the source's longer side
			const fa = width / height;
			const sa = sw / Math.max(1, sh);
			const sx = sa > fa ? fa / sa : 1;
			const sy = sa > fa ? 1 : sa / fa;
			x.uniform4f(g.u.u_fit, sx, sy, (1 - sx) / 2, (1 - sy) / 2);
			x.uniform4f(g.u.u_cam, cam.x, cam.y, cam.zoom, cam.depth);
			x.uniform3f(g.u.u_cam2, cam.rot, cam.fx, cam.fy);
			x.uniform1f(g.u.u_cell, o.cell * (bh / 1080));
			x.uniform1f(g.u.u_blend, o.blend);
			x.uniform1f(g.u.u_grain, o.grain);
			x.uniform1f(g.u.u_seed, seed);
			x.uniform1f(g.u.u_contrast, o.contrast);
			x.drawArrays(x.TRIANGLES, 0, 3);
		},
		[bw, bh, cam.x, cam.y, cam.zoom, cam.depth, cam.rot, cam.fx, cam.fy, depth, o.blend, o.cell, o.contrast, o.grain, o.halftone, seed, width, height],
	);

	// a video frame (or a composite canvas) can arrive as the same element with new pixels: every handle
	// draw uploads; and every render redraws the last one, so a held frame still takes the camera and grain
	const last = useRef<CanvasImageSource | null>(null);
	if (handle) {
		handle.current = {
			draw: (img) => {
				last.current = img;
				draw(img, {});
			},
		};
	}

	useLayoutEffect(() => {
		if (src) {
			draw(src, srcKey);
		} else if (last.current) {
			draw(last.current, gl.current?.srcKey);
		}
	}, [draw, src, srcKey]);

	return <canvas ref={canvas} width={bw} height={bh} style={{position: 'absolute', inset: 0, width, height}} />;
};
