from numpy.fft import fft, fftfreq, ifft
import math, numpy as np

def getPower (num, base):
    if base == 1 and num != 1: return False
    if base == 1 and num == 1: return True
    if base == 0 and num != 1: return False
    power = int (math.log (num, base) + 0.5)
    if base ** power == num: return power

class PeakFinder:
    def __init__(self, signal, samplerate):
        self.signal = signal
        self.samplerate = samplerate
        self.F = None
        self.a = None
        self.f = None
    def preprocess(self):
        self.F = fft(self.signal)
        self.a = np.log10(np.abs(np.fft.rfft(self.signal)))
        self.f = fftfreq(len(self.F), 1.0/(self.samplerate))
        self.f = self.f
    def findpeak(self, minfreq, maxfreq):
        self.preprocess()
        #s = filter(lambda x: minfreq<=x[0] and x[0] <= maxfreq, zip(self.f, self.a))
        #if not s: return
        y = np.indices(self.f.shape)
        locs = y[:, (self.f >= minfreq) & (self.f <= maxfreq)]
        peak = self.f[locs][0][np.argmax(self.a[locs])]
        if peak%1 == 0: return int(peak)
        return peak

if __name__ == '__main__':
    print getPower(8,2)
