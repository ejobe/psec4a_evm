import config.registers as reg

class PSEC4A:
    
    def __init__(self, dev):
        self.dev = dev  #the eval card usb device
        
    def write(self, addr, value):
        return self.dev.writeRegister(addr, value)

    def read(self, addr):
        return self.dev.readRegister(addr)

    def getRingOscFreq(self):
        '''
        returns count value of ring oscillator divider in 1 sec bin
        '''
        ro_count_lo = self.read(reg.map['RO_COUNT'])
        ro_count_hi = self.read(reg.map['RO_COUNT']+1)
        ro_count = ro_count_hi << 16 | ro_count_lo
        ro_freq_mhz = ro_count * 1. * pow(2,11) / pow(10,6)
        return ro_count, ro_freq_mhz

    def setROVCP(self, value):
        value = value & 0x3FF
        self.write(reg.map['RO_FREQ_DAC'], value)

    def setRampCurrent(self, value):
        value = value & 0x3FF
        self.write(reg.map['RAMP_SLOPE_DAC'], value)

    def setXferBufBias(self, value):
        value = value & 0x3FF
        self.write(reg.map['XFER_BIAS_DAC'], value)  
        
    def setRampBufBias(self, value):
        value = value & 0x3FF
        self.write(reg.map['RAMPBUF_BIAS_DAC'], value)     
    
    def setComparatorBias(self, value):
        value = value & 0x3FF
        self.write(reg.map['COMP_BIAS_DAC'], value)     
