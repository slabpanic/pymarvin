"""Check that the bundled official showcases remain distributable Python sources."""

import ast
import importlib
from pathlib import Path

EXAMPLES = Path(__file__).parents[1] / "examples"


def test_official_showcases_compile_and_use_pymarvin_imports():
    showcases = sorted(EXAMPLES.glob("showcase*.py"))
    assert len(showcases) == 54

    for path in showcases:
        source = path.read_text(encoding="utf-8-sig")
        compile(source, str(path), "exec")
        assert "SDK_PYTHON" not in source
        tree = ast.parse(source, filename=str(path))
        sdk_imports = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            and node.module
            and node.module.startswith("pymarvin.")
        ]
        # The collected-data conversion utility is intentionally standalone.
        if path.name != "showcase_process_collect_data_to_pvt_format.py":
            assert sdk_imports, f"{path.name} has no pymarvin SDK import"
        for node in sdk_imports:
            if node.module in {
                "pymarvin.fx_robot",
                "pymarvin.fx_kine",
                "pymarvin.fx_interference",
            }:
                module = importlib.import_module(node.module)
                for symbol in node.names:
                    assert hasattr(
                        module, symbol.name
                    ), f"{path.name} imports missing {node.module}.{symbol.name}"


def test_offline_examples_compile():
    for name in ("offline_kinematics.py", "offline_interference.py"):
        path = EXAMPLES / name
        compile(path.read_text(encoding="utf-8"), str(path), "exec")
