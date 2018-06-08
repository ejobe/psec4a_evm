import evm
import time
import matplotlib.pyplot as plt

dev=evm.EVM()
#dev.psec4a.setXferResetMode(1)
#dev.psec4a.setComparatorBias(0x240)
#dev.psec4a.setXferBufBias(0x0A0)
#dev.psec4a.setRampCurrent(0x1CF)
#dev.psec4a.setXferResetVoltage(0x2C00)

time.sleep(2)

dev.loadPedestals()

#dev.setPedestalVoltage(0.6)
time.sleep(1)
dev.softwareTrigger()

now=time.time()
ret=dev.readEvent(pedestal_sub=True)
print time.time()-now

for i in range(8):
    plt.plot(ret[i] - i * 0, 'o--', ms=1, lw=0.5)
plt.grid(True)
plt.show()

'''
now = time.time()
pedestals = dev.takePedestals(100)
print time.time()-now
#time.sleep(1)
#pedestals2 = dev.takePedestals(100)

for i in range(8):
    plt.plot(pedestals[i])
plt.show()
'''

