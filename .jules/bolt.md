## 2024-05-23 - Unused Interval State Causing Global Re-renders
**Learning:** The `App` component contained an unused `currentTime` state updated by a `setInterval` every second. This caused the entire React component tree to re-render at 1Hz, wasting CPU cycles and battery on idle. This seems to be a leftover from a previous feature or template.
**Action:** When auditing performance, specifically look for `setInterval` in root components and verify that the state they update is actually used in the render output.
