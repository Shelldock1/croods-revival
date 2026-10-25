"""Convert Lua 5.1 bytecode from the game's format (size_t=4, float numbers)
to the desktop x86_64 format (size_t=8, double numbers)."""
import struct


class Reader:
    def __init__(self, data):
        self.d, self.p = data, 0

    def take(self, n):
        b = self.d[self.p:self.p + n]
        self.p += n
        return b

    def byte(self):
        return self.take(1)[0]

    def int(self):
        return struct.unpack('<i', self.take(4))[0]


def convert(data):
    assert data[:4] == b'\x1bLua' and data[4] == 0x51, 'not Lua 5.1 bytecode'
    sizeof_int, sizeof_size_t, sizeof_instr, sizeof_num, integral = data[7:12]
    assert (sizeof_int, sizeof_size_t, sizeof_instr) == (4, 4, 4)
    r = Reader(data)
    r.take(12)
    out = [data[:7] + bytes([4, 8, 4, 8, 0])]

    def string():
        n = struct.unpack('<I', r.take(4))[0]
        out.append(struct.pack('<Q', n))
        out.append(r.take(n))

    def number():
        raw = r.take(sizeof_num)
        if integral:
            v = float(struct.unpack('<i' if sizeof_num == 4 else '<q', raw)[0])
        else:
            v = struct.unpack('<f' if sizeof_num == 4 else '<d', raw)[0]
        out.append(struct.pack('<d', v))

    def ints(count_bytes_each):
        n = r.int()
        out.append(struct.pack('<i', n))
        out.append(r.take(n * count_bytes_each))
        return n

    def function():
        string()                                  # source
        out.append(r.take(8))                     # linedefined, lastlinedefined
        out.append(r.take(4))                     # nups, numparams, is_vararg, maxstacksize
        ints(4)                                   # code
        n = r.int()
        out.append(struct.pack('<i', n))          # constants
        for _ in range(n):
            t = r.byte()
            out.append(bytes([t]))
            if t == 1:
                out.append(r.take(1))
            elif t == 3:
                number()
            elif t == 4:
                string()
        n = r.int()
        out.append(struct.pack('<i', n))          # nested functions
        for _ in range(n):
            function()
        ints(4)                                   # lineinfo
        n = r.int()
        out.append(struct.pack('<i', n))          # locvars
        for _ in range(n):
            string()
            out.append(r.take(8))
        n = r.int()
        out.append(struct.pack('<i', n))          # upvalue names
        for _ in range(n):
            string()

    function()
    # the 7z unpacker may leave a few bytes of LZMA padding after the chunk
    return b''.join(out)
