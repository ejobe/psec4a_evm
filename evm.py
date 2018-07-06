import usb.core
import time
import sys
import numpy 
import usb_device as usbdev
import registers as reg
import psec4a

'''EJO 2018.2.1
'''

#--------------------
class EVM:

   ext_dac_ref_voltage = 1.190 #volts
   psec4a_samples = 1056
   psec4a_channels = 8
   psec4a_vertical_bits = 11

   def __init__(self):
      #setup usb stuff
      self.dev = usb.core.find(idVendor=usbdev.VID, idProduct=usbdev.PID)
      if self.dev is None:
         print 'please connect board'
         sys.exit()
      self.dev.set_configuration()
      self.dev.reset()
      
      #initialize PSEC4A stuff
      self.psec4a = psec4a.PSEC4A(self)
      self.mode = 0
      self.getReadoutMode()

      self.pedestals = numpy.zeros((self.psec4a_channels, self.psec4a_samples))

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
         print "register read:", ret
         #for i in range(0,len(ret),-1):
         #   print "word recieved: ", hex((ret[i+1] << 8) | ret[i])

      return (ret[3] << 8) | ret[2]

   def readChannel(self, channel, num_bytes = 2120 ):
      '''read single PSEC4A channel
      '''

      self.writeRegister(reg.map['READ_CHAN'], channel)
      self.dev.write(usbdev.EDPNT_WR, [0x00, 0x00, 0x00, reg.map['READ_DATA_REG']])
      ret = self.dev.read(usbdev.EDPNT_RD, num_bytes)

      offset = 6 #bytes
      length= self.psec4a_samples #channel samples
      data = numpy.bitwise_or(ret[offset:offset+length*2:2], numpy.left_shift(numpy.bitwise_and(ret[offset+1:offset+length*2+1:2], 7) , 8))
      buf = numpy.right_shift(numpy.bitwise_and(ret[offset+1:offset+length*2+1:2], 16), 4) #psec4a readout block no. embedded in data

      return data, buf[0]

   ###########  
   def readEvent(self, pedestal_sub=False):
      '''read full 8 channel event
         returns numpy array
      '''
      data=[]

      #check readout mode to determine number of readout blocks
      if self.mode == 1:
         blocks = 4
         bytes_to_read = 1064 
      else:
         blocks = 8
         bytes_to_read = 2120

      for i in xrange(8):
         ch, buf = self.readChannel(i+1, bytes_to_read)
         data.append(ch)

         for j in xrange(blocks):
            data[i][132*j:132*j+132] = numpy.flip(data[i][132*j:132*j+132], 0)

      if pedestal_sub:
         if self.mode == 1:
            return numpy.array(data) - self.pedestals[:, (int(buf)*self.psec4a_samples/2):((int(buf)+1)*self.psec4a_samples/2)], buf
         else:
            return numpy.array(data) - self.pedestals
      else:
         return numpy.array(data), buf

   ###########
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

   ###########
   def resetReadout(self):
      self.writeRegister(121, 0x1)

   ###########
   def getReadoutMode(self):
      '''readback psec4a mode
      '''
      value = self.readRegister(0x4D)
      self.mode = value
      return value

   ###########
   def setReadoutMode(self, mode):
      '''specify readout mode. 0=readout all samples, 1=ping-pong 528 samples
      '''
      self.writeRegister(0x4D, 0x1 & mode)
      self.mode = self.getReadoutMode()
   
   ###########
   def softwareTrigger(self):
      ''' send software trigger
      '''
      self.writeRegister(reg.map['SW_TRIG'], 0x1)

   ###########
   def setPedestalVoltage(self, volts=0.60):
      '''
      sets dc offset 'pedestal' voltage on psec4a input RF
      external dac is 16 bits
      '''
      value = int(volts / self.ext_dac_ref_voltage * 0xFFFF)
      self.writeRegister(reg.map['PED_VOLTS'], value)

   ###########
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
         
         #if reading out in pingpong mode, need to record data for each block
         if self.mode == 1:
            for i in range(2):
               self.softwareTrigger()
               temp = self.readEvent(pedestal_sub=False)
               pedestals[:, (int(temp[1])*self.psec4a_samples/2):((int(temp[1])+1)*self.psec4a_samples/2)] = \
                                 pedestals[:, (int(temp[1])*self.psec4a_samples/2):((int(temp[1])+1)*self.psec4a_samples/2)] + temp[0]


               #print i, pedestals[:, (int(temp[1])*self.psec4a_samples/2):((int(temp[1])+1)*self.psec4a_samples/2)].shape

         #otherwise, reading out whole window:
         else:
            self.softwareTrigger()

            temp = self.readEvent(pedestal_sub=False)
            pedestals = pedestals + temp[0]
      

      self.pedestals = pedestals / num

      if filename is not None:
         numpy.savetxt(filename, self.pedestals, delimiter='\t')

      return self.pedestals
   
   ###########
   def loadPedestals(self, filename='pedestals.dat'):
      '''load pedestal data from file
      '''
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
         time.sleep(1.5) #let DAC voltage settle
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


   ###########
   def set_default_config(self):
      self.setReadoutMode(1)
      self.psec4a.setXferResetMode(1)
      self.psec4a.setComparatorBias(0x140) #(0x200)
      self.psec4a.setXferBufBias(0x0F0) #(0x120)
      self.psec4a.setRampCurrent(0x230)        #(0x1EF)
      self.psec4a.setRampBufBias(0x110) #(0x150)
      self.psec4a.setXferResetVoltage(0x1f00)
      self.setPedestalVoltage(0.7)

#--------------------
def makeCountToVoltage(infile, outfile=None):
   '''loads in a file generated by EVM.pedestalScan()
      creates interpolated DC count-to-voltage LUT
   '''
   
   try:
      ped_scan = numpy.loadtxt(infile)
   except IOError as e:
      print ('An IOError occured . {}'.format(e.args[-1]))

   psec4a_lut = -1.*numpy.ones((EVM.psec4a_channels*EVM.psec4a_samples, 2**EVM.psec4a_vertical_bits), dtype=float)
   
   for i in range(psec4a_lut.shape[0]):
      for j in range(ped_scan.shape[0]):
         
         val = int(round(ped_scan[j][i+1]))
         psec4a_lut[i, val] = ped_scan[j][0]
         
         if j > 0 and val < 2**EVM.psec4a_vertical_bits:
            slope = (psec4a_lut[i, val] - psec4a_lut[i, last_val]) / (val - last_val)
            psec4a_lut[i, last_val:val] = numpy.array(range(val-last_val))*slope + psec4a_lut[i, last_val]
            
            #print slope, val-last_val, (psec4a_lut[i, val] - psec4a_lut[i, last_val])

         last_val = val 


   if outfile is not None:
      numpy.savetxt(outfile, psec4a_lut)

   return psec4a_lut

#--------------------
if __name__=='__main__':

   dev = EVM()
   dev.identify()
   print 'setting default configuration..'
   dev.set_default_config()
   time.sleep(1)


