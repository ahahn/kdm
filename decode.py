from stringcodec import StringCodec
from framecodec import FrameCodec
from signalcodec import SignalCodec

import bitarray, itertools, time

stringcodec = StringCodec()
framecodec  = FrameCodec()
signalcodec = SignalCodec()

print "bits/sec:", (framecodec.bitrate / signalcodec.framelength)
print "bandwidth:", framecodec.bandwidth, "hz"

from scipy.io import wavfile
import sys
_, signal = wavfile.read(sys.argv[1])

t = time.time()

decoded = list(signalcodec.decode(framecodec, signal))
probabilistic_result = framecodec.probabilistic_decode(decoded)

complexity = 1
for x in probabilistic_result:
    if type(x) == list:
        complexity *=  len(x)
print 'decode complexity:', complexity

def process_probabilities(probabilities):
    lists = []
    list_indices = []
    for x in range(len(probabilities)):
        if type(probabilities[x]) == list:
            lists.append(probabilities[x])
            list_indices.append(x)
    products = itertools.product(*lists)
    for attempt in products:
        for x in range(len(attempt)):
            probabilities[list_indices[x]] = attempt[x]
        bits = bitarray.bitarray()
        for piece in probabilities:
            bits += piece
        yield bits

for possibility in process_probabilities(probabilistic_result):
    ecc, string = stringcodec.decode(possibility)
    if ecc:
        print string
        break

print
print time.time()-t
