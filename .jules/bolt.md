## 2024-05-23 - Unused State Timer Bottleneck
**Learning:** Found a pattern where `currentTime` state was updated every second via `setInterval` but never used in the render. This caused the entire application (root `App` component) to re-render every second, consuming battery and CPU unnecessarily.
**Action:** Always check `useEffect` timers to ensure the state they update is actually used in the render output. If not, remove the state and timer.
