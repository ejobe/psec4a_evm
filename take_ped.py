import evm
import matplotlib.pyplot as plt
import time

dev=evm.EVM()
dev.setPedestalVoltage(0.7)
time.sleep(1)
ped = dev.takePedestals()


for i in range(8):
    plt.plot(ped[i])
plt.show()
