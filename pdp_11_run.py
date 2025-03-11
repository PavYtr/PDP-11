import sys
from pdp_11_mem import w_read

def do_halt():
    print("HALT stopped the program")
    sys.exit(0)

def do_mov():
    print("MOV happened")

def do_add():
    print("ADD happened")

pc = 0o01000
while True:
    word = w_read(pc)
    print(f"{pc:06o} {word:06o}:")
    pc += 2
    if word == 0:
        do_halt()
    elif word & 0xF000 == 0o010000:
        do_mov()
    elif word & 0xF000 == 0o060000:
        do_add()
    else:
        print("Unknown")
