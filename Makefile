#############################################################################
# Makefile for PSEC-4 EVAL exes 
# 2/2012
#############################################################################
#Generic and Site Specific Flags
CC=g++ -g
LDFLAGS=$(LIBS) -lusb
CXXFLAGS=-Wall -O2

INC= -I./usb/

BINS= usb/read-psec4a-register

#############################################################################
OBJS= 	usb/stdUSBl.o 	
#############################################################################
##default: $(MAKE) all

all : $(BINS)

usb/%.o : usb/%.cc
	$(CC) $(INC) -c $< -o $@

usb/stdUSBl.o : usb/stdUSBl.cxx
	$(CC) $(INC) -c $< -o $@

usb/read-psec4a-register : usb/read-psec4a-register.o $(OBJS); $(CC) $^ $(LDFLAGS) -o $@


#############################################################################
clean:
	@ rm -f $(OBJS) *~ *.o 

#############################################################################
