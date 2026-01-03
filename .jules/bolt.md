## 2024-01-04 - Unused Global State Re-renders
**Learning:** Found an unused `currentTime` state in the root `App` component that updated every second. This caused the entire application to re-render every second, consuming resources unnecessarily. Always check if state updated in `setInterval` is actually used in the render.
**Action:** When seeing `setInterval` in `useEffect`, check if the state it updates is used in JSX.
