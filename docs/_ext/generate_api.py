"""Build the API index from installed exports and require public docstrings."""

from importlib import import_module
import inspect
from pathlib import Path


def check_docstrings(qualified, value):
    """Check Python methods and properties without constructing SDK objects."""
    missing = []
    if not value.__doc__:
        missing.append(qualified)
    for base in value.__mro__:
        if not base.__module__.startswith("pymarvin."):
            continue
        for name, member in vars(base).items():
            if name.startswith("_"):
                continue
            if isinstance(member, (classmethod, staticmethod)):
                member = member.__func__
            if (
                inspect.isfunction(member) or isinstance(member, property)
            ) and not inspect.getdoc(member):
                missing.append(f"{qualified}.{name}")
    return missing


def generate_api(docs: Path):
    """Inspect pymarvin.__all__ and write the public API page only when changed."""
    package = import_module("pymarvin")
    lines = ["Public package API", "==================", ""]
    missing = []
    for name in package.__all__:
        value = getattr(package, name)
        if not inspect.isclass(value):
            continue
        qualified = f"pymarvin.{name}"
        missing.extend(check_docstrings(qualified, value))
        lines.extend(
            [
                qualified,
                "-" * len(qualified),
                "",
                f".. autoclass:: {qualified}",
                "   :members:",
            ]
        )
        if name == "PointSet":
            lines.append(
                "   :special-members: __len__, __getitem__, __enter__, __exit__"
            )
        lines.append("")
    if missing:
        raise RuntimeError(
            "Public API docstrings are missing:\n" + "\n".join(sorted(set(missing)))
        )
    output = docs / "api/_generated"
    output.mkdir(parents=True, exist_ok=True)
    path = output / "pymarvin.rst"
    text = "\n".join(lines)
    if not path.exists() or path.read_text(encoding="utf-8") != text:
        path.write_text(text, encoding="utf-8")
