/*
 * Checksum helper functions
 *
 * Copyright (c) 2013 Michael Buesch <m@bues.ch>
 *
 * Licensed under the terms of the GNU General Public License version 2,
 * or (at your option) any later version.
 */

#include "checksum.h"


uint8_t simple_byte_add_checksum(uint8_t sum,
				 const void *buf,
				 unsigned int size)
{
	const uint8_t *p = buf;

	for ( ; size; size--, p++)
		sum += *p;

	return sum;
}
