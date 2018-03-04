#############################################################################
# Makefile for PSEC-4 EVAL exes 
# 2/2012
#############################################################################
#Generic and Site Specific Flags
CC=g++ -g
LDFLAGS=$(LIBS) -lusb
CXXFLAGS=-Wall -O2

INC= -I./usb-cpp/

BINS= usb-cpp/read-psec4a-register

#############################################################################
OBJS= 	usb-cpp/stdUSBl.o 	
#############################################################################
##default: $(MAKE) all

all : $(BINS)

usb/%.o : usb-cpp/%.cc
	$(CC) $(INC) -c $< -o $@

usb/stdUSBl.o : usb-cpp/stdUSBl.cxx
	$(CC) $(INC) -c $< -o $@

usb/read-psec4a-register : usb/read-psec4a-register.o $(OBJS); $(CC) $^ $(LDFLAGS) -o $@


#############################################################################
clean:
	@ rm -f $(OBJS) *~ *.o 

#############################################################################
