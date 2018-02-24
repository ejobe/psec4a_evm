#include <iostream>
#include <fstream>
//#include <stdio.h>
//#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include "stdUSB.h" 

using namespace std;

const int usb_read_buffersize=16;

int read_register(unsigned int reg)
{
  stdUSB usb;

  //write to device
  if(usb.createHandles() != stdUSB::SUCCEED) return -1;
  unsigned int write_data;
  write_data = (0x6D) << 24 | reg;
  usb.sendData(write_data);
  //usb.freeHandles();

  //usleep(100);
  //if(usb.createHandles() != stdUSB::SUCCEED) return -1;

  //readback
  int samples; //num of samples received
  unsigned short buffer[usb_read_buffersize];
  memset(buffer, 0x0, (usb_read_buffersize+2)*sizeof(unsigned short));
  try{
    usb.readData(buffer, usb_read_buffersize+2, &samples);
    cout << "samples read: " << samples << endl;
    for(int i=0;i<usb_read_buffersize; i++){
      cout << buffer[i] << endl;
    }
    usb.freeHandles();
	
  }
  catch(...){
    fprintf(stderr, "Please connect the board. [DEFAULT exception] \n");
    usb.freeHandles();
    return 1;
  }    

  return (int)buffer[0];
  
}


int main(int argc, char **argv){
  if(argc != 2){
    cout << "need to include register number 1-128" << endl;
    return 1;
  }

  read_register(atoi(argv[1]));

  return 0;
}
