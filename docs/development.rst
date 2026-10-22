Development and publishing
==========================

Verification
------------

.. code-block:: bash

   uv sync --locked --no-editable --group test --group docs --group release
   uv run --no-sync black --check src/pymarvin tests docs examples .github/scripts
   uv run --no-sync pytest -q
   uv run --no-sync coverage run -m pytest -q
   uv run --no-sync coverage xml
   uv run --no-sync coverage report
   uv build
   uv run --no-sync python .github/scripts/check_sdist.py dist/pymarvin-*.tar.gz

Maintain the nanobind C++ bindings in ``src/bindings/`` and the compatible Python facades
in ``src/pymarvin/`` directly. Update their English docstrings in place. Maintain the required Apache-2.0 SDK
sources in ``src/sdk/control/``, ``src/sdk/kinematics/`` and ``src/sdk/interference/``. Tests check the SDK
headers against the installed extensions; reference copies and obsolete SDKs are
not part of the project.

The bundled SDK snapshot is pinned to commit
``bc4f61104a66e82b4c750f3a0bc7a95c9ef44139`` from the official
`TJ_FX_ROBOT_CONTRL_SDK repository <https://github.com/cynthia-you/TJ_FX_ROBOT_CONTRL_SDK>`_.

English and Chinese documentation
---------------------------------

``docs/_ext/generate_api.py`` inspects the installed package exports, validates public
docstrings and generates the API index when Sphinx loads ``docs/conf.py``. Generated
API pages are excluded from version control and source distributions. CI invokes
Sphinx and the translation checker directly.

English reStructuredText and API docstrings are the source language. Chinese
translations live in ``docs/locale/zh_CN/LC_MESSAGES/*.po``. The catalog checker rejects
missing, untranslated, fuzzy, stale and invalid entries.

.. code-block:: bash

   uv run --no-sync sphinx-build -n -W -b gettext -D language=en docs docs/_build/gettext
   uv run --no-sync python docs/_ext/check_translations.py docs/_build/gettext
   uv run --no-sync sphinx-build -n -W -b html -D language=en docs docs/_build/en
   uv run --no-sync sphinx-build -n -W -b html -D language=zh_CN docs docs/_build/zh_CN

After editing source text, run the catalog checker with ``--update``, translate the new
entries, and rerun the check without that option. Each documentation page links to the
same page in the other language.

Read the Docs setup
-------------------

Import ``https://github.com/slabpanic/pymarvin`` into Read the Docs as project
``pymarvin``, select English as its language, use ``main`` as the default branch,
and select ``.readthedocs.yaml`` as the configuration file. Enable the repository's
Read the Docs Git integration to build documentation when changes are pushed.

For Simplified Chinese, import the same repository as a second project, for example
``pymarvin-zh-cn``, select Simplified Chinese as its language, and add it under the
parent project's Translations settings. Both projects use the same configuration
and gettext catalogs. Read the Docs supplies the selected language and version;
Sphinx uses them for translated pages, canonical URLs and language-switch links.

The public URLs are ``https://pymarvin.readthedocs.io/en/latest/`` and
``https://pymarvin.readthedocs.io/zh-cn/latest/``. CI independently checks both
languages and uploads available HTML previews even if a documentation build fails.
Read the Docs performs the hosted build using the repository configuration.

PyPI Trusted Publishing setup
-----------------------------

Create a PyPI Trusted Publisher (or pending publisher for a new project) with owner
``slabpanic``, repository ``pymarvin``, workflow ``release.yml`` and environment
``pypi``. Create the matching GitHub environment. No long-lived PyPI API token is used.

Set the normalized project version, update ``uv.lock``, and push a matching ``vX.Y.Z``
tag when ready to publish. ``release.yml`` calls the reusable ``ci.yml`` workflow,
which validates the tag, builds and verifies one source archive, runs tests and
coverage, validates bilingual documentation, and builds, repairs and tests all 15
CPython 3.10–3.14 wheels for Linux x86_64/aarch64 and Windows x64.

CI collects the source archive and wheels, verifies the complete set with
``check_wheels.py`` and Twine, and uploads the ``pymarvin-dist`` artifact. After CI
succeeds, the release job downloads that artifact and runs
``uv publish --trusted-publishing always dist/*`` without rebuilding packages.
macOS is excluded. CI validates documentation while Read the Docs handles hosting.

Do not recreate an existing PyPI version. Correct a failed release in a new version when
an archive has already been accepted by the registry. Configuring this workflow does not
publish a release until a matching tag is pushed.

Codecov and native coverage
---------------------------

Enable ``slabpanic/pymarvin`` in Codecov and allow GitHub OIDC uploads. The coverage job
requests ``id-token: write`` and sends separate ``python`` and ``native`` flags. Fork
PRs still generate coverage artifacts but do not upload with repository identity.

.. code-block:: bash

   uv sync --locked --no-editable --group test --group native-coverage \
     --no-build-isolation-package pymarvin \
     -Ccmake.define.PYMARVIN_ENABLE_COVERAGE=ON -Cbuild-dir=build/coverage
   uv run --no-sync coverage run -m pytest -q
   uv run --no-sync coverage xml
   uv run --no-sync gcovr --root . --filter "src/bindings/" --merge-lines \
     --xml-pretty --output coverage-native.xml --print-summary build/coverage

If a workstation has unrelated pytest plugins on PYTHONPATH, set
``PYTEST_DISABLE_PLUGIN_AUTOLOAD=1``. CI sets this explicitly. Coverage thresholds are
enforced in CI: 95 percent combined Python statement/branch coverage and 75 percent native line
coverage. Codecov compares each flag against its base commit with a 1 percent tolerance;
its treatment of partially covered branches differs from the line metric.
Uncovered controller-dependent paths remain in the reports.

Test execution, Python reporting and native reporting use separate CI steps. Both
reporting steps run with ``if: always()`` so failures retain diagnostic reports;
the original test failure still fails CI. Codecov uploads run only after successful
checks and use ``plugins: noop`` to upload the explicitly generated XML files.

Hosting references
------------------

`PyPI Trusted Publishers
<https://docs.pypi.org/trusted-publishers/adding-a-publisher/>`_

`Read the Docs project setup
<https://docs.readthedocs.com/platform/stable/intro/add-project.html>`_

`Read the Docs translations
<https://docs.readthedocs.com/platform/stable/localization.html>`_

`Codecov Action <https://github.com/codecov/codecov-action>`_

