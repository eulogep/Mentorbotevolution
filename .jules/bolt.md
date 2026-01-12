## 2024-10-24 - Root Component Re-render Loop
**Learning:** The root `App` component contained a `setInterval` that updated an unused state variable (`currentTime`) every second. This caused the entire application (and all children) to re-render at 1Hz, consuming resources for no visible benefit.
**Action:** When auditing React apps, check root-level `useEffect` hooks for timers that update state. Verify if that state is actually used in the JSX. If not, remove it.
