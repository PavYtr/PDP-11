from pdp_11_mem import w_read
from pdp_11_commands import *
from data_load import *



def main():
    load_data("01_sum.pdp.o")
    print(f"{reg[7]:06o}:    . = 1000")
    reg[7] = 0o1000
    
    while True:
        word = w_read(reg[7])
        print(f"{reg[7]:06o}:", end=" ")
        reg[7] += 2

        for cmd in commands:
            if (word & cmd["mask"]) == cmd["opcode"]:
                print("", end=" ")
                print(cmd["name"], end=" ")
                cmd["handler"](word)
                break

if __name__ == "__main__":
    main()