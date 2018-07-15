import evm
import numpy
import h5py
import sys
import time

def data_logger(nevents, sw_trig=True, outfile=None, ped_subtract=False):
    
    nevents = int(nevents)

    dev = evm.EVM()
    dev.loadPedestals()

    data=[]
    buf=[]

    for i in range(nevents):

        if sw_trig:
            dev.softwareTrigger()
            
        time.sleep(0.05) #limit rate

        temp = dev.readEvent(ped_subtract)

        data.append(temp[0])
        buf.append(temp[1])            

        if (i+1)%10==0:
            sys.stdout.write('logging event...{:}\r'.format(i+1))
            sys.stdout.flush()
        
    
    if outfile is not None:
        
        f = h5py.File(outfile+'.hd5', 'w')

        _data = f.create_dataset("data", (nevents, 8, 528), dtype='i', data=numpy.array(data), compression="gzip")
        _block=f.create_dataset("block", (nevents,), dtype='i', data=numpy.array(buf))
        _ped = f.create_dataset("ped", (8, 1056), dtype='i', data=dev.pedestals)

    print

    return data


if __name__=='__main__':

    import matplotlib.pyplot as plt

    data = data_logger(100, outfile='test', ped_subtract=True)
    
    ch_to_plot = 5
    for i in range(100):
        plt.figure(1)
        plt.plot(data[i][ch_to_plot])
    plt.show()
