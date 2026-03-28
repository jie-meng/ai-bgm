# OpenCode Plugin Issues and Fixes

## Problem Description

The AI BGM plugin for OpenCode would stop playing music after some time during a session. Restarting OpenCode would temporarily fix the issue, but the problem would recur.

## Root Cause Analysis

After investigation, the issue is primarily caused by **bugs in OpenCode's plugin system**, not our plugin code.

### 1. Fire-and-Forget Event Handlers

**Issue**: [#16879](https://github.com/anomalyco/opencode/issues/16879)

OpenCode's plugin event handlers are called without awaiting their promises. In `plugin/index.ts` line 138:

```typescript
hook["event"]?.({ event: input as any })  // Not awaited
```

This means async operations like `await $\`bgm play work 0\`` may not complete before the next event is processed.

**Status**: Closed (fixed)

### 2. session.created Event Not Firing

**Issue**: [#14808](https://github.com/anomalyco/opencode/issues/14808)

The `session.created` event sometimes doesn't fire, causing `currentSessionID` to remain `null`. This breaks the session ID check in subsequent `message.updated` events:

```javascript
props?.info?.sessionID === currentSessionID  // Always false when currentSessionID is null
```

**Status**: Open

### 3. Race Condition on Session Idle

**Issue**: [#15267](https://github.com/anomalyco/opencode/issues/15267)

A race condition exists between `session.idle` event handling and session teardown, which can cause events to be processed incorrectly.

**Status**: Open

### 4. Plugin System Robustness

**Issue**: [#18279](https://github.com/anomalyco/opencode/issues/18279)

Multiple robustness gaps in the plugin system, including:
- Plugin config hook errors crash entire bootstrap
- Insufficient error isolation between hooks
- Async errors in `prompt_async` silently dropped

**Status**: Closed

## Our Fix

Modified `opencode.py` to make the plugin more resilient to OpenCode's known issues:

### Changes Made

1. **Removed session ID check**: Since `session.created` may not fire, we no longer check `currentSessionID` in `message.updated` handler.

2. **Fire-and-forget command execution**: Added a helper function that catches and ignores errors:

```javascript
const runBgm = (cmd) => {
  $`bgm ${cmd}`.quiet().nothrow().catch(() => {});
};
```

3. **Simplified state management**: Removed redundant session ID checks in `session.idle` and `session.deleted` handlers.

### Before

```javascript
case "message.updated":
  if (
    !isWorking &&
    props?.info?.role === "user" &&
    props?.info?.sessionID === currentSessionID &&  // May fail if session.created didn't fire
    Date.now() - lastIdleTime > DEBOUNCE_MS
  ) {
    isWorking = true;
    await $`bgm play work 0`.quiet().nothrow();  // May not complete
  }
  break;
```

### After

```javascript
case "message.updated":
  if (
    !isWorking &&
    props?.info?.role === "user" &&
    Date.now() - lastIdleTime > DEBOUNCE_MS
  ) {
    isWorking = true;
    runBgm("play work 0");  // Fire-and-forget with error handling
  }
  break;
```

## Testing

After applying the fix:

1. Run `bgm setup` to regenerate the plugin
2. Restart OpenCode
3. The BGM should now play reliably across multiple prompts

## Related OpenCode Issues

| Issue | Title | Status |
|-------|-------|--------|
| [#16879](https://github.com/anomalyco/opencode/issues/16879) | await plugin event handlers on session.idle | Closed |
| [#14808](https://github.com/anomalyco/opencode/issues/14808) | Plugin event listener for "session.created" not firing | Open |
| [#15267](https://github.com/anomalyco/opencode/issues/15267) | opencode run teardown race after session.idle | Open |
| [#18279](https://github.com/anomalyco/opencode/issues/18279) | Plugin system robustness gaps | Closed |
