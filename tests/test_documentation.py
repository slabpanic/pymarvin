"""Verify that untranslated or stale API documentation blocks publication."""

from pathlib import Path
import runpy

import pytest

pytest.importorskip("babel")
from babel.messages.catalog import Catalog
from babel.messages.pofile import read_po, write_po


@pytest.fixture
def catalogs(tmp_path, monkeypatch):
    namespace = runpy.run_path(
        str(Path(__file__).parents[1] / "docs/_ext/check_translations.py")
    )
    check = namespace["check_translations"]
    locale = tmp_path / "locale"
    locale.mkdir()
    monkeypatch.setitem(check.__globals__, "LOCALE", locale)
    templates = tmp_path / "templates"
    templates.mkdir()
    template = Catalog(project="pymarvin")
    template.add("Source text")
    with (templates / "api.pot").open("wb") as stream:
        write_po(stream, template)
    return check, templates, locale


def write_catalog(path, mode):
    cat = Catalog(locale="zh_CN", project="pymarvin")
    cat.fuzzy = False
    if mode != "missing":
        cat.add(
            "Source text",
            "来源文本" if mode != "untranslated" else "",
            flags=["fuzzy"] if mode == "fuzzy" else [],
        )
    if mode == "stale":
        cat.add("Old text", "旧文本")
    with path.open("wb") as stream:
        write_po(stream, cat)


@pytest.mark.parametrize("mode", ["missing", "untranslated", "fuzzy", "stale"])
def test_invalid_catalogs_rejected(catalogs, mode):
    check, templates, locale = catalogs
    write_catalog(locale / "api.po", mode)
    with pytest.raises(ValueError, match="Translation errors"):
        check(templates)


def test_valid_translation_and_missing_catalog(catalogs):
    check, templates, locale = catalogs
    with pytest.raises(ValueError, match="Missing catalog"):
        check(templates)
    write_catalog(locale / "api.po", "valid")
    check(templates)
    write_catalog(locale / "unused.po", "valid")
    with pytest.raises(ValueError, match="Stale catalog"):
        check(templates)


def test_catalog_update_requires_translation(catalogs):
    check, templates, locale = catalogs
    check(templates, update=True)
    with (locale / "api.po").open("rb") as stream:
        catalog = read_po(stream, locale="zh_CN")
    assert catalog.get("Source text").string == ""
    with pytest.raises(ValueError, match="untranslated"):
        check(templates)
    with pytest.raises(ValueError, match="No gettext templates"):
        check(locale)


def test_api_index_uses_installed_exports(tmp_path):
    import inspect
    import pymarvin

    namespace = runpy.run_path(
        str(Path(__file__).parents[1] / "docs/_ext/generate_api.py")
    )
    namespace["generate_api"](tmp_path)
    page = tmp_path / "api/_generated/pymarvin.rst"
    text = page.read_text()
    for name in pymarvin.__all__:
        if inspect.isclass(getattr(pymarvin, name)):
            assert f".. autoclass:: pymarvin.{name}\n" in text
    timestamp = page.stat().st_mtime_ns
    namespace["generate_api"](tmp_path)
    assert page.stat().st_mtime_ns == timestamp


def test_api_index_rejects_undocumented_methods(tmp_path, monkeypatch):
    from types import SimpleNamespace

    class Undocumented:
        """An otherwise documented public class."""

        __module__ = "pymarvin.example"

        def method(self):
            pass

    namespace = runpy.run_path(
        str(Path(__file__).parents[1] / "docs/_ext/generate_api.py")
    )
    generate = namespace["generate_api"]
    package = SimpleNamespace(__all__=["Undocumented"], Undocumented=Undocumented)
    monkeypatch.setitem(generate.__globals__, "import_module", lambda name: package)
    with pytest.raises(RuntimeError, match=r"pymarvin.Undocumented.method"):
        generate(tmp_path)
    assert not (tmp_path / "api/_generated/pymarvin.rst").exists()
