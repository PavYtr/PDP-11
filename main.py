from pdp_11_mem import w_read, reg
from pdp_11_commands import commands
from data_load import load_data


def main():
    load_data("01_sum.pdp.o")

    reg[7] = 0o1000
    print("---------------- running --------------")

    while True:
        word = w_read(reg[7])
        print(f"{reg[7]:06o}:", end=" ")
        reg[7] += 2

        for cmd in commands:
            if (word & cmd["mask"]) == cmd["opcode"]:
                print(cmd["name"], end=" ")

                if hasattr(__import__(__name__), 'args'):
                    globals()['args'].clear()

                cmd["handler"](word)
                break


if __name__ == "__main__":
    main()