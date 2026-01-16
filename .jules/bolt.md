## 2024-05-22 - Unused State Causes Global Re-renders
**Learning:** React components will re-render if a state variable is updated, even if that state variable is NOT used in the JSX return. In this codebase, `App.jsx` had a `setInterval` updating `currentTime` every second, causing the entire application tree to re-render 60 times a minute unnecessarily.
**Action:** Always check `useEffect` timers and state updates. If a value is not used in the render, remove it or use `useRef` if the value is needed for logic but not display.
