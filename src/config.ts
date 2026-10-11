// 4:3 frame at NTSC film rate (24000/1001 ≈ 23.976 fps).
export const WIDTH = 1440;
export const HEIGHT = 1080;
export const FPS = 24000 / 1001;

export const secondsToFrames = (seconds: number) => Math.round(seconds * FPS);
