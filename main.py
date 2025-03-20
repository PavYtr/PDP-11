from pdp_11_mem import w_read
from pdp_11_commands import commands


def main():
    pc = 0o01000
    while True:
        word = w_read(pc)
        print(f"{pc:06o} {word:06o}")
        pc += 2
        
        for opcode, cmd in commands.items():
            if (word & cmd.mask) == opcode:
                cmd.handler()
                break
        else:
            print("Unknown")
