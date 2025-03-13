import sys
from pdp_11_mem import w_read, w_write

def do_halt():
    print("HALT")
    sys.exit(0)

def do_mov():
    print("MOV")

def do_add():
    print("ADD")

# test run
# w_write(0o01000, 0o010234)
# w_write(0o01002, 0o063241)
# w_write(0o01004, 0o062345)
# w_write(0o01006, 0o071345)
# w_write(0o01010, 0)  # HALT


pc = 0o01000
while True:
    word = w_read(pc)
    print(f"{pc:06o} {word:06o}")
    pc += 2
    if word == 0:
        do_halt()
    elif word & 0xF000 == 0o010000:
        do_mov()
    elif word & 0xF000 == 0o060000:
        do_add()
    else:
        print("Unknown")
