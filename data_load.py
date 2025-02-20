from pdp_11_mem import b_write, mem, w_read

def load_data(filename):
    with open(filename, 'r') as file:
        while True:
            line = file.readline().strip()
            if not line:
                break

            address, n = map(lambda x: int(x, 16), line.split())
            for i in range(n):
                byte = int(file.readline().strip(), 16)
                b_write(address + i, byte)


def mem_dump(address, size):
    for i in range(0, size, 2):
        print(f"{address + i:06o}: ", end='')
        print(f"{w_read(address + i):06o}", end=' ')
        print(f"{w_read(address + i):04x}", end='\n')


# if __name__ == "__main__":
#     load_data("tests.txt")

#     mem_dump(0x40, 20)
#     print()
#     mem_dump(0x200, 0x26)