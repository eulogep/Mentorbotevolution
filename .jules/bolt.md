## 2026-01-26 - Unused Timer causing 1Hz Re-renders
**Learning:** The `App` component had a `setInterval` updating a `currentTime` state every second, but this state was never used in the render output. This caused the entire application to re-render at 1Hz, wasting CPU and battery.
**Action:** Always check if state variables updated by timers or subscriptions are actually used in the render. If not, remove them.
