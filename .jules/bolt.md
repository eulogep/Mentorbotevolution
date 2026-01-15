## 2024-05-22 - Unused Timer State Causing Global Re-renders
**Learning:** Found `currentTime` state in `App.jsx` updated every second via `setInterval` but unused in render. This caused the entire application tree to re-render at 1Hz.
**Action:** When auditing React apps, check root components for `setInterval` loops updating state that isn't actually passed down or rendered.
