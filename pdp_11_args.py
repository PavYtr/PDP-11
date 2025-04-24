"""
Модуль для обработки аргументов команд и режимов адресации PDP-11.

Этот модуль содержит классы и функции для разбора и обработки аргументов команд PDP-11.
Основные компоненты:

Классы:
- ModeRegistrArg: Представляет аргумент команды, включая адрес, значение и флаг регистра.
- ArgsProcessor: Обрабатывает режимы адресации и аргументы команд.

Исключения:
- ModeNotIplementedError: Вызывается при использовании неподдерживаемого режима адресации.

Основные функции:
- get_mr: Разбирает режим адресации и возвращает объект ModeRegistrArg.
- process: Обрабатывает слово команды и извлекает аргументы.

Режимы адресации:
- 0: Регистровый (R)
- 1: Косвенный регистровый (R)
- 2: Автоинкрементный (R)+
- 3: Автоинкрементный косвенный @(R)+
- 4: Автодекрементный -(R)
- 5: Автодекрементный косвенный @-(R)
- 6: Индексный X(R)
- 7: Индексный косвенный @X(R)
"""

from pdp_11_mem import reg, w_write, b_write, w_read

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