## 2024-05-23 - [Global Re-render Timer]
**Learning:** A `setInterval` updating an unused state variable (`currentTime`) in the root `App` component caused the entire application tree to re-render every second (1Hz). This is a silent performance killer that consumes CPU and battery even when the app appears idle.
**Action:** Always verify if state variables driven by timers or frequent events are actually used in the render output. If not, remove them or move the logic outside the React render cycle.
