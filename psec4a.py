import evm
import config.registers as reg

dev = evm.EVM()

class PSEC4A:
    
    def __init__(self, dev=dev):
        self.dev = dev  #the eval card usb device
        
    def write(self, addr, value):
        return self.dev.writeRegister(addr, value)

    def read(self, addr):
        return self.dev.readRegister(addr)

    def getRingOscFreq(self):
        '''
        returns count value of ring oscillator divider in 1 sec bin
        '''
        ro_count = self.read(reg.map['RO_COUNT'])
        ro_freq_mhz = ro_count * 10. * pow(2,11) / pow(10,6)
        return ro_count, ro_freq_mhz

    def setROVCP(self, value):
        value = value & 0x3FF
        self.write(86, value)

        
        
