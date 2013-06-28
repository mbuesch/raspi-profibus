#ifndef RASPI_INTERFACE_H_
#define RASPI_INTERFACE_H_

#include "util.h"
#include "profibus-phy.h"

#include <stdint.h>


enum raspi_packet_fc {
	RPI_PACK_NOP,		/* No operation */
	RPI_PACK_RESET,		/* Reset */
	RPI_PACK_SETCFG,	/* Set config */
	RPI_PACK_PB_SRD,	/* Profibus SRD request */
	RPI_PACK_PB_SRD_REPLY,	/* Profibus SRD reply */
	RPI_PACK_PB_SDN,	/* Profibus SDN request */
	RPI_PACK_ACK,		/* Short ACK */
	RPI_PACK_NACK,		/* Short NACK */
};

#define RASPI_PACK_HDR_LEN	3

struct raspi_packet {
	uint8_t fc;		/* Frame control */
	uint8_t pl_size;	/* Payload size */
	uint8_t fcs;		/* Frame check sequence */

	/* Payload */
	union {
		/* Profibus telegram */
		struct pb_telegram pb_telegram;

		/* PHY configuration */
		struct config {
			uint8_t baudrate;	/* enum pb_phy_baud */
			uint8_t rx_timeout_ms;
			uint8_t biterror_checks;
		} _packed config;

		uint8_t raw_payload[255];
	} _packed;
} _packed;

void raspi_init(void);

#endif /* RASPI_INTERFACE_H_ */
