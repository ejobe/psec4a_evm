import usb.core
import time
import numpy 
import config.usb_device as usbdev
import config.registers as reg
import psec4a

class EVM:

   def __init__(self):
      self.dev = usb.core.find(idVendor=usbdev.VID, idProduct=usbdev.PID)
      self.dev.set_configuration()
      self.dev.reset()
      self.psec4a = psec4a.PSEC4A(self)

   def writeRegister(self, addr, value):
      addr = addr & 0xFF
      ret =self.dev.write(usbdev.EDPNT_WR, [(value & 0xFF), (value & 0xFF00) >> 8,  
                                            (value & 0xFF0000) >> 16, addr])
      return ret

   def readRegister(self, reg_addr, num_bytes=8, debug=False):
      '''
      read psec4a evm register
      num_bytes needs to be even. 
      '''

      reg_addr = reg_addr & 0xFF
      self.dev.write(usbdev.EDPNT_WR, [reg_addr, 0x00, 0x00, reg.map['READ_REG']])
      ret = self.dev.read(usbdev.EDPNT_RD, num_bytes)

      if debug:
         print "register read:"
         for i in range(0,len(ret),2):
            print "word recieved: ", hex((ret[i+1] << 8) | ret[i])

      return (ret[3] << 8) | ret[2]

   def readData(self, channel, num_bytes = 2120 ):
      
      self.writeRegister(reg.map['READ_CHAN'], channel)
      self.dev.write(usbdev.EDPNT_WR, [0x00, 0x00, 0x00, reg.map['READ_DATA_REG']])
      ret = self.dev.read(usbdev.EDPNT_RD, num_bytes)

      offset = 4 #bytes
      length=1056 #channel samples
      data = numpy.bitwise_or(ret[offset:offset+length*2:2], numpy.left_shift(ret[offset+1:offset+length*2+1:2], 8))
      return data


   def identify(self):
      '''returns board ID info
      '''
      firm_id   = self.readRegister(reg.map['FIRM_VER'])
      firm_date = self.readRegister(reg.map['FIRM_DAY'])
      firm_year = self.readRegister(reg.map['FIRM_YEAR'])
      
      print '*---psec4a firmware id---*'
      print 'firmware version:', (firm_id & 0xF0 >> 8), '.', firm_id & 0x0F
      print 'firmware date:', firm_year, '/', (firm_date & 0xFF00) >> 8, '/', firm_date & 0xFF
      print 

   def softwareTrigger(self):
      self.writeRegister(reg.map['SW_TRIG'], 0x1)

   def fifoReset(self):
      self.writeRegister(121,0x01)

   def readDataWord(self, channel):
      self.writeRegister(reg.map['READ_CHAN'], channel)
      self.writeRegister(122, 0x1)
      word = self.readRegister(0x8)
      return word


if __name__=='__main__':
   dev = EVM()
   dev.identify()
