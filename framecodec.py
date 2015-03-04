import bitarray, util

class FrameCodec:
    def __init__(self, carrier=500, channelcount=4, tonespacing=2, tonecount=4):
        self.carrier = carrier
        self.channelcount = channelcount
        self.tonespacing  = tonespacing
        self.tonecount    = tonecount
        self.channelwidth = self.tonespacing * self.tonecount
        self.channelbits  = util.getPower(self.tonecount, 2)

        self.states = [tuple(map(bool, map(int, tuple("{0:b}".format(x).zfill(self.channelbits))))) for x in range(self.tonecount)]
        self.channels = dict(self.mkchannels())

        self.tones_to_bin = {}
        self.bin_to_tones = {}
        for channel, tones in self.channels.items():
          self.bin_to_tones[channel] = {}
          for tone, bin in tones.items():
            self.tones_to_bin[tone] = bin
            self.bin_to_tones[channel][bin] = tone

        self.tones = []
        for tones in self.channels.values():
            self.tones += tones.keys()
        self.tones.sort()
        self.bandwidth = self.tones[-1] - self.tones[0]

        self.bitrate = self.channelcount * max(1, self.channelbits)

    def mkchannels(self):
        lowerbound = self.carrier - ((self.channelcount/2) * self.channelwidth)
        upperbound = self.carrier + ((self.channelcount/2) * self.channelwidth)
        if lowerbound == upperbound:
            yield self.carrier + self.channelwidth, dict(self.mktones(self.carrier + self.channelwidth))
        for center in range(lowerbound, upperbound+1, self.channelwidth):
            if center == self.carrier: continue
            yield center, dict(self.mktones(center))

    def mktones(self, channel):
        states = list(self.states)
        lowerbound = channel - (self.channelwidth/2)
        upperbound = channel + (self.channelwidth/2)
        for tone in range(lowerbound, upperbound, self.tonespacing):
            yield tone, states.pop()

    def encode(self, bits):
        for x in range(0, len(bits), self.bitrate):
          framebits = bits[x:x+self.bitrate]
          frame = []
          channels = list(sorted(self.channels, reverse=True))
          for y in range(0, len(framebits), self.channelbits):
            channel = channels.pop()
            tones = self.channels[channel]
            channelbits = tuple(framebits[y:y+self.channelbits])
            tone = self.bin_to_tones[channel][channelbits]
            frame.append(tone)
          yield frame

    def decode(self, frames):
        bits = bitarray.bitarray()
        for frame in frames:
            frame.sort()
            for tone in frame:
                if tone in self.tones:
                    bits += self.tones_to_bin[tone]
                    continue
                possibilities = [(x, abs(tone-x)) for x in self.tones]
                possibilities.sort(key=lambda x:x[1])
                tone = possibilities[0][0]
                bits += self.tones_to_bin[tone]
        return bits

    def probabilistic_decode(self, frames):
        possibits = []
        minbits = (len(frames) * len(frames[0])) * 0.6
        for frame in frames:
            frame.sort()
            for tone in frame:
                if tone in self.tones:
                    possibits.append(self.tones_to_bin[tone])
                    continue
                possibilities = [x for x in self.tones if abs(tone-x) <= self.tonespacing]
                possibilities.sort(key=lambda x:abs(tone-x))
                possibits.append([self.tones_to_bin[x] for x in possibilities])
        return possibits

if __name__ == "__main__":
    codec = FrameCodec()
    data = bitarray.bitarray()
    data += [0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1]
    encoded = list(codec.encode(data))
    encoded[0][0] += 1
    decoded = codec.decode(encoded)
    print decoded, data
