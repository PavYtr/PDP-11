from pdp_11_mem import w_read, reg
from pdp_11_commands import commands, ArgsProcessor
from data_load import load_data


def main():
    load_data("integral_tests/01_sum_neg.pdp.o")

    reg[7] = 0o1000
    print("---------------- running --------------")

    args = ArgsProcessor()
    while True:
        word = w_read(reg[7])
        print(f"{reg[7]:06o}:", end=" ")
        reg[7] += 2

        for cmd in commands:
            if (word & cmd["mask"]) == cmd["opcode"]:
                print(cmd["name"], end=" ")

                args.process(cmd["params"], word)

                cmd["handler"](args)
                print()
                break


if __name__ == "__main__":
    main()