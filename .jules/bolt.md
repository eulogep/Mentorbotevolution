## 2026-01-22 - Unused State with Interval Causes Global Re-renders
**Learning:** The `App` component contained a `currentTime` state updated every second via `setInterval`, yet this state was completely unused in the render output. This caused the entire application tree to re-render at 1Hz unnecessarily.
**Action:** Before adding time-based state, verify it is actually displayed. Audit existing components for unused state variables driven by effects/timers.
