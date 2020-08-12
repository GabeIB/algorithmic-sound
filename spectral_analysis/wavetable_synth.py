import wave, struct

class WaveTable:

    def __init__(self, table_name, sampleRate):
        obj = wave.open(table_name, 'r')
        self.outsideSampleRate = sampleRate
        self.table = []
        self.tableSampleRate = obj.getframerate()
        self.bitDepth = obj.getsampwidth()*8
        for x in range(obj.getnframes()):
            f = obj.readframes(1)
            self.table.append(struct.unpack('<h', f[:2])[0]/(2**(self.bitDepth-1))) #takes the first 2 bytes and interprets as little endian short
        self.t = 0
        self.frequency = 0
        self.gain=1.0
        self.sample=0.0

    def linearInterpolate(self, index):
        integer = int(index)
        remainder = index-integer
        s1 = self.table[integer]
        s2 = self.table[(integer+1)%self.tableSampleRate]
        linear_interpolated_sample = s1*(1-remainder)+s2*(remainder)
        return linear_interpolated_sample

    #gets a sample from a t value in seconds
    def getSample(self, time, frequency):
        time_to_index = (time*self.sampleRate*frequency)%self.sampleRate
        integer = int(time_to_index)
        remainder = time_to_index-integer
        s1 = self.table[integer]
        s2 = self.table[integer+1]
        linear_interpolated_sample = s1*(remainder-1)+s2*(remainder)
        self.frequency = frequency
        self.t = time_to_index
        return linear_interpolated_sample*self.gain

    #get sample from an index index is exterior samples from start
    def getSamplei(self, index, frequency):
        sample_to_time = index/self.outsideSampleRate
        return self.getSample(sample_to_time, frequency)

    def getSample(self):
        sample = self.sample
        return sample*self.gain

    def nextSample(self, frequency = None, prev_index = None):
        if(frequency == None): frequency = self.frequency
        if(prev_index == None): prev_index = self.t
        skip = (frequency*self.tableSampleRate)/self.outsideSampleRate
        new_index = (prev_index+skip)%self.tableSampleRate
        sample = self.linearInterpolate(new_index)
        self.frequency = frequency
        self.t = new_index
        self.sample = sample
        return sample*self.gain

    def setFreq(self, freq):
        self.frequency = freq

    #needs work
    def setPhase(self, phase):
        self.t = phase

    def setGain(self, gain):
        self.gain = gain
