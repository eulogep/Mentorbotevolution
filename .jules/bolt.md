## 2024-05-23 - Unused State Timer
**Learning:** Discovered a `useState` updated by a 1-second `setInterval` that was completely unused in the render output. This caused the entire application to re-render every second unnecessarily.
**Action:** When auditing performance, look for "zombie" `useEffect` timers that update state which is no longer referenced in the JSX.
