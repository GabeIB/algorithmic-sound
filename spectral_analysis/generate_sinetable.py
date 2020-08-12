import wave, struct, math

sampleRate = 44100 #hz
bitdepth = 16 #bits

obj = wave.open('sinetable.wav','w')
obj.setnchannels(1) # mono
obj.setsampwidth(int(bitdepth/8)) #takes param as bytes
obj.setframerate(sampleRate)

f = 1 #frequency 1hz

for t in range(int(sampleRate/f)):
    float_data = math.sin((t*2*math.pi*f)/sampleRate)
    s = round(float_data*math.pow(2, bitdepth-1))
    if (s < -32768) : s = -32768 #hard clip
    if (s > 32767) : s = 32767
    data = struct.pack('<h', s)
    obj.writeframesraw(data)

obj.close()
