
MEMSIZE = 64 * 1024

mem = [0] * MEMSIZE
reg = [0] * 8

def b_write(adr, value):
    mem[adr] = value & 0xFF
    

def b_read(adr):
    return mem[adr]
           

def w_write(adr, value):
    if adr % 2 != 0:
        raise ValueError("Word adress must be even")
    mem[adr+1] = (value >> 8) & 0xFF
    mem[adr] = value & 0xFF


def w_read(adr):
    if adr % 2 != 0:
        raise ValueError("Word adress must be even")
    word = mem[adr+1] << 8 
    word |= mem[adr]
        
    return word & 0xFFFF




# b0 = 0x0a
# b1 = 0x0b
# b_write(2, b0)
# assert b0 == b_read(2)


# adr = 4
# w = 0xb0a
# b_write(adr, b0)
# b_write(adr+1, b1)
# wres = w_read(adr)    

# adr = 6
# word = 0x0
# w_write(6, word)
# assert word == w_read(6)


# print(wres, b1, b0)
# assert w == wres

# a1 = -1
# w_write(14, a1)
# assert w_read(14) == a1