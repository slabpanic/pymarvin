"""Build English documentation and its Chinese gettext translation."""

from importlib.metadata import version as package_version
import os
from pathlib import Path
import sys

DOCS = Path(__file__).resolve().parent
sys.path.insert(0, str(DOCS / "_ext"))

from generate_api import generate_api

project = "pymarvin"
author = "pymarvin contributors"
release = package_version("pymarvin")
version = release
language = os.environ.get("READTHEDOCS_LANGUAGE", "en").replace("-", "_")
if language.lower() == "zh_cn":
    language = "zh_CN"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.autosummary"]
autosummary_generate = True
autodoc_typehints = "none"
autodoc_member_order = "bysource"
locale_dirs = ["locale/"]
gettext_compact = True
gettext_uuid = False
html_theme = "furo"
templates_path = ["_templates"]
exclude_patterns = ["_build"]
html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "sidebar/navigation.html",
        "language-switcher.html",
        "sidebar/scroll-end.html",
        "sidebar/variant-selector.html",
    ]
}


# Inspect the installed binding before Sphinx discovers its source documents.
generate_api(DOCS)


def configure_language(app, config):
    """Use the language-specific Read the Docs canonical URL."""
    locale = "zh-cn" if config.language == "zh_CN" else "en"
    config.html_baseurl = os.environ.get(
        "READTHEDOCS_CANONICAL_URL",
        f"https://pymarvin.readthedocs.io/{locale}/latest/",
    )


def language_links(app, pagename, templatename, context, doctree):
    """Link matching pages in preview builds and Read the Docs translations."""
    page = app.builder.get_target_uri(pagename)
    links = []
    for code, label in [("en", "English"), ("zh_CN", "简体中文")]:
        if os.environ.get("READTHEDOCS") == "True":
            locale = "zh-cn" if code == "zh_CN" else "en"
            root = app.config.html_baseurl.rstrip("/").rsplit("/", 2)[0]
            revision = os.environ.get("READTHEDOCS_VERSION", "latest")
            url = f"{root}/{locale}/{revision}/{page}"
        else:
            url = context["pathto"](f"../{code}/{page}", True)
        links.append((code, label, url, app.config.language == code))
    context["documentation_languages"] = links
    context["language_heading"] = (
        "语言" if app.config.language == "zh_CN" else "Languages"
    )


def setup(app):
    app.connect("config-inited", configure_language)
    app.connect("html-page-context", language_links)
