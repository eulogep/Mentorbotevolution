## 2026-01-20 - [Removing 1Hz Global Re-renders]
**Learning:** The application had a `setInterval` in `App.jsx` updating a `currentTime` state every second, but this state was never used in the render output. This caused the entire React component tree to re-render every second, consuming significant CPU and battery.
**Action:** Always check if state variables updated by timers (or any frequent source) are actually used in the render. If not, remove them.
