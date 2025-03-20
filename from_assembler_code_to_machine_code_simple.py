import pyparsing as pp

command_name = pp.Word(pp.alphas)
argument_name = pp.Word(pp.printables, exclude_chars=';,')
arguments = pp.Optional(argument_name) + pp.ZeroOrMore(pp.Suppress(',') + argument_name)
label = pp.Word(pp.alphas) + pp.Optional(pp.Suppress(' ')) + pp.Suppress(":")
comment = pp.Suppress(';') + pp.Optional(pp.Suppress(' ')) + pp.restOfLine()
rule =  pp.Optional(label) + pp.Optional(command_name) + pp.Optional(arguments) + pp.Optional(comment)
def parse(s):
    s = s.lower().rstrip().lstrip()
    if s[0] == '.':
        s = s.replace(" ", "")
        return ['start_from_address', s[2:]]
    return rule.parseString(s).asList()



assembler_code = []
filename = 'assembler_code.txt'
#filename = 'pdp11_code.txt'
with open(filename, 'r', encoding='utf-8') as file:
    for line in file:
        line = line.lower().rstrip().lstrip()
        assembler_code.append(parse(line))

print("assembler_code", assembler_code)

opcode = {
    'mov': '0001',
    'add': '0110'
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
    if command[0] == 'halt':
        return ["00", "00"]
    if command[0] == 'start_from_address':
        return [to_four_digit_hex_number(int(command[1], 8)), 'number of bytes in the resulting file']
    command_code = opcode[command[0]]

    source = command[1]
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

    destination = command[2]
    destination_mode = ''
    destination_R_num = ''
    if destination[0] == 'r':
        destination_mode = '000'
        destination_R_num = to3bit(destination[1])

    raw_machine_command = command_code + source_mode + source_R_num + destination_mode + destination_R_num
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

print("machine_code", machine_code)

with open("machine_code.txt", "w", encoding="utf-8") as file:
    for cmd in machine_code:
        for line in cmd:
            file.write(line + "\n")

print("Файл успешно создан и записан.")
