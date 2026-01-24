## 2024-05-23 - [Prevent Global Re-renders]
**Learning:** Found an unused `setInterval` updating state in the root `App` component, causing the entire application tree to re-render every second (1Hz) unnecessarily.
**Action:** Audit `useEffect` hooks containing `setInterval` or `setTimeout`. Ensure the state they update is actually used in the render output. Remove if unused to prevent massive performance waste.
