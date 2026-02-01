## 2024-05-22 - Root Component Re-render Storm
**Learning:** Discovered a `setInterval` updating unused state in the root `App` component, causing the entire React tree to re-render every second.
**Action:** Always audit `useEffect` hooks with `setInterval` in root components. Check if the state they update is actually used in the render. If not, delete it. If it is, isolate it in a leaf component.
