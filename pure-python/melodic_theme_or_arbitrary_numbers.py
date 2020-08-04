import wave, struct, math
#from playsound import playsound

sampleRate = 44100 #hz
bitdepth = 16 #bits

obj = wave.open('melodic_theme_or_arbitrary_numbers.wav','w')
obj.setnchannels(1) # mono
obj.setsampwidth(int(bitdepth/8)) #takes param as bytes
obj.setframerate(sampleRate)

def recHarmonics_call(baseFreq, maxDepth, decayRate, t, level):
    if (level > maxDepth):
        return 0
    current_comp = math.sin((t*(2*math.pi)*baseFreq)/(sampleRate))
    return current_comp + decayRate*recHarmonics_call(baseFreq*2, maxDepth, decayRate, t, level+1)

def recursiveHarmonics(baseFreq, maxDepth, decayRate, t):
    return recHarmonics_call(baseFreq, maxDepth, decayRate, t, 0)

#takes float between 1 and -1 and returns crushed int in bitbounds
def bitcrush(f, crushAmt):
        s = round(f*math.pow(2, crushAmt-1)-1)
        s = round(s*math.pow(2, bitdepth-crushAmt))
        return s

def hardclip(s):
        if (s < -32768) : s = -32768 #hard clip
        if (s > 32767) : s = 32767
        return s

#obj.setnframes(len(notes)*duration*sampleRate)

#play each note for equal length in 12 tone scale
duration = 0.5 #seconds

#notes = [4, 8, 0, 11, 0, -3, 2, 4] # melodic theme or arbitrary numbers
notes = [4, 8, 0, 11] # melodic theme or arbitrary numbers
#notes = [7, 9, 3, 6]
baseFreq = 420
step_per_octave = 12
gain = 0.6
t = 0
#play theme with harmonic modulation


for n in notes:
    n -= 24
    frequency = baseFreq*math.pow(2, n/step_per_octave) #powers of 2 as fundamental in music and cs
    #print(frequency)
    for i in range(int(sampleRate*duration)):
        f = recursiveHarmonics(frequency, int(t*20/sampleRate)%8, 0.5, t) #number between -gain and +gain
        s = hardclip(bitcrush(f, 16))
        data = struct.pack('<h', s)
        #print("data = " + str(data))
        obj.writeframesraw(data)
        t += 1

#repeat last note of theme with compounding bit reduction
t = 0
bit = 16
for x in range(4):
    bit /= 2
    n = notes[3] - 24
    frequency = baseFreq*math.pow(2, n/step_per_octave) #powers of 2 as fundamental in music and cs
    #print(frequency)
    for i in range(int(sampleRate*duration)):
        f = recursiveHarmonics(frequency, int(t*20/sampleRate)%8, 0.5, t) #number between -gain and +gain
        s = hardclip(bitcrush(f, bit))
        data = struct.pack('<h', s)
        #print("data = " + str(data))
        obj.writeframesraw(data)
        t += 1

#play theme again
for n in notes:
    n -= 24
    frequency = baseFreq*math.pow(2, n/step_per_octave) #powers of 2 as fundamental in music and cs
    #print(frequency)
    for i in range(int(sampleRate*duration)):
        f = recursiveHarmonics(frequency, int(t*20/sampleRate)%8, 0.5, t) #number between -gain and +gain
        s = hardclip(bitcrush(f, 16))
        data = struct.pack('<h', s)
        #print("data = " + str(data))
        obj.writeframesraw(data)
        t += 1

for x in range(4):
    n = notes[x]-24
    if(x == 3): n -= 12
    frequency = baseFreq*math.pow(2, n/step_per_octave) #powers of 2 as fundamental in music and cs
    #print(frequency)
    for i in range(int(sampleRate*duration)):
        f = recursiveHarmonics(frequency, int(t*20/sampleRate)%8, 0.5, t) #number between -gain and +gain
        s = hardclip(bitcrush(f, 16))
        data = struct.pack('<h', s)
        #print("data = " + str(data))
        obj.writeframesraw(data)
        t += 1

#f is float btwn -1 and 1
#t is sample location
#timeon timeoff and offset are in seconds
#striate just works by either returning f or 0 whether it's in a timeon or timeoff zone
def striate(f, t, timeon, timeoff, offset):
    seconds_elapsed = t/sampleRate
    mod = (seconds_elapsed+offset) % (timeon+timeoff)
    if (mod <= timeon) : return f
    else: return 0

t = 0
timeon = 0.05
timeoff = 0.05
offset = 0
for x in range(4):
    n = notes[3] - 36
    frequency = baseFreq*math.pow(2, n/step_per_octave) #powers of 2 as fundamental in music and cs
    #print(frequency)
    for i in range(int(sampleRate*duration)):
        if(x < 2): timeon -= 0.02/(sampleRate*duration*2)
        if(x >= 2): timeoff -= 0.02/(sampleRate*duration*2)
        #print(str(timeon) + ", " + str(timeoff))
        f = recursiveHarmonics(frequency, int(t*20/sampleRate)%8, 0.5, t) #number between -gain and +gain
        s = hardclip(bitcrush(striate(f, t, timeon, timeoff, offset), 16))
        data = struct.pack('<h', s)
        #print("data = " + str(data))
        obj.writeframesraw(data)
        t += 1

t = 0
timeon = 0.02
timeoff = 0.03
offset = 0
for x in range(4):
    n = notes[3] - 36
    frequency = baseFreq*math.pow(2, n/step_per_octave) #powers of 2 as fundamental in music and cs
    #print(frequency)
    for i in range(int(sampleRate*duration)):
        if(x < 2): timeoff += 0.02/(sampleRate*duration*2)
        if(x >= 2): timeon += 0.03/(sampleRate*duration*2)
        #print(str(timeon) + ", " + str(timeoff))
        f = recursiveHarmonics(frequency, int(t*20/sampleRate)%8, 0.5, t) #number between -gain and +gain
        s = hardclip(bitcrush(striate(f, t, timeon, timeoff, offset), 16))
        data = struct.pack('<h', s)
        #print("data = " + str(data))
        obj.writeframesraw(data)
        t += 1

def calcFreq(base, steps, n):
    return base*math.pow(2, n/steps)

sticato = duration/2
for x in range(4):
    n = notes[3] - 36
    frequency = calcFreq(baseFreq, step_per_octave, n)
    for i in range(int(sampleRate*duration)):
        f = recursiveHarmonics(frequency, 4, 0.3, t)*0.5 #number between -gain and +gain
        s = hardclip(bitcrush(striate(f, t, sticato, duration-sticato, 0), 16))
        data = struct.pack('<h', s)
        obj.writeframesraw(data)
        t += 1

sticato = duration*2/3
for x in range(8):
    n = notes[3] - 36 + 1
    frequency = calcFreq(baseFreq, step_per_octave, n)
    for i in range(int(sampleRate*duration)):
        n1 = notes[0]
        f = recursiveHarmonics(frequency, 4, 0.3, t)*0.3 #number between -gain and +gain
        frequency1 = calcFreq(baseFreq, step_per_octave, n1)
        f1 = recursiveHarmonics(frequency1, 1, 0.3, t)*0.5 #number between -gain and +gain
        s = hardclip(bitcrush(striate(f, t, sticato, duration-sticato, 0)+striate(f1, t, math.sin(2*math.pi*(t/sampleRate))*0.02+0.12, math.sin(math.pi*(t/sampleRate))*0.02+0.1, 0), 16))
        data = struct.pack('<h', s)
        obj.writeframesraw(data)
        t += 1

sticato = duration/2
for x in range(8):
    n = notes[3] - 36
    frequency = calcFreq(baseFreq, step_per_octave, n)
    for i in range(int(sampleRate*duration)):
        f = recursiveHarmonics(frequency, 4, 0.3, t)*0.5 #number between -gain and +gain
        s = hardclip(bitcrush(striate(f, t, sticato, duration-sticato, 0), 16))
        data = struct.pack('<h', s)
        obj.writeframesraw(data)
        t += 1


sticato = duration*2/3
t=0
for x in range(8):
    n = notes[3] - 36 + 1
    n1 = notes[x%4]
    frequency = calcFreq(baseFreq, step_per_octave, n)
    for i in range(int(sampleRate*duration)):
        f = recursiveHarmonics(frequency, 4, 0.3, t)*0.3 #number between -gain and +gain
        frequency1 = calcFreq(baseFreq, step_per_octave, n1)
        f1 = recursiveHarmonics(frequency1, 1, 0.3, t)*0.5 #number between -gain and +gain
        s = hardclip(bitcrush(striate(f, t, sticato, duration-sticato, 0)+striate(f1, t, math.sin(2*math.pi*(t/sampleRate))*0.02+0.12, math.sin(math.pi*(t/sampleRate))*0.02+0.12, 0), 16))
        data = struct.pack('<h', s)
        obj.writeframesraw(data)
        t += 1

sticato = duration/2
for x in range(8):
    n = notes[3] - 36
    frequency = calcFreq(baseFreq, step_per_octave, n)
    for i in range(int(sampleRate*duration)):
        f = recursiveHarmonics(frequency, 4, 0.3, t)*0.5 #number between -gain and +gain
        s = hardclip(bitcrush(striate(f, t, sticato, duration-sticato, 0), 16))
        data = struct.pack('<h', s)
        obj.writeframesraw(data)
        t += 1

sticato = duration*2/3
for x in range(8):
    n = notes[3] - 36 + 1
    n1 = -notes[x%4]
    if (x>=4) : n1 += 12
    frequency = calcFreq(baseFreq, step_per_octave, n)
    for i in range(int(sampleRate*duration)):
        f = recursiveHarmonics(frequency, 4, 0.3, t)*0.3 #number between -gain and +gain
        frequency1 = calcFreq(baseFreq, step_per_octave, n1)
        f1 = recursiveHarmonics(frequency1, 1, 0.3, t)*0.5 #number between -gain and +gain
        s = hardclip(bitcrush(striate(f, t, sticato, duration-sticato, 0)+striate(f1, t, math.sin(2*math.pi*(t/sampleRate))*0.02+0.12, math.sin(math.pi*(t/sampleRate))*0.02+0.12, 0), 16))
        data = struct.pack('<h', s)
        obj.writeframesraw(data)
        t += 1

sticato = duration/2
for x in range(8):
    n = notes[3] - 36
    frequency = calcFreq(baseFreq, step_per_octave, n)
    for i in range(int(sampleRate*duration)):
        f = recursiveHarmonics(frequency, 4, 0.3, t)*0.5 #number between -gain and +gain
        s = hardclip(bitcrush(striate(f, t, sticato, duration-sticato, 0), 16))
        data = struct.pack('<h', s)
        obj.writeframesraw(data)
        t += 1

sticato = duration/2
for x in range(8):
    n = notes[3] - 36 + 1
    n1 = -notes[x%4]
    if (x>=4) : n1 = -notes[-x%4]+ 12
    frequency = calcFreq(baseFreq, step_per_octave, n)
    for i in range(int(sampleRate*duration)):
        f = recursiveHarmonics(frequency, 4, 0.3, t)*0.3 #number between -gain and +gain
        frequency1 = calcFreq(baseFreq, step_per_octave, n1)
        f1 = recursiveHarmonics(frequency1, 1, 0.3, t)*0.5 #number between -gain and +gain
        s = hardclip(bitcrush(striate(f, t, sticato, duration-sticato, 0)+striate(f1, t, math.sin(2*math.pi*(t/sampleRate))*0.02+0.12, math.sin(math.pi*(t/sampleRate))*0.02+0.12, 0), 16))
        data = struct.pack('<h', s)
        obj.writeframesraw(data)
        t += 1

sticato = duration/2
for x in range(8):
    n = notes[3] - 36
    frequency = calcFreq(baseFreq, step_per_octave, n)
    for i in range(int(sampleRate*duration)):
        f = recursiveHarmonics(frequency, 4, 0.3, t)*0.5 #number between -gain and +gain
        s = hardclip(bitcrush(striate(f, t, math.sin(2*math.pi*(t/sampleRate))*0.02+0.2, math.sin(math.pi*(t/sampleRate))*0.02+0.18, 0), 16))
        data = struct.pack('<h', s)
        obj.writeframesraw(data)
        t += 1

for n in notes:
    n -= 24
    frequency = baseFreq*math.pow(2, n/step_per_octave) #powers of 2 as fundamental in music and cs
    #print(frequency)
    for i in range(int(sampleRate*duration)):
        f = recursiveHarmonics(frequency, int(t*20/sampleRate)%8, 0.5, t) #number between -gain and +gain
        s = hardclip(bitcrush(f, 16))
        data = struct.pack('<h', s)
        #print("data = " + str(data))
        obj.writeframesraw(data)
        t += 1

for n in notes:
    n -= 36
    frequency = baseFreq*math.pow(2, n/step_per_octave) #powers of 2 as fundamental in music and cs
    #print(frequency)
    for i in range(int(sampleRate*duration)):
        f = recursiveHarmonics(frequency, int(t*20/sampleRate)%8, 0.5, t) #number between -gain and +gain
        s = hardclip(bitcrush(f, 16))
        data = struct.pack('<h', s)
        #print("data = " + str(data))
        obj.writeframesraw(data)
        t += 1

for n in notes:
    n -= 36
    frequency = baseFreq*math.pow(2, n/step_per_octave) #powers of 2 as fundamental in music and cs
    #print(frequency)
    for i in range(int(sampleRate*duration)):
        f = recursiveHarmonics(frequency, int(t*20/sampleRate)%8, 0.5, t) #number between -gain and +gain
        s = hardclip(bitcrush(f, 6))
        data = struct.pack('<h', s)
        #print("data = " + str(data))
        obj.writeframesraw(data)
        t += 1

t=0
for x in range(4):
    n = notes[3] - 36
    frequency = baseFreq*math.pow(2, n/step_per_octave) #powers of 2 as fundamental in music and cs
    for i in range(int(sampleRate*duration)):
        f = recursiveHarmonics(frequency, int(t*32*2/sampleRate)%8, 0.3, t)
        s = hardclip (bitcrush(f, 16))
        data = struct.pack('<h', s)
        obj.writeframesraw(data)
        t+=1

obj.close()
#playsound('melodic_theme_or_arbitrary_numbers.wav')
