import {
  AbsoluteFill,
  Audio,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export type HookProps = {
  /** File in /public, e.g. "photo.jpg". Null shows a placeholder. */
  photo: string | null;
  /** File in /public, e.g. "voiceover.mp3". Null renders silent. */
  voiceover: string | null;
  headline: string;
  durationInSeconds: number;
};

export const hookSchemaDefaults: HookProps = {
  photo: null,
  voiceover: null,
  headline: "Your hook goes here",
  durationInSeconds: 6,
};

export const Hook: React.FC<HookProps> = ({ photo, voiceover, headline }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  // Slow Ken Burns push-in across the whole clip.
  const scale = interpolate(frame, [0, durationInFrames], [1.05, 1.2]);
  const fadeIn = interpolate(frame, [0, fps * 0.5], [0, 1], {
    extrapolateRight: "clamp",
  });
  const textIn = spring({ frame: frame - Math.round(fps * 0.4), fps, config: { damping: 200 } });

  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <AbsoluteFill style={{ opacity: fadeIn, transform: `scale(${scale})` }}>
        {photo ? (
          <Img src={staticFile(photo)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
        ) : (
          <AbsoluteFill
            style={{ background: "linear-gradient(135deg, #1e3a5f 0%, #7b2d5b 100%)" }}
          />
        )}
      </AbsoluteFill>
      <AbsoluteFill style={{ justifyContent: "flex-end", padding: 96 }}>
        <h1
          style={{
            margin: 0,
            color: "white",
            fontFamily: "Helvetica, Arial, sans-serif",
            fontSize: 96,
            lineHeight: 1.05,
            textShadow: "0 4px 24px rgba(0,0,0,0.6)",
            opacity: textIn,
            transform: `translateY(${(1 - textIn) * 60}px)`,
          }}
        >
          {headline}
        </h1>
      </AbsoluteFill>
      {voiceover ? <Audio src={staticFile(voiceover)} /> : null}
    </AbsoluteFill>
  );
};
