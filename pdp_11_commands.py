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
    - params: параметры команды (ss, dd и т.д.)

Режимы адресации:
    Поддерживаются следующие режимы адресации:
    - 0: регистровый (R)
    - 1: косвенный (R)
    - 2: автоинкрементный (R)+
"""

from pdp_11_mem import w_read, w_write, reg, b_write
import sys


commands = [
    {'mask': 0o177777, 'opcode': 0o000000, 'name': 'halt', 'handler': lambda _args: do_halt(_args), 'params': ()},
    {'mask': 0o170000, 'opcode': 0o010000, 'name': 'mov', 'handler': lambda _args: do_mov(_args), 'params': ('ss', 'dd')},
    {'mask': 0o170000, 'opcode': 0o060000, 'name': 'add', 'handler': lambda _args: do_add(_args), 'params': ('ss', 'dd')},
    {'mask': 0o177777, 'opcode': 0o177777, 'name': 'unknown', 'handler': lambda _args: do_unknown(_args), 'params': ()}
]

class ModeNotIplementedError(Exception):
    """Исключение, вызываемое при использовании неподдерживаемого режима адресации."""
    pass


class ModeRegistrArg:
    """Класс для представления аргумента команды с учетом режима адресации."""

    def __init__(self, address: int, value: int, is_register: bool = False):
        self.address = address
        self.value = value
        self.is_register = is_register

    def write(self, value: int, is_word: bool = True):
        """Записывает значение по адресу с учетом типа (регистр/память) и размера (слово/байт)."""
        if self.is_register:
            reg[self.address] = value & 0xFFFF
        else:
            if is_word:
                w_write(self.address, value)
            else:
                b_write(self.address, value)


class ArgsProcessor:
    """Класс для обработки аргументов команд и режимов адресации."""
    def __init__(self):
        self.ss = None
        self.dd = None
        self.nn = None
        self.xx = None
        self.r = None

    def clear(self):
        self.ss = None
        self.dd = None
        self.nn = None
        self.xx = None
        self.r = None

    @staticmethod
    def get_mr(w) -> ModeRegistrArg:
        """
        Разбирает режим адресации и возвращает объект ModeRegistrArg.

        Args:
            w (int): Слово, содержащее номер регистра (младшие 3 бита)
                    и режим адресации (биты 3-5)

        Returns:
            ModeRegistrArg: объект, содержащий адрес и значение

        Raises:
            ModeNotIplementedError: если указан неподдерживаемый режим адресации
        """
        r = w & 7
        mode = (w >> 3) & 7
        addr, value = 0, 0

        if mode == 0:  # Регистровый
            addr = r
            value = reg[r]
            print(f'r{r}', end=' ')

        elif mode == 1:  # Косвенный
            addr = reg[r]
            value = w_read(addr)
            print(f'(r{r})', end=' ')

        elif mode == 2:  # Автоинкрементный
            addr = reg[r]
            value = w_read(addr)
            reg[r] += 2

            if r == 7:
                print(f'#{value:06o}', end=' ')
            else:
                print(f'(r{r})+', end=' ')

        else:
            raise ModeNotIplementedError(f"Unsupported mode {mode}")

        return ModeRegistrArg(addr, value, mode == 0)

    def process(self, params: tuple, word: int):
        """
        Обрабатывает слово команды, извлекая аргументы в глобальный словарь args.

        Args:
            params (tuple): кортеж с типами параметров ('ss', 'dd' и т.д.)
            word (int): слово команды
        """
        self.clear()
        for param in params:
            if param == 'ss':
                self.ss = ArgsProcessor.get_mr(word >> 6)
            elif param == 'dd':
                self.dd = ArgsProcessor.get_mr(word & 0o77)
            else:
                raise ValueError(f'Unknown argument type {param}')

        return self.ss, self.dd


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

def reg_dump(reg):
    print(f"r0={reg[0]:06o} r2={reg[2]:06o} r4={reg[4]:06o} sp={reg[6]:06o}")
    print(f"r1={reg[1]:06o} r3={reg[3]:06o} r5={reg[5]:06o} pc={reg[7]:06o}")