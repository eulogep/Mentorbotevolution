# Bolt's Journal

## 2024-05-22 - [Optimization] 1Hz Global Re-render
**Learning:** Found an unused `currentTime` state updated via `setInterval` every second in the root `App` component. This caused the entire application tree to re-render at 1Hz, consuming CPU and battery even when idle.
**Action:** When seeing `setInterval` in a root component, always verify if the state it updates is actually driving the UI. If not, remove it immediately.
