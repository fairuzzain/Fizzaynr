import { Composition } from "remotion";
import { FPS, HEIGHT, WIDTH, secondsToFrames } from "./config";
import { Hook, hookSchemaDefaults, type HookProps } from "./Hook";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Hook"
      component={Hook}
      width={WIDTH}
      height={HEIGHT}
      fps={FPS}
      durationInFrames={secondsToFrames(hookSchemaDefaults.durationInSeconds)}
      defaultProps={hookSchemaDefaults satisfies HookProps}
      calculateMetadata={({ props }) => ({
        durationInFrames: secondsToFrames(props.durationInSeconds),
      })}
    />
  );
};
