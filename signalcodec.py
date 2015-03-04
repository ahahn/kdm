from numpy import linspace,sin,pi,int16,array,append,arange
from util import PeakFinder
import numpy as np
import copy

class SignalCodec:
    def __init__(self, framelength=0.5, baseamp=12750, samplerate=48000):
        self.framelength = framelength
        self.baseamp = baseamp
        self.samplerate = samplerate

    def note(self, freq, length=None, amp=None):
        amp = amp or self.baseamp
        length = length or self.framelength
        t = linspace(0, length, length * self.samplerate)
        data = sin(2 * pi * freq * t) * amp
        return data

    def encode(self, carrier, frames):
        signal = array([])
        framecount = 0
        for frame in frames:
            framecount += 1
            framesignal = None
            for tone in frame:
                if framesignal == None: framesignal = self.note(tone) * 1.0/len(frame)
                else: framesignal += self.note(tone) * 1.0/len(frame)
            signal = append(signal, framesignal)
        carrier = self.note(carrier, length=self.framelength * framecount)
        signal = signal + carrier
        return signal.astype(int16)

    def decode(self, framedecoder, signal):
        for x in range(0, len(signal), int(self.samplerate*self.framelength)):
            chunk = signal[x:x+int(self.samplerate*self.framelength)]
            peakfinder = PeakFinder(chunk, self.samplerate)
            frame = []
            carrier = peakfinder.findpeak(
                                framedecoder.carrier - (framedecoder.channelwidth/2),
                                framedecoder.carrier + (framedecoder.channelwidth/2)
                                )
            if not carrier: continue
            frequencydrift = carrier - framedecoder.carrier
            channel_ranges = {}
            all_tones = []
            for channel, tones in framedecoder.channels.items():
                for tone, bin in tones.items():
                    tone += frequencydrift
                    all_tones.append(tone)
                tones = tones.keys()
                tones.sort()
                channel_ranges[channel] = (tones[0],
                                           tones[-1])
            for channel in sorted(channel_ranges):
                channel_range = channel_ranges[channel]
                tone = peakfinder.findpeak(
                                 channel_range[0] + frequencydrift - (framedecoder.tonespacing/2),
                                 channel_range[1] + frequencydrift + (framedecoder.tonespacing/2)
                                 )
                frame.append(tone)
            yield frame

if __name__ == "__main__":
    from scipy.io import wavfile
    import sys
    codec = SignalCodec()
    s = codec.encode(500, [[300,400,600,700]])
    print s
    wavfile.write(sys.argv[1], codec.samplerate, s)
