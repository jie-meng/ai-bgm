#!/usr/bin/env python3
"""Tests for the ZCode AI tool integration."""

import json
from pathlib import Path
from unittest import mock

import pytest

from mythril_agent_bgm.commands.integrations.registry import IntegrationRegistry
from mythril_agent_bgm.commands.integrations.zcode import ZcodeIntegration


@pytest.fixture
def fake_home(tmp_path: Path) -> Path:
    """A fake home directory with a .zcode/cli config root."""
    zcode_dir = tmp_path / ".zcode" / "cli"
    zcode_dir.mkdir(parents=True)
    return tmp_path


@pytest.fixture
def patched_home(fake_home: Path):
    return mock.patch(
        "mythril_agent_bgm.commands.integrations.zcode.Path.home",
        return_value=fake_home,
    )


def _settings_path(fake_home: Path) -> Path:
    return fake_home / ".zcode" / "cli" / "config.json"


def _write_config(fake_home: Path, hooks: dict) -> None:
    _settings_path(fake_home).write_text(json.dumps({"hooks": hooks}), encoding="utf-8")


def _read_config(fake_home: Path) -> dict:
    return json.loads(_settings_path(fake_home).read_text(encoding="utf-8"))


def test_tool_info():
    assert ZcodeIntegration().get_tool_info() == ("zcode", "ZCode")


def test_settings_path_under_zcode_cli(patched_home):
    with patched_home:
        assert ZcodeIntegration().get_settings_path() == (
            Path.home() / ".zcode" / "cli" / "config.json"
        )


def test_config_dir_is_zcode_cli(patched_home):
    with patched_home:
        assert ZcodeIntegration().get_config_dir() == Path.home() / ".zcode" / "cli"


def test_setup_adds_all_hooks(fake_home: Path, patched_home):
    with patched_home:
        ok, _ = ZcodeIntegration().perform_setup()
        assert ok
        hooks = _read_config(fake_home)["hooks"]

    # Configuration-file hooks are skipped by ZCode unless enabled.
    assert hooks["enabled"] is True
    events = hooks["events"]
    assert events["UserPromptSubmit"][0]["hooks"][0]["command"] == "bgm play work 0"
    assert events["Stop"][0]["hooks"][0]["command"] == "bgm play done"
    assert events["PermissionRequest"][0]["hooks"][0]["command"] == "bgm play notification 0"
    assert events["PostToolUse"][0]["hooks"][0]["command"] == "bgm play work 0"


def test_setup_keeps_other_settings_and_events(fake_home: Path, patched_home):
    _write_config(
        fake_home,
        {
            "enabled": True,
            "events": {"SessionStart": [{"hooks": [{"type": "command", "command": "x"}]}]},
        },
    )
    path = _settings_path(fake_home)
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["mcp"] = {"servers": {}}
    path.write_text(json.dumps(raw), encoding="utf-8")

    with patched_home:
        ok, _ = ZcodeIntegration().perform_setup()
        assert ok
        settings = _read_config(fake_home)

    assert settings["mcp"] == {"servers": {}}
    events = settings["hooks"]["events"]
    assert events["SessionStart"] == [{"hooks": [{"type": "command", "command": "x"}]}]
    assert "PostToolUse" in events


def test_setup_enables_hooks_when_disabled(fake_home: Path, patched_home):
    _write_config(fake_home, {"enabled": False, "events": {}})

    with patched_home:
        ok, _ = ZcodeIntegration().perform_setup()
        assert ok
        assert _read_config(fake_home)["hooks"]["enabled"] is True


def test_setup_cleanup_roundtrip(fake_home: Path, patched_home):
    with patched_home:
        integration = ZcodeIntegration()
        assert not integration.is_configured()

        ok, _ = integration.perform_setup()
        assert ok
        assert integration.is_configured()
        assert integration.is_up_to_date()

        ok, _ = integration.perform_cleanup()
        assert ok
        assert not integration.is_configured()
        assert "hooks" not in _read_config(fake_home)


def test_cleanup_removes_only_bgm_hooks(fake_home: Path, patched_home):
    _write_config(
        fake_home,
        {
            "enabled": True,
            "events": {"SessionStart": [{"hooks": [{"type": "command", "command": "x"}]}]},
        },
    )

    with patched_home:
        ok, _ = ZcodeIntegration().perform_setup()
        assert ok
        ok, _ = ZcodeIntegration().perform_cleanup()
        assert ok
        settings = _read_config(fake_home)

    assert "PostToolUse" not in settings["hooks"]["events"]
    assert settings["hooks"]["events"]["SessionStart"] == [
        {"hooks": [{"type": "command", "command": "x"}]}
    ]


def test_up_to_date_detects_missing_resume_hook(fake_home: Path, patched_home):
    # Simulate a pre-resume config: the three lifecycle hooks but no PostToolUse.
    _write_config(
        fake_home,
        {
            "enabled": True,
            "events": {
                "UserPromptSubmit": [
                    {"hooks": [{"type": "command", "command": "bgm play work 0"}]}
                ],
                "Stop": [{"hooks": [{"type": "command", "command": "bgm play done"}]}],
                "PermissionRequest": [
                    {"hooks": [{"type": "command", "command": "bgm play notification 0"}]}
                ],
            },
        },
    )
    with patched_home:
        integration = ZcodeIntegration()
        assert integration.is_configured()
        assert not integration.is_up_to_date()


def test_registry_returns_zcode():
    integration = IntegrationRegistry.get_integration_by_id("zcode")
    assert isinstance(integration, ZcodeIntegration)
