"""
Модуль эмулятора команд процессора PDP-11.

Этот модуль реализует базовые команды процессора PDP-11, включая:
- MOV (перемещение данных)
- ADD (сложение)
- HALT (остановка процессора)
- SOB (вычитание с ветвлением)
- CLR (очистка)

Основные компоненты:
- commands: Список поддерживаемых команд с их масками, кодами операций и обработчиками.
- Функции-обработчики команд (do_mov, do_add, do_halt, do_sob, do_clr, do_unknown).
- Вспомогательные функции (reg_dump для вывода состояния регистров).

Формат команд:
Каждая команда представлена словарем с полями:
- mask: Битовая маска для выделения кода операции.
- opcode: Код операции.
- name: Мнемоника команды.
- handler: Функция-обработчик команды.
- params: Параметры команды (ss, dd, r, nn и т.д.).

"""

from pdp_11_mem import w_read, w_write, reg, b_write
from pdp_11_args import ArgsProcessor
import sys



commands = [
    {'mask': 0o177777, 'opcode': 0o000000, 'name': 'halt', 'handler': lambda _args: do_halt(_args), 'params': ()},
    {'mask': 0o170000, 'opcode': 0o010000, 'name': 'mov', 'handler': lambda _args: do_mov(_args), 'params': ('ss', 'dd')},
    {'mask': 0o170000, 'opcode': 0o060000, 'name': 'add', 'handler': lambda _args: do_add(_args), 'params': ('ss', 'dd')},
    {'mask': 0o177000, 'opcode': 0o077000, 'name': 'sob', 'handler': lambda _args: do_sob(_args), 'params': ('r', 'nn')},
    {'mask': 0o177000, 'opcode': 0o005000, 'name': 'clr', 'handler': lambda _args: do_clr(_args), 'params': ('dd',)},
    {'mask': 0o177777, 'opcode': 0o177777, 'name': 'unknown', 'handler': lambda _args: do_unknown(_args), 'params': ()}
]


def do_mov(_args):
    """
    Обработчик команды MOV (перемещение данных).

    Переносит значение из источника в приемник.

    Args:
        w (int): Слово команды
    """
    _args.dd.write(_args.ss.value)


def do_add(_args):
    """
    Обработчик команды ADD (сложение).

    Складывает значения источника и приемника, результат сохраняет в приемник.

    Args:
        w (int): Слово команды
    """
    result = _args.ss.value + _args.dd.value
    _args.dd.write(result)


def do_halt(_args):
    """
    Обработчик команды HALT (остановка процессора).

    Выводит содержимое регистров и завершает работу программы.
    """
    print("\n---------------- halted ---------------")
    reg_dump(reg)
    sys.exit(0)


def do_unknown(_args):
    """
    Обработчик неизвестной команды.

    Выводит сообщение о неизвестной команде.
    """
    print("\nUNKNOWN COMMAND")


def do_sob(_args):
    """
        Обработчик команды SOB (Subtract One and Branch).

        Уменьшает значение регистра на 1 и, если результат не равен нулю,
        выполняет переход на указанное смещение назад.

        Формат команды: SOB r, NN
        PC = PC - 2 * NN
    """
    reg[_args.r] = (reg[_args.r] - 1) & 0xFFFF
    if reg[_args.r] != 0:
        reg[7] = (reg[7] - 2 * _args.nn) & 0xFFFF

def do_clr(_args):
    """
        Обработчик команды CLR (очистка).
        Обнуляет указанный регистр или ячейку памяти.
        """
    _args.dd.write(0)

def reg_dump(reg):
    print(f"r0={reg[0]:06o} r2={reg[2]:06o} r4={reg[4]:06o} sp={reg[6]:06o}")
    print(f"r1={reg[1]:06o} r3={reg[3]:06o} r5={reg[5]:06o} pc={reg[7]:06o}")