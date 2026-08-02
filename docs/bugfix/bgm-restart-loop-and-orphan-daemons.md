# BGM Restart Loop and Overlapping Player Daemons

Two related bugs caused background music to behave badly during long AI
work sessions. Both were triggered by the OpenCode plugin firing many
`bgm play` requests while a task was running.

## Bug 1: Work BGM Restarting Every Few Seconds (fixed in 6039a2c)

### Problem Description

During a long task, the work BGM restarted every few seconds and shuffled
to a different track each time, making the music unusable.

### Root Cause Analysis

OpenCode 1.18 emits repeated `role=user` `message.updated` events while a
task runs (synthetic messages from task tool completions, summary fills).
The old plugin treated each one as a new user turn:

```javascript
case "message.updated":
  if (
    props?.info?.role === "user" &&
    Date.now() - lastIdleTime > DEBOUNCE_MS  // lastIdleTime not reset during a run
  ) {
    isWorking = true;
    runBgm("play", "work", "0");  // fired on every synthetic user message
  }
  break;
```

The 2-second debounce only guarded against the previous "done" turn; it
did nothing between repeated user messages within one run.

### Fix

- Restore the `!isWorking` guard in `message.updated` so work BGM starts
  exactly once per run.
- Track `mainSessionID` via `session.updated` as a fallback for dropped
  `session.created` events.
- Handle the new `session.status` event as a reliable work/done anchor
  for the main session only (subagent sessions filtered out).

## Bug 2: Overlapping Player Daemons (fixed in 1b59294)

### Problem Description

Multiple music tracks played simultaneously (audio chaos) and never
stopped. `ps` showed several `bgm play --daemon` processes alive at once,
each looping a different track.

### Root Cause Analysis

`start_background_player` spawned the new daemon and released the file
lock immediately, but the daemon saves its PID **asynchronously** —
Python startup plus imports take ~300ms before `save_pid()` runs:

```
call 1: [lock] kill old PID → spawn daemon A → [unlock]
daemon A: ...300ms startup... → save_pid(A)
call 2: [lock] read PID file (stale/empty!) → kill nothing → spawn daemon B → [unlock]
daemon B: ...→ save_pid(B)   ← overwrites, A is now an orphan
```

Any `play`/`stop` call arriving inside that window read a stale or
missing PID file, killed nothing, and spawned yet another daemon. Orphaned
daemons piled up, each looping its own track at full volume. The old
plugin's restart loop (Bug 1) made the window get hit constantly.

### Fix

In `start_background_player` (src/mythril_agent_bgm/commands/play.py):

- `kill_existing_process()` now returns the PID it killed
  (`Optional[int]`) instead of a bool.
- New `wait_for_daemon_pid()` polls the PID file (up to 5s) **while still
  holding the file lock**, until it sees a live PID different from the
  killed one. The lock is only released once the new daemon owns the PID
  file, so the next play/stop call always targets the correct process.

### Verification

Stress test with 8 concurrent `bgm play work 0` calls: exactly 1 daemon
survives (previously 4-5 piled up). Mixed 10-call test (work/notification/
done) also leaves exactly 1 daemon, and the PID file matches the live
process.

## Operational Notes

- OpenCode loads plugins at startup and does **not** hot-reload them: an
  opencode process started before the plugin update keeps running the old
  plugin in memory. Restart opencode to pick up a new plugin.
- `bgm stop` kills all daemons via pgrep on Unix (not just the PID file
  owner), which also cleans up any pre-existing orphans.
- The `bgm` CLI is installed non-editable in site-packages; a `pip install .`
  is required after changing player code.
