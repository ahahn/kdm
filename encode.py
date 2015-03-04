from stringcodec import StringCodec
from framecodec import FrameCodec
from signalcodec import SignalCodec
from numpy import append, array
import struct

input = "KR1LLR CN85 -100"
print "message length:", len(input)

stringcodec = StringCodec()
framecodec  = FrameCodec()
signalcodec = SignalCodec()

print "bits/sec:", (framecodec.bitrate / signalcodec.framelength)
print "bandwidth:", framecodec.bandwidth, "hz"

string = stringcodec.encode(input)
frames = framecodec.encode(string)
signal = signalcodec.encode(framecodec.carrier, frames)
 
from scipy.io import wavfile
import sys
wavfile.write(sys.argv[1], signalcodec.samplerate, signal)
