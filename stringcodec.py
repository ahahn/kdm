import bitarray, reedsolo, string

DEFAULT_CHARSET = string.uppercase + string.digits + "?:;'\"!@#$%^&*()_-+=<>~`,./ \x00"

class StringCodec:
    def __init__(self, charset=DEFAULT_CHARSET, eccratio=1.0):
        self.charset = charset
        self.forward_codec = {}
        self.reverse_codec = {}
        self.eccratio = eccratio

        for x in range(len(self.charset)):
            binary = tuple(map(int, "{0:b}".format(x).zfill(6)))
            self.forward_codec[self.charset[x]] = binary
            self.reverse_codec[binary] = self.charset[x]

    def encode(self, s):
        s = s.upper()
        s = ''.join([x for x in s if x in self.charset])
        if len(s)%4: s += (4-(len(s)%4))*"\x00"
        print len(s)
        bits = bitarray.bitarray()
        for x in s:
            bits += self.forward_codec[x]
        s = bytearray(bits.tobytes())
        print len(s)
        ecclen = int(len(s) * self.eccratio)
        rs = reedsolo.RSCodec(ecclen)
        s = rs.encode(s)
        bits = bitarray.bitarray()
        bits.frombytes(bytes(s))
        return bits

    def decode(self, bits):
        b = bytearray(bits.tobytes())
        ecclen = int(len(b) * (self.eccratio/2))
        rs = reedsolo.RSCodec(ecclen)
        try:
            ecc = True
            b = rs.decode(b)
        except:
            ecc = False
            b = b[:len(b)-ecclen]
        bits = bitarray.bitarray()
        bits.frombytes(bytes(b))
        s = ''
        for x in range(0, len(bits), 6):
            seg = tuple(map(int, bits[x:x+6]))
            c = self.reverse_codec.get(seg,'')
            if c != '\x00': s += c
        return ecc, s

if __name__ == '__main__':
    codec = StringCodec()
    i = 'Hello World! Lol!'
    o = codec.encode(i)
    v = codec.decode(o)
    assert i.upper() == v
