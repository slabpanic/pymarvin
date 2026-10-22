"""Check data parsing and controller file conversions without network access."""

import pytest
from pymarvin import fx_robot as fx


@pytest.mark.parametrize(
    "content,expected",
    [
        ("", 0),
        ("\n \n", 0),
        ("0,0\n", 0),
        ("0,0\n0,0\n", 0),
        ("0,0\n1,2\n", ("line2", [1.0, 2.0])),
        ("1,2\n0,0\n", ("line1", [1.0, 2.0])),
        ("1,2\n3,4\n", [[1.0, 2.0], [3.0, 4.0]]),
        ("1\n", -1),
        ("a,2\n", -1),
        ("1,2\n3,4\n5,6\n", -1),
    ],
)
def test_csv_conventions(tmp_path, content, expected):
    path = tmp_path / "tool.csv"
    path.write_text(content)
    assert fx.read_csv_file_to_float_strict(str(path), 2) == expected


def test_missing_files_and_read_errors(tmp_path, monkeypatch):
    path = tmp_path / "missing"
    assert fx.read_csv_file_to_float_strict(str(path)) == -1
    assert fx.read_csv_file_to_float_strict(str(tmp_path)) == -1
    assert not fx.update_text_file_simple("A", [0] * 16, str(path))
    assert not fx.update_text_file_simple("X", [0] * 16, str(path))
    assert not fx.update_text_file_simple("A", [], str(path))
    path.write_text("before A\nbefore B\n")
    assert fx.update_text_file_simple("A", list(range(16)), str(path))
    assert path.read_text().splitlines()[0] == ",".join(map(str, range(16)))
    assert fx.update_text_file_simple("B", [3] * 16, str(path))
    assert path.read_text().splitlines()[1] == ",".join(["3"] * 16)


@pytest.mark.parametrize(
    "value,kind,encoded",
    [
        (b"\x00\xff", "bytes", b"\x00\xff"),
        ("0x ABC", "hex string", b"\x0a\xbc"),
        ("aa bb", "hex string", b"\xaa\xbb"),
        ("你好", "regular string", "你好".encode()),
        ('b"\\xff"', "bytes representation string", b"\xff"),
        ('b"\\xzz"', "regular string", b'b"\\xzz"'),
        ("", "regular string", b""),
    ],
)
def test_channel_data_types(value, kind, encoded):
    result = fx.identify_and_calculate_length(value)
    assert result == dict(
        input=value, type=kind, length_bytes=len(encoded), bytes_representation=encoded
    )


def test_channel_invalid_inputs():
    with pytest.raises(TypeError):
        fx.identify_and_calculate_length(3)
    with pytest.raises(ValueError):
        fx.identify_and_calculate_length("\ud800")


@pytest.mark.parametrize(
    "number,options,result",
    [
        (255, {}, "FF"),
        (255, {"prefix": True, "upper": False}, "0xff"),
        (1.5, {"float_precision": 2, "upper": False}, "1.80p+0"),
        (
            1.5,
            {"float_precision": None, "prefix": True, "upper": False},
            float(1.5).hex(),
        ),
        (-1, {"prefix": True}, "0X-0X1"),
        (float("inf"), {}, "INF"),
    ],
)
def test_hex_format(number, options, result):
    assert fx.decimal_to_hex(number, **options) == result


def test_hex_type_and_faults():
    with pytest.raises(TypeError):
        fx.decimal_to_hex("255")
    assert fx.get_fault_descriptions([]) == "None fault codes list"
    assert fx.get_fault_descriptions([0, "0x0000", ""]) == "None"
    code = next(iter(fx.fault_code_dict_EN))
    assert fx.fault_code_dict_EN[code] in fx.get_fault_descriptions([code], lang="EN")
    assert fx.fault_code_dict_CN[code] in fx.get_fault_descriptions([code])
    message = fx.get_fault_descriptions(["missing", "other"])
    assert message.startswith("Fault information for each joint:")
    assert "joint 2: other - unknown error(other)" in message
