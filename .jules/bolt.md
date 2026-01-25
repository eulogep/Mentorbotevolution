## 2024-05-22 - [Unused State Intervals]
**Learning:** Found a component updating unused state (`currentTime`) via `setInterval` every second. This triggered 1Hz re-renders of the entire component tree for no reason.
**Action:** Always check if state updated by timers is actually used in the render. If not, remove it.
