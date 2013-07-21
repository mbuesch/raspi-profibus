# Project name
NAME			:= cp-phy

# Project source files
SRCS			:= checksum.c \
			   main.c \
			   profibus-phy.c \
			   raspi-interface.c

# Project fuse bits
LFUSE			:= 0xB7
HFUSE			:= 0xDD
EFUSE			:= 0x01

# CPU speed, in Hz
F_CPU			:= 18432000

# Architecture configuration
GCC_ARCH		:= atmega88
AVRDUDE_ARCH		:= m88
AVRDUDE_SPEED		:= 1
AVRDUDE_SLOW_SPEED	:= 100

# Programmer selection.
# Values can be:  avrisp2, mysmartusb
PROGRAMMER		:= avrisp2

# Additional compiler flags
CFLAGS			:=
LDFLAGS			:=

# Additional "clean" and "distclean" target files
CLEAN_FILES		:=
DISTCLEAN_FILES		:=


# =============================================================================
# =============================================================================
# =============================================================================


BINEXT			:=
NODEPS			:=

# The toolchain definitions
CC			= avr-gcc$(BINEXT)
OBJCOPY			= avr-objcopy$(BINEXT)
OBJDUMP			= avr-objdump$(BINEXT)
SIZE			= avr-size$(BINEXT)
MKDIR			= mkdir$(BINEXT)
MV			= mv$(BINEXT)
RM			= rm$(BINEXT)
CP			= cp$(BINEXT)
ECHO			= echo$(BINEXT)
GREP			= grep$(BINEXT)
TRUE			= true$(BINEXT)
TEST			= test$(BINEXT)
AVRDUDE			= avrdude$(BINEXT)
MYSMARTUSB		= mysmartusb.py
DOXYGEN			= doxygen$(BINEXT)

V			:= @		# Verbose build:  make V=1
O			:= s		# Optimize flag
Q			:= $(V:1=)
QUIET_CC		= $(Q:@=@$(ECHO) '     CC       '$@;)$(CC)
QUIET_DEPEND		= $(Q:@=@$(ECHO) '     DEPEND   '$@;)$(CC)
QUIET_OBJCOPY		= $(Q:@=@$(ECHO) '     OBJCOPY  '$@;)$(OBJCOPY)
QUIET_SIZE		= $(Q:@=@$(ECHO) '     SIZE     '$@;)$(SIZE)

CFLAGS			+= -mmcu=$(GCC_ARCH) -std=c99 -g -O$(O) -Wall \
			  "-Dinline=inline __attribute__((__always_inline__))" \
			  -fshort-enums -DF_CPU=$(F_CPU)

BIN			:= $(NAME).bin
HEX			:= $(NAME).hex
EEP			:= $(NAME).eep.hex

.SUFFIXES:
.DEFAULT_GOAL := all

# Programmer parameters
ifeq ($(PROGRAMMER),mysmartusb)
AVRDUDE_PROGRAMMER	:= avr910
PROGPORT		:= /dev/ttyUSB0
endif
ifeq ($(PROGRAMMER),avrisp2)
AVRDUDE_PROGRAMMER	:= avrisp2
PROGPORT		:= usb
endif

ifeq ($(AVRDUDE_PROGRAMMER),)
$(error Invalid PROGRAMMER specified)
endif

# MySmartUSB helpers
MYSMARTUSB_PWRCYCLE := \
	$(if $(filter mysmartusb,$(PROGRAMMER)), \
		$(MYSMARTUSB) -p0 $(PROGPORT) && \
		sleep 1 && \
		$(MYSMARTUSB) -p1 $(PROGPORT) \
	)

MYSMARTUSB_PROGMODE := \
	$(if $(filter mysmartusb,$(PROGRAMMER)), \
		$(MYSMARTUSB) -mp $(PROGPORT) \
	)

MYSMARTUSB_DATAMODE := \
	$(if $(filter mysmartusb,$(PROGRAMMER)), \
		$(MYSMARTUSB) -md $(PROGPORT) \
	)

DEPS = $(sort $(patsubst %.c,dep/%.d,$(1)))
OBJS = $(sort $(patsubst %.c,obj/%.o,$(1)))

# Generate dependencies
$(call DEPS,$(SRCS)): dep/%.d: %.c 
	@$(MKDIR) -p $(dir $@)
	@$(MKDIR) -p obj
	$(QUIET_DEPEND) -o $@.tmp -MM -MT "$@ $(patsubst dep/%.d,obj/%.o,$@)" $(CFLAGS) $<
	@$(MV) -f $@.tmp $@

ifeq ($(NODEPS),)
-include $(call DEPS,$(SRCS))
endif

# Generate object files
$(call OBJS,$(SRCS)): obj/%.o: %.c
	@$(MKDIR) -p $(dir $@)
	$(QUIET_CC) -o $@ -c $(CFLAGS) $<

all: $(HEX)

%.s: %.c
	$(QUIET_CC) $(CFLAGS) -S -o $@ $<

%.e: %.c
	$(QUIET_CC) $(CFLAGS) -E -o $@ $<

$(BIN): $(call OBJS,$(SRCS))
	$(QUIET_CC) $(CFLAGS) -o $(BIN) $(call OBJS,$(SRCS)) $(LDFLAGS) $(LDFLAGS)

$(HEX): $(BIN)
	$(QUIET_OBJCOPY) -R.eeprom -O ihex $(BIN) $(HEX)
	@$(if $(filter .exe,$(BINEXT)),$(TRUE), \
	$(OBJDUMP) -h $(BIN) | $(GREP) -qe .eeprom && \
	 $(OBJCOPY) -j.eeprom --set-section-flags=.eeprom="alloc,load" \
	 --change-section-lma .eeprom=0 -O ihex $(BIN) $(EEP) \
	 || $(TRUE))
	$(QUIET_SIZE) $(BIN)

avrdude:
	$(call MYSMARTUSB_PROGMODE)
	$(AVRDUDE) -B $(AVRDUDE_SPEED) -p $(AVRDUDE_ARCH) \
	 -c $(AVRDUDE_PROGRAMMER) -P $(PROGPORT) -t
	$(call MYSMARTUSB_PWRCYCLE)
	$(call MYSMARTUSB_DATAMODE)

install_eeprom: all
	$(TEST) -r $(EEP) && ( \
	 $(call MYSMARTUSB_PROGMODE) \
	 $(AVRDUDE) -B $(AVRDUDE_SPEED) -p $(AVRDUDE_ARCH) \
	  -c $(AVRDUDE_PROGRAMMER) -P $(PROGPORT) \
	  -U eeprom:w:$(EEP) \
	) || $(TRUE)

install_flash: install_eeprom
	$(call MYSMARTUSB_PROGMODE)
	$(AVRDUDE) -B $(AVRDUDE_SPEED) -p $(AVRDUDE_ARCH) \
	 -c $(AVRDUDE_PROGRAMMER) -P $(PROGPORT) \
	 -U flash:w:$(HEX)

install: install_flash
	$(call MYSMARTUSB_PWRCYCLE)
	$(call MYSMARTUSB_DATAMODE)

reset:
	$(call MYSMARTUSB_PROGMODE)
	$(AVRDUDE) -B $(AVRDUDE_SPEED) -p $(AVRDUDE_ARCH) \
	 -c $(AVRDUDE_PROGRAMMER) -P $(PROGPORT) \
	 -U signature:r:/dev/null:i -q -q
	$(call MYSMARTUSB_PWRCYCLE)

writefuse:
	$(call MYSMARTUSB_PROGMODE)
	$(AVRDUDE) -B $(AVRDUDE_SLOW_SPEED) -p $(AVRDUDE_ARCH) \
	 -c $(AVRDUDE_PROGRAMMER) -P $(PROGPORT) -q -q \
	 -U lfuse:w:$(LFUSE):m \
	 -U hfuse:w:$(HFUSE):m \
	 $(if $(EFUSE),-U efuse:w:$(EFUSE):m)
	$(call MYSMARTUSB_PWRCYCLE)
	$(call MYSMARTUSB_DATAMODE)

doxygen:
	$(DOXYGEN) Doxyfile

clean:
	-$(RM) -rf obj dep $(BIN) $(CLEAN_FILES)

distclean: clean
	-$(RM) -f $(HEX) $(EEP) $(DISTCLEAN_FILES)
	-$(RM) -f $(if $(filter .exe,$(BINEXT)),$(patsubst %.c,%.s,$(SRCS)),*.s)
