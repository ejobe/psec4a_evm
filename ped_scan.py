import evm
import numpy
import time
import matplotlib.pyplot as plt

dev=evm.EVM()
time.sleep(2)
ped, codes = dev.pedestalScan(incr_volts=0.1, filename='test.dat')


ch = 1
for ch in range(2):

    for j in range(528):
        plt.figure(1)
        plt.plot(ped, numpy.array(codes)[:,ch,j], 'o--')

    for j in range(528,1056,1):
        plt.figure(2)
        plt.plot(ped, numpy.array(codes)[:,ch,j], 'o--')

for ch in range(8):
    plt.figure(4)
    plt.plot(ped, numpy.mean(numpy.array(codes)[:,ch,:528], axis=1), 'o--')
    plt.plot(ped, numpy.mean(numpy.array(codes)[:,ch,528:], axis=1), 'o--')


plt.show()
