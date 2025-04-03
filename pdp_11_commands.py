from pdp_11_mem import w_read, w_write, reg
import sys

commands = [
    {'mask': 0o177777, 'opcode': 0o000000, 'name': 'halt', 'handler': lambda w: do_halt(w)},
    {'mask': 0o170000, 'opcode': 0o010000, 'name': 'mov', 'handler': lambda w: do_mov(w)},
    {'mask': 0o170000, 'opcode': 0o060000, 'name': 'add', 'handler': lambda w: do_add(w)},
]

class ModeNotIplementedError(Exception):
    pass


def get_mr(w):
    r = w & 7
    mode = (w >> 3) & 7
    addr, value = 0, 0
    
    if mode == 0:  # Регистровый
        addr = r
        value = reg[r]
        print(f"R{r}", end=' ')
    elif mode == 1:  # Косвенный
        addr = reg[r]
        value = w_read(addr)
        print(f"(R{r})", end=' ')
    elif mode == 2:  # Автоинкрементный
        addr = reg[r]
        value = w_read(addr)
        reg[r] += 2
    else:
        raise ModeNotIplementedError(f"Unsupported mode {mode}")
    
    return addr, value

def do_mov(w):
    src = (w >> 6) & 0o77
    dst = w & 0o77
    
    _, src_val = get_mr(src)
    dst_addr, _ = get_mr(dst)
    
    # Для регистрового режима
    if (dst >> 3) & 7 == 0:
        reg[dst & 7] = src_val
    else:
        w_write(dst_addr, src_val)
    print(f"; MOV: {src_val} -> R{dst & 7}")

def do_add(w):
    src = (w >> 6) & 0o77
    dst = w & 0o77
    
    _, src_val = get_mr(src)
    dst_addr, dst_val = get_mr(dst)
    
    result = (src_val + dst_val) & 0xFFFF
    
    # Для регистрового режима
    if (dst >> 3) & 7 == 0:
        reg[dst & 7] = result
    else:
        w_write(dst_addr, result)
    print(f"; ADD: {src_val} + {dst_val} = {result}")

def do_halt(w):
    print("\nHALT")
    print(f"Result in R1: {reg[1]}")
    sys.exit(0)