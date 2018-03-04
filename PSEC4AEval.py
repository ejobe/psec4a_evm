import usb.core
import time
import config.usb_device as usbdev
import config.registers as reg

class PSEC4AEval:

   def __init__(self):
      self.dev = usb.core.find(idVendor=usbdev.VID, idProduct=usbdev.PID)
      self.dev.set_configuration()
      self.dev.reset()


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


   def identify(self):
      '''
      returns board ID info
      '''
      firm_id   = self.readRegister(reg.map['FIRM_VER'])
      firm_date = self.readRegister(reg.map['FIRM_DAY'])
      firm_year = self.readRegister(reg.map['FIRM_YEAR'])
      
      print '*---psec4a firmware id---*'
      print 'firmware version:', (firm_id & 0xF0 >> 8), '.', firm_id & 0x0F
      print 'firmware date:', firm_year, '/', (firm_date & 0xFF00) >> 8, '/', firm_date & 0xFF
      print 

