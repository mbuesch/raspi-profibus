#ifndef CHECKSUM_H_
#define CHECKSUM_H_

#include <stdint.h>


uint8_t simple_byte_add_checksum(uint8_t sum,
				 const void *buf,
				 unsigned int size);

#endif /* CHECKSUM_H_ */
