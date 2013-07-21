#ifndef UTIL_H_
#define UTIL_H_

#ifndef F_CPU
# error "F_CPU not defined"
#endif
#include <util/delay.h>

#include <stdint.h>
#include <avr/interrupt.h>
#include <avr/pgmspace.h>
#include <avr/cpufunc.h>


#define _min(a, b)	((a) < (b) ? (a) : (b))

#define min(a, b)	({			\
		__typeof__(a) __a = (a);	\
		__typeof__(b) __b = (b);	\
		_min(__a, __b);			\
	})

#define _max(a, b)	((a) > (b) ? (a) : (b))

#define max(a, b)	({			\
		__typeof__(a) __a = (a);	\
		__typeof__(b) __b = (b);	\
		_max(__a, __b);			\
	})

#define clamp(value, min_val, max_val)		\
	max(min(value, max_val), min_val)

#define _generic_abs(val)	((val) >= 0 ? (val) : -(val))

#define generic_abs(val)	({		\
		__typeof__(val) __val = (val);	\
		_generic_abs(__val);		\
	})

#define ARRAY_SIZE(x)		(sizeof(x) / sizeof((x)[0]))

/* Progmem pointer annotation. */
#define PROGPTR			/* progmem pointer */

#define mb()			__asm__ __volatile__("" : : : "memory")


#define noinline        __attribute__((__noinline__))
#define _packed		__attribute__((__packed__))


typedef _Bool		bool;


static inline void irq_disable(void)
{
	cli();
	mb();
}

static inline void irq_enable(void)
{
	mb();
	sei();
}

static inline uint8_t irq_disable_save(void)
{
	uint8_t sreg = SREG;
	cli();
	mb();
	return sreg;
}

static inline void irq_restore(uint8_t sreg_flags)
{
	mb();
	SREG = sreg_flags;
}

static inline bool __irqs_enabled(uint8_t sreg_flags)
{
	return !!(sreg_flags & (1 << SREG_I));
}

static inline bool irqs_enabled(void)
{
	return __irqs_enabled(SREG);
}

#endif /* UTIL_H_ */
