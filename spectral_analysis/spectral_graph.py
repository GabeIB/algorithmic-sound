import wave, struct
import matplotlib.pyplot as plt
from scipy.fft import fft
import numpy as np
import sys

obj = wave.open('wavetable_test.wav', 'r')

upper_limit = float(sys.argv[1]) #upper limit of graphed freq range

left = []

n = obj.getnframes()
frameRate = obj.getframerate()
t = 1.0/44100.0
time_step = .05 #seconds
window = int(time_step * frameRate)

upper_samp = int(upper_limit*time_step) # (window*upper_limit)/frameRate

for x in range(window):
    f = obj.readframes(1)
    left.append((struct.unpack('<h', f[:2])[0])/(2**15))

yf = fft(left)
yf = np.abs(yf)
xf = np.linspace(0.0, frameRate, num=window)

def getMaxima(datax, datay, n):
    local_maxima = []
    global_maxima = []
    for x in range(len(datay)-1):
        if(x != 0):
            if (datay[x] > datay[x-1] and datay[x] > datay[x+1]):
                local_maxima.append([datax[x], datay[x]])
    for y in range(n):
        largest = [0,0]
        index = 0
        for x in range(len(local_maxima)):
            if(local_maxima[x][1] > largest[1]):
                largest = local_maxima[x]
                index = x
        global_maxima.append(largest)
        del local_maxima[index]
    return global_maxima
 
local_maxima = []

for x in range(int(len(yf)/2)):
    if (x != 0):
        if (yf[x] > yf[x-1] and yf[x] > yf[x+1]):
            local_maxima.append([xf[x], yf[x]])


local_maxima = getMaxima(xf[0:int(len(xf)/2)], yf[0:int(len(yf)/2)], 16)

plt.figure(figsize=(20,10))

plt.plot(xf[0:upper_samp+1], np.abs(yf[0:upper_samp+1]), 'r-')
print(local_maxima)
for p in local_maxima:
    if(p[0]<upper_limit):
        plt.plot(p[0], p[1], 'bo')
plt.grid()
plt.show()
