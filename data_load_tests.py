import pytest
from data_load import load_data
from pdp_11_mem import w_read

def test_load_data_single_block(tmp_path):
    # Создаем временный файл с тестовыми данными
    test_data = """1000 3
    AA
    BB
    CC
    """
    test_file = tmp_path / "test_file.txt"
    test_file.write_text(test_data)

    load_data(str(test_file))

    assert w_read(0x1000) == 0xBBAA
    assert w_read(0x1002) == 0x00CC

def test_load_data_multiple_blocks(tmp_path):
    # Создаем временный файл с несколькими блоками данных
    test_data = """1000 3
    AA
    BB
    CC
    2000 2
    DD
    EE
    """
    test_file = tmp_path / "test_file.txt"
    test_file.write_text(test_data)

    load_data(str(test_file))

    assert w_read(0x1000) == 0xBBAA
    assert w_read(0x1002) == 0x00CC
    assert w_read(0x2000) == 0xEEDD