## 2024-05-22 - Unused State Updates Cause Global Re-renders
**Learning:** Found a `setInterval` updating an unused `currentTime` state every second in the root `App` component. This caused the entire application tree to re-render every 1000ms, consuming resources for absolutely no visible change.
**Action:** Always check if state variables updated by timers (or any frequent source) are actually used in the render output. If not, remove them. If used, isolate them in a leaf component.
