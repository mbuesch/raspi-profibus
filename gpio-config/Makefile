# The toolchain definitions
CC		= gcc
INSTALL		= install

V		= @		# Verbose build:  make V=1
C		= 0		# Sparsechecker build:  make C=1
Q		= $(V:1=)
QUIET_CC	= $(Q:@=@echo '     CC       '$@;)$(CC)
QUIET_DEPEND	= $(Q:@=@echo '     DEPEND   '$@;)$(CC)

PREFIX		?= /usr/local
CFLAGS		= -O2 -Wall -std=c99 -D_GNU_SOURCE -pedantic
LDFLAGS		=

SRCS		= main.c
BIN		= cp-phy-gpiosetup

.SUFFIXES:
.PHONY: all install clean distclean
.DEFAULT_GOAL := all

DEPS = $(sort $(patsubst %.c,dep/%.d,$(1)))
OBJS = $(sort $(patsubst %.c,obj/%.o,$(1)))

# Generate dependencies
$(call DEPS,$(SRCS)): dep/%.d: %.c 
	@mkdir -p $(dir $@)
	$(QUIET_DEPEND) -o $@.tmp -MM -MT "$@ $(patsubst dep/%.d,obj/%.o,$@)" $(CFLAGS) $< && mv -f $@.tmp $@

-include $(call DEPS,$(SRCS))

# Generate object files
$(call OBJS,$(SRCS)): obj/%.o:
	@mkdir -p $(dir $@)
	$(QUIET_CC) -o $@ -c $(CFLAGS) $<

all: $(BIN)

$(BIN): $(call OBJS,$(SRCS))
	$(QUIET_CC) $(CFLAGS) -o $(BIN) $(call OBJS,$(SRCS)) $(LDFLAGS)

install: all
	$(INSTALL) -g 0 -o 0 -m 0755 -t $(PREFIX)/bin/ $(BIN)

clean:
	-rm -Rf *~ obj dep

distclean: clean
	-rm -f $(BIN)
