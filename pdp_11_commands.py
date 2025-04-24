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
    Поддерживаются все режимы адресации PDP-11:
    - 0: регистровый (R)
    - 1: косвенный (R)
    - 2: автоинкрементный (R)+
    - 3: автоинкрементный косвенный @(R)+
    - 4: автодекрементный -(R)
    - 5: автодекрементный косвенный @-(R)
    - 6: индексный X(R)
    - 7: индексный косвенный @X(R)
"""

from pdp_11_mem import w_read, w_write, reg, b_write
import sys


commands = [
    {'mask': 0o177777, 'opcode': 0o000000, 'name': 'halt', 'handler': lambda _args: do_halt(_args), 'params': ()},
    {'mask': 0o170000, 'opcode': 0o010000, 'name': 'mov', 'handler': lambda _args: do_mov(_args), 'params': ('ss', 'dd')},
    {'mask': 0o170000, 'opcode': 0o060000, 'name': 'add', 'handler': lambda _args: do_add(_args), 'params': ('ss', 'dd')},
    {'mask': 0o177000, 'opcode': 0o077000, 'name': 'sob', 'handler': lambda _args: do_sob(_args), 'params': ('r', 'nn')},
    {'mask': 0o177000, 'opcode': 0o005000, 'name': 'clr', 'handler': lambda _args: do_clr(_args), 'params': ('dd',)},
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
        is_register = False

        if mode == 0:  # Регистровый
            addr = r
            value = reg[r]
            is_register = True
            print(f'r{r}', end=' ')

        elif mode == 1:  # Косвенный регистровый
            addr = reg[r]
            if addr % 2 != 0:
                raise ValueError(f"Unaligned word address {addr:06o}")
            value = w_read(addr)
            print(f'(r{r})', end=' ')

        elif mode == 2:  # Автоинкрементный
            addr = reg[r]
            if r == 7:  # Непосредственная адресация для PC
                value = w_read(addr)
                print(f'#{value:06o}', end=' ')
            else:
                value = w_read(addr)
                print(f'(r{r})+', end=' ')
            reg[r] += 2

        elif mode == 3:  # Автоинкрементный косвенный
            addr = reg[r]
            ptr = w_read(addr)
            value = w_read(ptr)
            reg[r] += 2
            print(f'@(r{r})+', end=' ')

        elif mode == 4:  # Автодекрементный
            reg[r] -= 2
            addr = reg[r]
            value = w_read(addr)
            print(f'-(r{r})', end=' ')

        elif mode == 5:  # Автодекрементный косвенный
            reg[r] -= 2
            addr = reg[r]
            ptr = w_read(addr)
            value = w_read(ptr)
            print(f'@-(r{r})', end=' ')

        elif mode == 6:  # Индексный
            offset = w_read(reg[7])
            reg[7] += 2
            addr = reg[r] + offset
            value = w_read(addr)
            print(f'{offset}(r{r})', end=' ')

        elif mode == 7:  # Индексный косвенный
            offset = w_read(reg[7])
            reg[7] += 2
            ptr = reg[r] + offset
            addr = w_read(ptr)
            value = w_read(addr)
            print(f'@{offset}(r{r})', end=' ')

        else:
            raise ModeNotIplementedError(f"Unsupported mode {mode}")

        return ModeRegistrArg(addr, value, is_register)

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
            elif param == 'r':
                self.r = (word >> 6) & 0o7
                print(f'r{self.r}', end=' ')
            elif param == 'nn':
                self.nn = word & 0o77
                print(f'{self.nn:o}', end=' ')
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