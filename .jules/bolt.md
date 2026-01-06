## 2024-05-23 - [Unexpected Re-render Cause]
**Learning:** React components using `setInterval` in `useEffect` to update state (e.g., a clock) will cause the *entire* component tree to re-render on every tick, even if the state isn't visually rendered or used in props.
**Action:** Always extract "live" features like clocks or real-time counters into their own small, isolated components to prevent polluting the main render cycle. If the state is unused, remove it entirely.
