## 2024-10-18 - Unintended Lockfile Changes
**Learning:** Running `npm install` can modify `package-lock.json` and `yarn.lock` even if no new dependencies are added, often due to environment differences or synchronization issues. These changes are flagged as critical failures during review if not reverted.
**Action:** Always check `git status` after running `npm install` and revert changes to lockfiles (`git restore package-lock.json yarn.lock`) if no dependencies were explicitly added or updated in `package.json`.
