import usb.core
import time
import sys
import numpy 
import usb_device as usbdev
import registers as reg
import psec4a

class EVM:

   ext_dac_ref_voltage = 1.190 #volts
   psec4a_samples = 1056
   psec4a_channels = 8

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
      '''write firmware register: 32 bits
      '''
      addr = addr & 0xFF
      ret = self.dev.write(usbdev.EDPNT_WR, [(value & 0xFF), (value & 0xFF00) >> 8,  
                                             (value & 0xFF0000) >> 16, addr])
      return ret

   def readRegister(self, reg_addr, num_bytes=8, debug=False):
      '''read psec4a evm register
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
      length= self.psec4a_samples #channel samples
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

   def setPedestalVoltage(self, volts=0.60):
      '''
      sets dc offset 'pedestal' voltage on psec4a input RF
      external dac is 16 bits
      '''
      value = int(volts / self.ext_dac_ref_voltage * 0xFFFF)
      self.writeRegister(reg.map['PED_VOLTS'], value)

   def readPedestalVoltage(self):
      '''read value of pedestal voltage register
      '''
      value = self.readRegister(reg.map['PED_VOLTS'])
      volts = float(value) / 0xFFFF * self.ext_dac_ref_voltage
      return volts


   ###########
   def takePedestals(self, num=100, filename='pedestals.dat'):
      '''get pedestal offset values for each storage cell
      '''
      self.resetReadout()
      pedestals = numpy.zeros((self.psec4a_channels,self.psec4a_samples))
      
      for j in range(num):
         self.softwareTrigger()
         pedestals = pedestals + self.readEvent(pedestal_sub=False)
      
      self.pedestals = pedestals / num

      if filename is not None:
         numpy.savetxt(filename, self.pedestals, delimiter='\t')

      return self.pedestals

   def loadPedestals(self, filename='pedestals.dat'):
      self.pedestals = numpy.loadtxt(filename)


   ###########
   def pedestalScan(self, start_volts=0.00, stop_volts=1.20, incr_volts=0.05, filename='pedscan.dat'):
      '''performs a dc pedestal scan for each storage cell
      '''
      ped_voltages = numpy.arange(start_volts, stop_volts, incr_volts)

      out_array = numpy.zeros((len(ped_voltages), self.psec4a_channels * self.psec4a_samples + 1))
      scan_values=[]

      for i, ped_voltage in enumerate(ped_voltages):

         self.setPedestalVoltage(ped_voltage)
         time.sleep(1.5)
         set_voltage = self.readPedestalVoltage()
         
         sys.stdout.write('pedestal voltage is.....{:.2f} V\r'.format(set_voltage))
         sys.stdout.flush()

         pedestals = self.takePedestals(filename=None)
         
         out_array[i,0] = set_voltage
         out_array[i,1:] = pedestals.flatten()

         scan_values.append(pedestals)

      sys.stdout.write('\n')
         
      if filename is not None:
         numpy.savetxt(filename, out_array)
         
      return ped_voltages, scan_values


if __name__=='__main__':
   dev = EVM()
   dev.identify()


