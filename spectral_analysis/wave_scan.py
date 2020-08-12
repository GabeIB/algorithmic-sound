import wave, struct, math
import matplotlib.pyplot as plt
from scipy.fft import fft
import numpy as np
from wavetable_synth import WaveTable
from playsound import playsound
from mpl_toolkits.mplot3d import Axes3D
from ipywidgets import interact 
import ipywidgets as widgets
import time

def getWavWrite(name, bitdepth = 16, channels = 1, frameRate = 44100):
    write = wave.open(name,'w')
    write.setnchannels(channels) # mono
    write.setsampwidth(int(bitdepth/8)) #takes param as bytes
    write.setframerate(frameRate)
    return write

def get_important_freq(pts, n, base, octaves):
    split = []
    important = []
    for i in range(octaves):
        lowbound = 20*(2**i)
        highbound = lowbound*2
        f = list(filter(lambda l: (l[0]>=lowbound and l[0]<highbound), pts)) 
        split.append(f)
    for s in split:
        local_freq = getMaxima(s, n)
        for f in local_freq:
            important.append(f[0])
    return sorted(important)

def getMaxima(pts, n):
    local_maxima = []
    global_maxima = []
    for x in range(len(pts)-1):
        if(x != 0):
            if (pts[x][1] > pts[x-1][1] and pts[x][1] > pts[x+1][1]):
                local_maxima.append(pts[x])
    local_maxima = sorted(local_maxima, key=lambda pt: pt[1])
    if (n > len(local_maxima)): n = len(local_maxima)
    for i in range(n):
        global_maxima.append(local_maxima.pop())
    return global_maxima

def bitcrush(f,bitdepth):
    s = round(f*math.pow(2, bitdepth-1)-1)
    if (s < -32768) : s = -32768 #hard clip
    if (s > 32767) : s = 32767
    return s


#reads n samples from obj
def getWindow(obj, n):
    l = []
    for x in range(n):
        f = obj.readframes(1)
        if(f==b''):
            raise IndexError()
        l.append((struct.unpack('<h', f[:2])[0])/(2**15))
    return l

#returns list len(freq) with corresponding gain values
def getGain(x, y, freq):
    gain = []
    for f in freq:
        #improve speed here
        for i in range(len(x)):
            if(f >= x[i] and f <= x[i+1]): index = i
        if(y[index] > y[index+1]): gain.append(y[index])
        else: gain.append(y[index+1])
    return gain

def linearInterpolate(a, b, remainder):
    return a*(1-remainder)+b*remainder

def linearInterpolate_pairlist(a, b, remainder):
    r = []
    for i in range(len(a)):
        r.append([linearInterpolate(a[i][0],b[i][0],remainder), linearInterpolate(a[i][1],b[i][1],remainder)])
    return r

#t is an int sample_count
def getCtl(ctl_data, t, sampleRate, timeStep):
    ctl = []
    index = t/(sampleRate*timeStep)
    integer = int(index)
    remainder = index - integer
    if(index > len(ctl_data)-1):
        raise IndexError
    else:
        return linearInterpolate_pairlist(ctl_data[integer], ctl_data[integer+1], remainder)
        


outputname = 'output.wav'
readF = wave.open('piano.wav', 'r')
writeF = getWavWrite(outputname)

left = []
ctl_data = []

sampleRate = 44100 #hz
bitdepth = 16 #bits
n = readF.getnframes()
frameRate = readF.getframerate()
time_step = .05 #seconds
windowLen = int(time_step * frameRate)
oscCount = 32

#get frequencies
freq_per_octave = 4
octaves = 10
base = 20 #hz
oscCount = octaves*freq_per_octave

window = getWindow(readF, int(.5*frameRate))
yf = np.abs(fft(window))
xf = np.linspace(0.0, frameRate, num=int(.5*frameRate))
pts = []
for i in range(int(len(yf)/2)):
    p = [xf[i], yf[i]]
    pts.append(p)
important_frequencies = get_important_freq(pts, freq_per_octave, base, octaves)
"""
p=[]
q=[]
upper_limit = 1000
for i in range(len(xf)):
    if(xf[i]<upper_limit):
        if(xf[i] in important_frequencies):
            plt.plot(xf[i],yf[i],'ro')
for i in range(len(xf)):
    if(xf[i]<upper_limit):
        p.append(xf[i])
        q.append(yf[i])
plt.plot(p,q,'g-')
plt.show()
exit()
"""
all_data = []
readF.rewind()
while(1):
    try:
        window = getWindow(readF, windowLen)
    except IndexError:
        break
    yf = np.abs(fft(window))
    xf = np.linspace(0.0, frameRate, num=windowLen)
    pts = []
    for i in range(int(len(yf)/2)):
        p = [xf[i], yf[i]]
        pts.append(p)
    all_data.append(pts)
    oscGain = getGain(xf, yf, important_frequencies)
    oscBank_timestep = []
    for i in range(len(oscGain)):
        p = [important_frequencies[i], oscGain[i]]
        oscBank_timestep.append(p)
    ctl_data.append(oscBank_timestep)

tf = np.linspace(0.0, len(ctl_data)*time_step, num=len(ctl_data))
x = []
y = []
for i in range(len(ctl_data[0])):
    xf = []
    yf = []
    for l in ctl_data:
        xf.append(l[i][0])
        yf.append(l[i][1])
    x.append(xf)
    y.append(yf)

import matplotlib as mpl
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt

#mpl.rcParams['legend.fontsize'] = 10

#fig = plt.figure()
#ax = fig.gca(projection='3d')
#for i in range(len(x)):
#    plt.plot(tf, y[i], label=str(int(x[i][0])))
#plt.legend(loc="upper right")
#plt.show()
"""
upper_limit = 1500
def showgraph(t=0):
    data = all_data[t]
    ctl = ctl_data[t]
    x = []
    y = []
    for d in data:
        if(d[0]<upper_limit):
            x.append(d[0])
            y.append(d[1])
    plt.clf()
    plt.ylim(0, 1200)
    plt.title('t = '+str(t*time_step))
    plt.plot(x,y,'b-')
    for osc in ctl:
        if(osc[0]<upper_limit):
            plt.plot(osc[0], osc[1], 'ro')

t=0
plt.ion()
while(1):
    showgraph(t)
    plt.draw()
    t = (t+1)%len(all_data)
    plt.pause(time_step)
   """ 

maxgain = 0
oscBank = []
for p in ctl_data[0]:
    w = WaveTable('sinetable.wav', 44100)
    w.setFreq(p[0])
    w.setGain(p[1]/(sampleRate*time_step))
    if(p[1]>maxgain): maxgain=p[1]
    oscBank.append(w)
print(maxgain)

t = 0
while(1):
    f=0
    try:
        ctl = getCtl(ctl_data, t, sampleRate, time_step)
    except IndexError:
        break
    for i in range(len(ctl)):
        oscBank[i].setFreq(ctl[i][0])
        oscBank[i].setGain(ctl[i][1]/(120*16*3))
        f += oscBank[i].nextSample()
    s = bitcrush(f,16)
    data = struct.pack('<h', s)
    writeF.writeframesraw(data)
    t+=1


readF.close()
writeF.close()
playsound('output.wav')  
