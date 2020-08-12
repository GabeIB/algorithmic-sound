#tests wavetable oscilator functionality
import wave, struct, math
from playsound import playsound
from wavetable_synth import WaveTable

sampleRate = 44100 #hz
bitdepth = 16 #bits

obj = wave.open('wavetable_test.wav','w')
obj.setnchannels(1) # mono
obj.setsampwidth(int(bitdepth/8)) #takes param as bytes
obj.setframerate(sampleRate)

baseFreq = 4
duration = 1 #seconds

def bitcrush(f,bitdepth):
    s = round(f*math.pow(2, bitdepth-1)-1)
    if (s < -32768) : s = -32768 #hard clip
    if (s > 32767) : s = 32767
    return s

oscBank = []
for x in range(16):
    w = WaveTable('sinetable.wav', 44100)
    w.setFreq(398*(1.5**x))
    oscBank.append(w)

for i in range(int(sampleRate*duration)):
    f = 0
    for i in range(3):
        f += oscBank[i].getSample()*0.5*(0.2**i)
        oscBank[i].nextSample()
    s = bitcrush(f,16)
    
    data = struct.pack('<h', s)
    #print("data = " + str(data))
    obj.writeframesraw(data)

obj.close()
playsound('wavetable_test.wav')
