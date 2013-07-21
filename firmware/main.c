/*
 * PROFIBUS DP - Communication Processor PHY firmware
 *
 * Copyright (c) 2013 Michael Buesch <m@bues.ch>
 *
 * Licensed under the terms of the GNU General Public License version 2,
 * or (at your option) any later version.
 */

#include "profibus-phy.h"
#include "raspi-interface.h"
#include "util.h"

#include <avr/io.h>
#include <avr/interrupt.h>


/* 1000 Hz tick */
ISR(TIMER1_COMPA_vect)
{
	pb_ms_tick();
}

static void systemtimer_init(void)
{
	/* Initialize system timer to 1000 Hz */
	TCCR1A = 0;
	TCCR1B = (1 << WGM12) | (1 << CS12); /* CTC / PS 256 */
	TCCR1C = 0;
	TCNT1 = 0;
	OCR1A = 72;
	TIFR1 = (1 << OCF1A);
	TIMSK1 |= (1 << OCIE1A);
}

int main(void)
{
	pb_phy_init();
	raspi_init();
	systemtimer_init();

	irq_enable();
	while (1) {
	}
}
