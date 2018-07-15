import numpy
import h5py
import sys
import matplotlib.pyplot as plt

if __name__=='__main__':

    if len(sys.argv) != 3:
        print 'two arguments: filename and event no.'
        sys.exit()
    
    filename = sys.argv[1]
    event = int(sys.argv[2])

    
    try:
        h5_file = h5py.File(filename, 'r')
    except IOError:
        print 'file not found'


    #get data / pedestals
    data = numpy.array(h5_file.get('data'))
    pedstals = numpy.array(h5_file.get('ped'))
    block = numpy.array(h5_file.get('block'))
    
    #plot data:
    fig, ax = plt.subplots(8,1, sharex=True, figsize=(8,10))

    #scale = (numpy.min(data[event,:,:]), numpy.max(data[event,:,:]))

    for i in range(8):
        #assume pedestals already subtracted
        ax[i].plot(data[event,i,:], 'o--', lw=1, ms=2, c='black')

        scale = (numpy.min(data[event,i,:]), numpy.max(data[event,i,:]))

        ax[i].set_ylim([scale[0]-100, scale[1]+100])
        #ax[i].set_ylim([-800, 800])

    plt.show()
