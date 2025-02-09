
MEMSIZE = 64 * 1024

mem = [None] * MEMSIZE

def b_write(adr, value):
    mem[adr] = value
    

def b_read(adr):
    return mem[adr]
           
def w_write(adr, value):
    mem[adr+1] = hex(int(value, 16) >> 8)
    mem[adr] = hex(int(value, 16))
    

def w_read(adr):
    word = int(mem[adr+1], 16) << 8
    word |= int(mem[adr], 16)
    print(hex(word))
    return hex(word)




b0 = '0x0a'
b1 = '0x0b'
b_write(2, b0)
assert b0 == b_read(2)


adr = 4
w = '0xb0a'
b_write(adr, b0)
b_write(adr+1, b1)
wres = w_read(adr)    

adr = 6
word = '0x0'
w_write(6, word)
assert word == w_read(6)


print(wres, b1, b0)
assert w == wres

