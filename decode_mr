import pyparsing as pp


# .venv\Scripts\activate
def to3bit(x):
    res = str(bin(int(x))[2:])
    while len(res) < 3:
        res = '0' + res
    return res


def to_four_digit_hex_number(x):
    res = str(hex(int(x)))[2:]
    while len(res) < 4:
        res = '0' + res
    return res


# Пока без label (лейблы могут быть, но они никак не обрабатываются и не записываются в машинный код)

command_description = {
    # Однобайтовые команды
    'halt': {
        'opcode': '0' * 16,  # Код операции MOV (в hex)
        'args': []
    },
    # Двухадресные команды
    'mov': {
        'opcode': '0001',
        'args': ['mr', 'mr']  # ss = mr, dd = mr - mode, register
    },
    'add': {
        'opcode': '0110',
        'args': ['mr', 'mr']
    },
}


def get_command_by_name(name):
    return command_description[name]


def to16bit(x):
    res = bin(x)[2:]
    while len(res) < 16:
        res = '0' + res
    return res


def from8to10(s):
    x = 0
    s = s[::-1]
    for i in range(len(s)):
        x += int(s[i]) * 8 ** i
    return x


def from8to16bit(s):
    return to16bit(from8to10(s))


mode_reg = (
        pp.Regex(r'^R[1-7]$').setParseAction(lambda t: f'000{to3bit(t[0][1])}')('code') |  # R3, mode = '000'
        pp.Regex(r'^\(R[1-7]\)$').setParseAction(lambda t: f'001{to3bit(t[0][2])}')('code') |  # (R3), mode = '001'
        pp.Regex(r'^\(R[1-7]\)\+$').setParseAction(lambda t: f'010{to3bit(t[0][2])}')('code') |  # (R3)+, mode = '010'
        pp.Regex(r'^@\(R[1-7]\)\+$').setParseAction(lambda t: f'011{to3bit(t[0][3])}')('code') |  # @(R3)+, mode = '011'
        pp.Regex(r'^-\(R[1-7]\)$').setParseAction(lambda t: f'100{to3bit(t[0][3])}')('code') |  # -(R3), mode = '100'
        pp.Regex(r'^@-\(R[1-7]\)$').setParseAction(lambda t: f'101{to3bit(t[0][4])}')('code') |  # @-(R3), mode = '101',
        pp.Regex(r'^[1-7]+\(R[1-7]\)$').setParseAction(lambda t: f'110{to3bit(t[0][-2]) + from8to16bit(t[0][:-4])}')('code') |  # 2(R3), mode = '110'
        pp.Regex(r'^@[1-7]+\(R[1-7]\)$').setParseAction(lambda t: f'111{to3bit(t[0][-2]) + from8to16bit(t[0][1:-4])}')('code') |  # @2(R3), mode = '111'
        pp.Regex(r'^#[0-7]+$').setParseAction(lambda t: f'010111{from8to16bit(t[0][1:])}')('code') |  # #3, mode = '010'
        pp.Regex(r'^@#[0-7]+').setParseAction(lambda t: f'011111{from8to16bit(t[0][2:])}')('code') |  # @#100, mode = '011'
        pp.Regex(r'^[0-7]+').setParseAction(lambda t: f'110111{from8to16bit(t[0])}')('code') |  # 100, mode = '110'
        pp.Regex(r'^@[0-7]+').setParseAction(lambda t: f'111111{from8to16bit(t[0][1:])}')('code')  # @100, mode = '111'

)
# runtests!


mode_reg.runTests('''
R7
(R3)
(R3)+
@(R3)+
-(R3)
@-(R3)
277(R3)
@26(R3)
#100
@#100
100
@100
''')
print()
print("Отдельно для #100 - потому что в runtests это считывается как комментарий из-за значка # в начале строки")
res = mode_reg.parseString('#100')
print(res)
