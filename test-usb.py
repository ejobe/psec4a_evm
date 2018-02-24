import usb.core
import time

dev=usb.core.find(idVendor=0x6672, idProduct=0x2920)
dev.set_configuration()

ret=dev.write(0x02, [0x01, 0x00, 0x00, 0x6D])
print ret
ret=dev.read(0x86, 8)
#ret=dev.read(0x86, 8)

print ret

dev.reset()

