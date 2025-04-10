"""
Модуль эмулятора процессора PDP-11.

Этот модуль реализует базовые команды процессора PDP-11:
- mov (перемещение данных)
- add (сложение)
- halt (остановка процессора)

Основные компоненты:
- commands: список поддерживаемых команд с их обработчиками
- ArgsProcessor: класс для обработки режимов адресации и аргументов команд
- Функции-обработчики команд (do_mov, do_add, do_halt, do_unknown)

Классы исключений:
- ModeNotIplementedError: вызывается при попытке использовать неподдерживаемый режим адресации

Формат команд:
    Каждая команда представлена словарем с полями:
    - mask: битовая маска для выделения кода операции
    - opcode: код операции
    - name: мнемоника команды
    - handler: функция-обработчик команды

Режимы адресации:
    Поддерживаются следующие режимы адресации:
    - 0: регистровый (R)
    - 1: косвенный (R)
    - 2: автоинкрементный (R)+
"""

from pdp_11_mem import w_read, w_write, reg
import sys

commands = [
    {'mask': 0o177777, 'opcode': 0o000000, 'name': 'halt', 'handler': lambda w: do_halt(w)},
    {'mask': 0o170000, 'opcode': 0o010000, 'name': 'mov', 'handler': lambda w: do_mov(w)},
    {'mask': 0o170000, 'opcode': 0o060000, 'name': 'add', 'handler': lambda w: do_add(w)},
    {'mask': 0o177777, 'opcode': 0o177777, 'name': 'unknown', 'handler': lambda w: do_unknown(w)}
]


class ModeNotIplementedError(Exception):
    """Исключение, вызываемое при использовании неподдерживаемого режима адресации."""
    pass


class ArgsProcessor:
    """Класс для обработки аргументов команд и режимов адресации."""

    @staticmethod
    def get_mr(w):
        """
        Разбирает режим адресации и возвращает адрес и значение.

        Args:
            w (int): Слово, содержащее номер регистра (младшие 3 бита) 
                    и режим адресации (биты 3-5)

        Returns:
            tuple: (addr, value), где:
                addr - адрес в памяти или номер регистра
                value - значение из регистра или памяти

        Raises:
            ModeNotIplementedError: если указан неподдерживаемый режим адресации
        """
        r = w & 7
        mode = (w >> 3) & 7
        addr, value = 0, 0

        if mode == 0:  # Регистровый
            addr = r
            value = reg[r]
        elif mode == 1:  # Косвенный
            addr = reg[r]
            value = w_read(addr)
        elif mode == 2:  # Автоинкрементный
            addr = reg[r]
            value = w_read(addr)
            reg[r] += 2
        else:
            raise ModeNotIplementedError(f"Unsupported mode {mode}")

        return addr, value

    @staticmethod
    def process(w):
        """
        Обрабатывает слово команды, извлекая source и destination.

        Args:
            w (int): Слово команды

        Returns:
            tuple: (src, dst, src_addr, src_val, dst_addr, dst_val), где:
                src - поле source из команды
                dst - поле destination из команды
                src_addr - адрес источника
                src_val - значение источника
                dst_addr - адрес приемника
                dst_val - значение приемника
        """
        src = (w >> 6) & 0o77
        dst = w & 0o77

        src_addr, src_val = ArgsProcessor.get_mr(src)
        dst_addr, dst_val = ArgsProcessor.get_mr(dst)
        return src, dst, src_addr, src_val, dst_addr, dst_val


def do_mov(w):
    """
    Обработчик команды MOV (перемещение данных).

    Переносит значение из источника в приемник.

    Args:
        w (int): Слово команды
    """
    src, dst, src_addr, src_val, dst_addr, dst_val = ArgsProcessor.process(w)

    # Для регистрового режима
    if (dst >> 3) & 7 == 0:
        reg[dst & 7] = src_val
    else:
        w_write(dst_addr, src_val)
    print(f"    #{src_val}, R{dst & 7}")


def do_add(w):
    """
    Обработчик команды ADD (сложение).

    Складывает значения источника и приемника, результат сохраняет в приемник.

    Args:
        w (int): Слово команды
    """
    src, dst, src_addr, src_val, dst_addr, dst_val = ArgsProcessor.process(w)
    result = (src_val + dst_val)

    # Для регистрового режима
    if (dst >> 3) & 7 == 0:
        reg[dst & 7] = result
    else:
        w_write(dst_addr, result)
    print(f"    R{src}, R{dst}")


def do_halt(w):
    """
    Обработчик команды HALT (остановка процессора).

    Выводит содержимое регистров и завершает работу программы.
    """
    print("\n")
    for i in range(len(reg)):
        print(f"R{i} : ", reg[i])
    sys.exit(0)


def do_unknown(w):
    """
    Обработчик неизвестной команды.

    Выводит сообщение о неизвестной команде.
    """
    print("\nUNKNOWN")