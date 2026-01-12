## 2024-01-12 - [Unused State Updates]
**Learning:** Found a state variable `currentTime` in `App.jsx` that was updated every second via `setInterval` but never used in the UI. This caused the entire root `App` component and its children to re-render every second, silently consuming resources.
**Action:** Always check `setInterval` and `useEffect` hooks for side effects that trigger state updates. Ensure the state is actually used. Remove them if not.
