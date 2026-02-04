## 2024-05-23 - Global State Timer Anti-Pattern
**Learning:** Avoid defining state variables updated by timers (e.g., `setInterval`) in the root component if they are not used in the render output. This triggers unnecessary re-renders of the entire application tree every second, significantly impacting performance and battery life.
**Action:** Always verify if a state variable is actually used in the JSX before adding a timer to update it. If a timer is needed for a specific child component, move the state and timer to that component.
