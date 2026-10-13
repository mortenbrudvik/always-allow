// Remotion's settings for the Always Allow compositor. The render scripts in scripts/ pass what varies
// (the composition, frames, scale, output); everything that must never vary is here.
import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(92);
Config.setChromiumOpenGlRenderer('angle'); // WebGL (the print pass) on the RTX 3090, not a blank canvas
Config.setOverwriteOutput(true);
Config.setCodec('h264');
Config.setPixelFormat('yuv420p');
Config.setCrf(18);
Config.setDelayRenderTimeoutInMilliseconds(120000);
