## 2024-05-23 - React Interval State Updates
**Learning:** Updating state in `setInterval` (e.g., `currentTime`) at the root component level triggers full-app re-renders on every tick. In this case, `App.jsx` was re-rendering every second even though the time wasn't being used in the render output, causing significant CPU overhead.
**Action:** Always verify if state updated by intervals is actually used in the render. If not, remove it. If it is used, localize the state to the smallest possible child component to prevent cascading re-renders.
