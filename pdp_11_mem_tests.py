import pytest
from pdp_11_mem import *

# Фикстура для очистки памяти перед каждым тестом
@pytest.fixture(autouse=True)
def clear_memory():
    global mem
    mem = [0] * MEMSIZE
    yield

def test_b_write_and_b_read():
    # Тест записи и чтения одного байта
    b_write(0x10, 0xAB)
    assert b_read(0x10) == 0xAB

    b_write(0x20, 0xFF)
    assert b_read(0x20) == 0xFF

    # Проверка, что запись не затрагивает соседние ячейки
    assert b_read(0x1F) == 0
    assert b_read(0x21) == 0

def test_w_write_and_w_read():
    # Тест записи и чтения слова (2 байта)
    w_write(0x10, 0xABCD)
    assert w_read(0x10) == 0xABCD

    w_write(0x20, 0x1234)
    assert w_read(0x20) == 0x1234

    # Проверка, что запись не затрагивает соседние ячейки
    assert w_read(0x0E) == 0
    assert w_read(0x12) == 0

def test_w_write_odd_address():
    # Тест записи слова по нечетному адресу (должно вызывать ошибку)
    with pytest.raises(ValueError, match="Word address must be even"):
        w_write(0x11, 0xABCD)

def test_w_read_odd_address():
    # Тест чтения слова по нечетному адресу (должно вызывать ошибку)
    with pytest.raises(ValueError, match="Word address must be even"):
        w_read(0x11)

def test_word_boundary():
    # Тест записи и чтения слова на границе памяти
    w_write(MEMSIZE - 2, 0xDEAD)
    assert w_read(MEMSIZE - 2) == 0xDEAD

    # Попытка записи за границей памяти (должно вызывать IndexError)
    with pytest.raises(IndexError):
        w_write(MEMSIZE, 0xBEEF)

    # Попытка чтения за границей памяти (должно вызывать IndexError)
    with pytest.raises(IndexError):
        w_read(MEMSIZE)

def test_write_word_as_two_bytes_and_read():
    # Записываем слово 0xAABB как два отдельных байта
    b_write(0x30, 0xBB)  # Младший байт
    b_write(0x31, 0xAA)  # Старший байт

    # Читаем слово через w_read
    assert w_read(0x30) == 0xAABB

    # Проверяем, что запись не затронула соседние ячейки
    assert b_read(0x2F) == 0
    assert b_read(0x32) == 0