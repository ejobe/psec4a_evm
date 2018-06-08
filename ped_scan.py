import evm
import numpy
import time
import matplotlib.pyplot as plt

dev=evm.EVM()

#for i in range(300, 801, 100):
#    print i
#    dev.psec4a.setXferBufBias(i)
#    time.sleep(1)
dev.psec4a.setXferResetMode(1)
dev.psec4a.setComparatorBias(0x140) #(0x200)
dev.psec4a.setXferBufBias(0x120) #(0x120)
dev.psec4a.setRampCurrent(0x230)        #(0x1EF)
dev.psec4a.setRampBufBias(0x150)
dev.psec4a.setXferResetVoltage(0x1e00) #0x2c00 seems to be minimum for leakage...if reading out both 528 sample banks
time.sleep(2)

ped, codes = dev.pedestalScan(incr_volts=0.1, filename=None)

#    plt.figure(i)


ch = 5 
plt.figure()
for j in range(528):
    plt.plot(ped, numpy.array(codes)[:,ch,j], 'o--')

plt.figure()
for j in range(528,1056,1):
    plt.plot(ped, numpy.array(codes)[:,ch,j], 'o--')

plt.figure()

plt.plot(ped, numpy.mean(numpy.array(codes)[:,ch,:528], axis=1), 'o--')
plt.plot(ped, numpy.mean(numpy.array(codes)[:,ch,528:], axis=1), 'o--')


plt.show()
