"""Unit tests for content writer tools.

All tests mock the filesystem so no real files are written.
No real LLM calls are made in these tests.
"""

import json

import pytest

from agents.content_writer.tools import execute_tool, get_brand_guidelines, get_audience_persona, save_draft


class TestGetBrandGuidelines:
    def test_returns_json_string(self):
        result = get_brand_guidelines("blog")
        parsed = json.loads(result)
        assert parsed["channel"] == "blog"
        assert "guidelines" in parsed

    def test_includes_channel_note(self):
        result = get_brand_guidelines("linkedin")
        parsed = json.loads(result)
        assert "linkedin" in parsed["note"].lower()

    @pytest.mark.parametrize("channel", ["blog", "linkedin", "twitter", "email", "ad"])
    def test_all_channels_return_data(self, channel):
        result = get_brand_guidelines(channel)
        assert json.loads(result)["channel"] == channel


class TestGetAudiencePersona:
    def test_returns_json_string(self):
        result = get_audience_persona("Marketing Manager")
        parsed = json.loads(result)
        assert parsed["persona_name"] == "Marketing Manager"
        assert "personas_doc" in parsed

    def test_personas_doc_is_non_empty(self):
        result = get_audience_persona("CMO")
        parsed = json.loads(result)
        assert len(parsed["personas_doc"]) > 100


class TestSaveDraft:
    def test_dry_run_does_not_write_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = save_draft("test.md", "# Hello", dry_run=True)
        parsed = json.loads(result)
        assert parsed["dry_run"] is True
        # File should NOT exist
        assert not (tmp_path / "outputs" / "drafts" / "test.md").exists()

    def test_saves_file_when_not_dry_run(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = save_draft("post.md", "# Content", dry_run=False)
        parsed = json.loads(result)
        assert "saved_to" in parsed
        assert (tmp_path / "outputs" / "drafts" / "post.md").exists()

    def test_prevents_path_traversal(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = save_draft("../../evil.md", "malicious", dry_run=False)
        parsed = json.loads(result)
        # Should save to outputs/drafts/evil.md, not ../../evil.md
        assert "evil.md" in parsed["saved_to"]
        assert ".." not in parsed["saved_to"]


class TestExecuteTool:
    def test_dispatches_get_brand_guidelines(self):
        result = execute_tool("get_brand_guidelines", {"channel": "blog"})
        assert json.loads(result)["channel"] == "blog"

    def test_dispatches_get_audience_persona(self):
        result = execute_tool("get_audience_persona", {"persona_name": "CMO"})
        assert json.loads(result)["persona_name"] == "CMO"

    def test_raises_on_unknown_tool(self):
        with pytest.raises(ValueError, match="Unknown tool"):
            execute_tool("does_not_exist", {})
