## 2024-05-23 - [Unnecessary Root Re-renders]
**Learning:** React state updates inside `setInterval` trigger re-renders even if the state value is not used in the render output. In the root component (`App`), this causes the entire application to re-render, which is a major performance bottleneck.
**Action:** Always verify if state variables updated by timers or effects are actually used in the render function. If not, remove them.
