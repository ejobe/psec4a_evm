import usb.core
import time
import sys
import numpy 
import config.usb_device as usbdev
import config.registers as reg
import psec4a
import h5py

class EVM:

   def __init__(self):
      self.dev = usb.core.find(idVendor=usbdev.VID, idProduct=usbdev.PID)
      if self.dev is None:
         print 'please connect board'
         sys.exit()
      self.dev.set_configuration()
      self.dev.reset()
      self.psec4a = psec4a.PSEC4A(self)

      self.pedestals = numpy.zeros((8,1056))

   def writeRegister(self, addr, value):
      addr = addr & 0xFF
      ret = self.dev.write(usbdev.EDPNT_WR, [(value & 0xFF), (value & 0xFF00) >> 8,  
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
         for i in range(0,len(ret),-1):
            print "word recieved: ", hex((ret[i+1] << 8) | ret[i])

      return (ret[3] << 8) | ret[2]

   def readChannel(self, channel, num_bytes = 2120 ):
      '''read single PSEC4A channel
      '''
      self.writeRegister(reg.map['READ_CHAN'], channel)
      self.dev.write(usbdev.EDPNT_WR, [0x00, 0x00, 0x00, reg.map['READ_DATA_REG']])
      ret = self.dev.read(usbdev.EDPNT_RD, num_bytes)

      offset = 6 #bytes
      length=1056 #channel samples
      data = numpy.bitwise_or(ret[offset:offset+length*2:2], numpy.left_shift(ret[offset+1:offset+length*2+1:2], 8))

      return data

   def readEvent(self, pedestal_sub=False):
      '''read full 8 channel event
         returns numpy array
      '''
      data=[]
      for i in xrange(8):
         data.append(self.readChannel(i+1))

         for j in xrange(8):
            data[i][132*j:132*j+132] = numpy.flip(data[i][132*j:132*j+132], 0)

      if pedestal_sub:
         return numpy.array(data) - self.pedestals
      else:
         return numpy.array(data)

   def identify(self):
      '''returns board ID info
      '''
      firm_id   = self.readRegister(reg.map['FIRM_VER'])
      firm_date = self.readRegister(reg.map['FIRM_DAY'])
      firm_year = self.readRegister(reg.map['FIRM_YEAR'])
      
      print '*---psec4a evm firmware---*'
      print 'firmware version:', (firm_id & 0xF0 >> 8), '.', firm_id & 0x0F
      print 'firmware date:', firm_year, '/', (firm_date & 0xFF00) >> 8, '/', firm_date & 0xFF
      print 

   def resetReadout(self):
      self.writeRegister(121, 0x1)

   def softwareTrigger(self):
      self.writeRegister(reg.map['SW_TRIG'], 0x1)

   def takePedestals(self, num=100, save=True, filename='pedestals.dat'):
      self.resetReadout()
      pedestals = numpy.zeros((8,1056))
      
      for j in range(num):
         self.softwareTrigger()
         pedestals = pedestals + self.readEvent(pedestal_sub=False)
      
      self.pedestals = pedestals / num
      if save:
         numpy.savetxt(filename, self.pedestals, delimiter='\t')

      return self.pedestals

   def loadPedestals(self, filename='pedestals.dat'):
      self.pedestals = numpy.loadtxt(filename)

if __name__=='__main__':
   dev = EVM()
   dev.identify()
