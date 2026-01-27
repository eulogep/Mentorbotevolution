## 2026-01-27 - [Unused State Causes 1Hz Re-renders]
**Learning:** Found an unused state variable `currentTime` updated via `setInterval` every second in the root `App` component. This caused the entire React tree to re-render every second for no reason, as the state was never used in the render output.
**Action:** Always check if state variables updated by timers (or any side effect) are actually used in the render. If not, remove them to prevent wasted cycles.
