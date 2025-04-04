import pyparsing as pp


# Улучшенные определения элементов
identifier = pp.Word(pp.alphas, pp.alphanums + "_")
mnemonic = pp.oneOf("mov add sub halt", caseless=True)  # Список команд
command_name = mnemonic("command")

# Числа: #10 или 10 (целые)
number = pp.Combine(pp.Optional('#') + pp.Word(pp.nums))
# Регистры: r0, r1, ..., r15
register = pp.Combine(pp.CaselessLiteral('r') + pp.Word(pp.nums, max=2))
argument = number | register | identifier
arguments = pp.Group(pp.delimitedList(argument, delim=pp.Suppress(',')))("args")

label = (identifier + pp.Suppress(":"))("label")
comment = (pp.Suppress(';') + pp.restOfLine.setParseAction(lambda t: t[0].strip()))("comment")

# Основное правило
rule = (
    pp.Optional(label, default='')
    + pp.Optional(command_name, default='')
    + pp.Optional(arguments, default=[])
    + pp.Optional(comment, default='')
)

debug_mode = True

def parse(s):
    s = s.lower().strip()
    if s[0] == '.':
        s = s.replace(" ", "")
        return {'label': '', 'command_name': 'start_from_address', 'arguments': [ s[2:] ], 'comment': ''}
    parsed = rule.parseString(s, parseAll=True)
    args = []
    if len(parsed.args) != 0:
        args = parsed.args.asList()
    comment = ''
    if parsed.comment  != '':
        comment = parsed.comment[0]
    label = ''
    if  parsed.label != '':
        label = parsed.label[0]
    result = {
        'label': label,
        'command_name': parsed.command if 'command' in parsed else '',
        'arguments': args,
        'comment': comment
    }

    """if debug_mode:
        print("s:", s)
        #print([parsed.label, parsed.command_name, parsed.arguments, parsed.comment])
        print("return:", result)
        print()"""

    return result


dict_machine_code = {'start': '', 'data': []}

assembler_code = []
filename = 'asm_code.txt'
#filename = 'pdp11_code.txt'
with open(filename, 'r', encoding='utf-8') as file:
    for line in file:
        line = line.lower().strip()
        assembler_code.append(parse(line))

if debug_mode:
    print("assembler_code")
    for line in assembler_code:
        print(line)
    print()

opcode = {
    'mov': '0001',
    'add': '0110',
    'halt': '0000'
}

def to3bit(x):
    res = str(bin(int(x))[2:])
    while len(res) < 3:
        res = '0' + res
    return res

#print(to3bit('3'))

def to_four_digit_hex_number(x):
    res = str(hex(int(x)))[2:]
    while len(res) < 4:
        res = '0' + res
    return res

#print(to_four_digit_hex_number('10'))

#для начала считаем, что сначала идёт команда. то есть без label
#считаем, что у нас могут быть только 3 команды: move/add/halt
#у этих 3х команд аргументы - это SSDD
#вырианты: cmd R, R; cmd #, R;

#на случай # у нас есть переменные additional...
def to_raw_machine_code(command):

    if command['command_name'] == 'halt':
        dict_machine_code['data'].append('0' * 16)
        return '0' * 16, ''
    if command['command_name'] == 'start_from_address':
        dict_machine_code['start'] = to_four_digit_hex_number(int(command['arguments'][0], 8))
        return [to_four_digit_hex_number(int(command['arguments'][0], 8)), 'number of bytes in the resulting file']

    command_code = opcode[command['command_name']]

    source = command['arguments'][0]
    source_mode = ''
    source_R_num = ''
    if source[0] == 'r':
        source_mode = '000'
        source_R_num = to3bit(source[1])
    source_additional_word = ''
    if source[0] == '#':
        source_mode = '010'
        source_R_num = '111'
        source_additional_word = to_four_digit_hex_number(source[1:])

    destination = command['arguments'][1]
    destination_mode = ''
    destination_R_num = ''
    if destination[0] == 'r':
        destination_mode = '000'
        destination_R_num = to3bit(destination[1])

    raw_machine_command = command_code + source_mode + source_R_num + destination_mode + destination_R_num
    dict_machine_code['data'].append(raw_machine_command)
    if source_additional_word != '':
        dict_machine_code['data'].append(source_additional_word)
    return raw_machine_command, source_additional_word

raw_machine_code = []
for cmd in assembler_code:
    raw_machine_code.append(to_raw_machine_code(cmd))

print("raw_machine_code",  raw_machine_code)

machine_code = []
def to_machine_code(raw_machine_command):
    #print("raw_machine_command", raw_machine_command)
    if len(raw_machine_command[0]) != 16:
        return raw_machine_command

    raw_command_code = raw_machine_command[0]
    piece1 = raw_command_code[:4]
    piece2 = raw_command_code[4:8]
    piece3 = raw_command_code[8:12]
    piece4 = raw_command_code[12:]
    #print("pieces", piece1, piece2, piece3, piece4)
    num1 = hex(int(piece1,  2))[2:] + hex(int(piece2, 2))[2:]
    num2 = hex(int(piece3,  2))[2:] + hex(int(piece4, 2))[2:]
    machine_command = [num2, num1]

    additional_num1 = ''
    additional_num2 = ''
    if len(raw_machine_command[1]) == 4:
        additional_num1 = raw_machine_command[1][:2]
        additional_num2 = raw_machine_command[1][2:]
        machine_command.append(additional_num2)
        machine_command.append(additional_num1)

    return machine_command



for cmd in raw_machine_code:
    cmd = to_machine_code(cmd)
    machine_code.append(cmd)

print("machine_code:", machine_code)
print("dict_machine_code:", dict_machine_code)

with open("machine_code.txt", "w", encoding="utf-8") as file:
    for cmd in machine_code:
        for line in cmd:
            file.write(line + "\n")



print("Файл успешно создан и записан.")

