import wave, struct
import matplotlib.pyplot as plt
import sys

obj = wave.open(sys.argv[1], 'r')

left = []
#right = []

for x in range(obj.getnframes()):
    f = obj.readframes(1)
    left.append(struct.unpack('<h', f[:2])[0]) #takes the first 2 bytes and interprets as little endian short
    #right.append(struct.unpack('<h', f[2:4])[0]) #same but second 2 bytes

#plt.figure()
#plt.subplot(211)
plt.plot(left)

#plt.subplot(212)
#plt.plot(right)
plt.show()
