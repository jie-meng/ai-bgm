#!/usr/bin/env python3
"""Tests for the Cline CLI (runtime hooks) AI tool integration."""

from pathlib import Path
from unittest import mock

import pytest

from mythril_agent_bgm.commands.integrations.cline import (
    ClineIntegration,
    _HOOK_EVENTS,
)


@pytest.fixture

def fake_home(tmp_path: Path) -> Path:
    """A fake home directory with a .cline config root."""
    cfg = tmp_path / ".cline"
    cfg.mkdir()
    return tmp_path


def _make_bgm(home: Path) -> Path:
    """Create a fake bgm executable inside the fake home."""
    fake_bgm = home / "fake-bgm"
    fake_bgm.write_text("#!/bin/sh\necho ok\n", encoding="utf-8")
    fake_bgm.chmod(0o755)
    return fake_bgm


@pytest.fixture
def patched_home(fake_home: Path):
    return mock.patch(
        "mythril_agent_bgm.commands.integrations.cline.Path.home",
        return_value=fake_home,
    )


def test_tool_info():
    assert ClineIntegration().get_tool_info() == ("cline", "Cline CLI")


def test_hooks_dir_is_under_dot_cline_hooks(patched_home):
    with patched_home:
        assert ClineIntegration().get_settings_path() == (
            Path.home() / ".cline" / "hooks"
        )


def test_generates_all_hook_events():
    integration = ClineIntegration()
    assert set(_HOOK_EVENTS) == {
        "TaskStart",
        "TaskComplete",
        "SessionShutdown",
        "PostToolUse",
    }
    for event in _HOOK_EVENTS:
        script = integration._hook_script(event, "/usr/local/bin/bgm")
        assert script.startswith("#!/usr/bin/env bash")
        assert script.endswith("echo '{}'\n")


def test_task_start_plays_work():
    script = ClineIntegration._hook_script("TaskStart", "/x/bgm")
    assert '"/x/bgm" play work 0' in script


def test_task_complete_plays_done():
    script = ClineIntegration._hook_script("TaskComplete", "/x/bgm")
    assert '"/x/bgm" play done' in script


def test_session_shutdown_stops():
    script = ClineIntegration._hook_script("SessionShutdown", "/x/bgm")
    assert '"/x/bgm" stop' in script


def test_post_tool_use_plays_notification_on_ask_question():
    script = ClineIntegration._hook_script("PostToolUse", "/x/bgm")
    assert 'tool_result.name' in script
    assert '"ask_question"' in script
    assert '"/x/bgm" play notification 0' in script


def test_unknown_event_raises():
    with pytest.raises(ValueError):
        ClineIntegration._hook_script("NotARealEvent", "/x/bgm")


def test_setup_and_cleanup_roundtrip(fake_home: Path, patched_home):
    fake_bgm = _make_bgm(fake_home)
    with patched_home:
        with mock.patch("shutil.which", return_value=str(fake_bgm)):
            integration = ClineIntegration()
            assert not integration.is_configured()

            ok, _ = integration.perform_setup()
            assert ok
            assert integration.is_configured()
            assert integration.is_up_to_date()
            hooks_dir = integration.get_settings_path()
            assert all((hooks_dir / f"{e}.sh").exists() for e in _HOOK_EVENTS)
            # scripts are executable
            assert (hooks_dir / "TaskStart.sh").stat().st_mode & 0o111

            ok, _ = integration.perform_cleanup()
            assert ok
            assert not integration.is_configured()
            assert not (hooks_dir / "TaskStart.sh").exists()


def test_setup_requires_config_dir(tmp_path: Path):
    # No .cline config dir -> setup reports failure without creating files.
    with mock.patch(
        "mythril_agent_bgm.commands.integrations.cline.Path.home", return_value=tmp_path
    ):
        ok, message = ClineIntegration().perform_setup()
        assert not ok
        assert "Config directory not found" in message


def test_cleanup_with_no_hooks_is_noop(fake_home: Path, patched_home):
    with patched_home:
        ok, message = ClineIntegration().perform_cleanup()
        assert ok
        assert "nothing to clean up" in message
