
## Unnecessary Re-render in App.jsx

### Problem
The `App` component in `src/App.jsx` has a `currentTime` state that is updated every second using `setInterval`.

```javascript
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);
```

However, `currentTime` is **never used** in the render output of `App.jsx` or passed to any children.

### Impact
- The root `App` component re-renders every 1000ms.
- This causes all child components (the entire application) to re-render (unless they are memoized, which most are not).
- This wastes CPU cycles and battery on the user's device.

### Verification
I have grepped the file `src/App.jsx` and `currentTime` only appears in the definition and the effect.

```bash
grep "currentTime" src/App.jsx
# Output: const [currentTime, setCurrentTime] = useState(new Date());
```

It is not used in the return statement.
