import sys

commands = [
    {'mask': 0o177777, 'opcode': 0o000000, 'name': 'halt', 'handler': lambda: do_halt()},
    {'mask': 0o170000, 'opcode': 0o010000, 'name': 'mov', 'handler': lambda: do_mov()},
    {'mask': 0o170000, 'opcode': 0o060000, 'name': 'add', 'handler': lambda: do_add()},
]


def do_halt():
    print("HALT")
    sys.exit(0)

def do_mov():
    print("MOV")

def do_add():
    print("ADD")