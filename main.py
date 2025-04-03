from pdp_11_mem import w_read
from pdp_11_commands import *
from data_load import *



def main():
    load_data("01_sum.pdp.o")
    reg[7] = 0o1000
    
    while True:
        word = w_read(reg[7])
        reg[7] += 2
        
        for cmd in commands:
            if (word & cmd["mask"]) == cmd["opcode"]:
                cmd["handler"](word)
                break
        else:
            print(f"Unknown command: {word:06o}")
            break


if __name__ == "__main__":
    main()