from pdp_11_mem import w_read
from pdp_11_commands import *
from data_load import *


def main():
    load_data("byte_code.txt")

    pc = 0o01000
    while True:
        word = w_read(pc)
        pc += 2
        
        for cmd in commands:
            if (word & cmd["mask"]) == cmd["opcode"]:
                cmd["handler"]()
                break
            else:
                print("Unknown")


if __name__ == "__main__":
    main()