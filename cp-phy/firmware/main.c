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


int main(void)
{
	pb_phy_init(PB_PHY_BAUD_19200);
	raspi_init();

	irq_enable();
	while (1) {
	}
}
