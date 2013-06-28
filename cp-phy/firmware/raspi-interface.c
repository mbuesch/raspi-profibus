/*
 * PROFIBUS DP - Raspberry Pi SPI interface
 *
 * Copyright (c) 2013 Michael Buesch <m@bues.ch>
 *
 * Licensed under the terms of the GNU General Public License version 2,
 * or (at your option) any later version.
 */

#include "raspi-interface.h"
#include "profibus-phy.h"
#include "checksum.h"

#include <string.h>

#include <avr/io.h>
#include <avr/interrupt.h>


/* Interrupt pin */
#define RASPI_IRQ_DDR		DDRB
#define RASPI_IRQ_PORT		PORTB
#define RASPI_IRQ_BIT		1


struct raspi_context {
	struct raspi_packet rx_packet;
	uint16_t rx_byte_ptr;
	bool rx_blocked;

	struct raspi_packet tx_packet;
	uint16_t tx_byte_ptr;
	uint16_t tx_packet_size;
};

static struct raspi_context raspi;


static void raspi_context_reset(void)
{
	memset(&raspi.rx_packet, 0, sizeof(raspi.rx_packet));
	raspi.rx_byte_ptr = 0;
	raspi.rx_blocked = 0;

	memset(&raspi.tx_packet, 0, sizeof(raspi.tx_packet));
	raspi.tx_byte_ptr = 0;
	raspi.tx_packet_size = 0;
}

static inline void raspi_irq_set(void)
{
	mb();
	RASPI_IRQ_PORT |= (1 << RASPI_IRQ_BIT);
	mb();
}

static inline void raspi_irq_clear(void)
{
	mb();
	RASPI_IRQ_PORT &= ~(1 << RASPI_IRQ_BIT);
	mb();
}

static uint8_t calculate_fcs(const struct raspi_packet *p)
{
	uint8_t sum = 0;

	sum = simple_byte_add_checksum(sum, p, RASPI_PACK_HDR_LEN - 1);
	sum = simple_byte_add_checksum(sum, p->raw_payload, p->pl_size);

	return sum ^ 0xFF;
}

static bool check_fcs(const struct raspi_packet *p)
{
	uint8_t fcs;

	if (p->fc == RPI_PACK_NOP)
		return 1;

	fcs = calculate_fcs(p);
	if (fcs != p->fcs) {
		/* Checksum mismatch */
		return 0;
	}

	return 1;
}

static void queue_ack(void)
{
	raspi.tx_packet_size = RASPI_PACK_HDR_LEN;
	raspi.tx_packet.fc = RPI_PACK_ACK;
	raspi.tx_packet.pl_size = 0;
	raspi.tx_packet.fcs = calculate_fcs(&raspi.tx_packet);
	raspi_irq_set();
}

static void queue_nack(void)
{
	raspi.tx_packet_size = RASPI_PACK_HDR_LEN;
	raspi.tx_packet.fc = RPI_PACK_NACK;
	raspi.tx_packet.pl_size = 0;
	raspi.tx_packet.fcs = calculate_fcs(&raspi.tx_packet);
	raspi_irq_set();
}

static void handle_rx(void)
{
	int8_t err;

	if (!check_fcs(&raspi.rx_packet))
		goto error_nack;

	switch (raspi.rx_packet.fc) {
	case RPI_PACK_NOP:
	case RPI_PACK_PB_SRD_REPLY:
	case RPI_PACK_ACK:
	case RPI_PACK_NACK:
		break;
	case RPI_PACK_RESET:
		pb_reset();
		raspi_context_reset();
		queue_ack();
		break;
	case RPI_PACK_SETCFG:
		if (raspi.rx_packet.pl_size < sizeof(raspi.rx_packet.config))
			goto error_nack;
		if (raspi.rx_packet.config.baudrate != pb_get_baudrate()) {
			err = pb_phy_init(raspi.rx_packet.config.baudrate);
			if (err)
				goto error_nack;
		}
		pb_set_rx_timeout(raspi.rx_packet.config.rx_timeout_ms);
		queue_ack();
		break;
	case RPI_PACK_PB_SRD:
		/* Send the profibus telegram. */
		err = pb_srd(&raspi.rx_packet.pb_telegram,
			     &raspi.tx_packet.pb_telegram);
		if (err) {
			queue_nack();
			return;
		}
		raspi.rx_blocked = 1;
		break;
	case RPI_PACK_PB_SDN:
		/* Send the profibus telegram. */
		err = pb_sdn(&raspi.rx_packet.pb_telegram);
		if (err) {
			queue_nack();
			return;
		}
		raspi.rx_blocked = 1;
		break;
	}

	return;

error_nack:
	queue_nack();
}

ISR(SPI_STC_vect)
{
	uint8_t *p;
	uint8_t data;

	data = SPDR;

	raspi_irq_clear();

	/* Handle RX byte */
	if (!raspi.rx_blocked) {
		if (raspi.rx_byte_ptr == 0 &&
		    data == RPI_PACK_NOP) {
			/* No operation. Don't store the byte. */
		} else {
			/* Store the byte. */
			p = (uint8_t *)&raspi.rx_packet;
			p[raspi.rx_byte_ptr] = data;
			raspi.rx_byte_ptr++;

			if (raspi.rx_byte_ptr >= RASPI_PACK_HDR_LEN &&
			    raspi.rx_byte_ptr - RASPI_PACK_HDR_LEN == raspi.rx_packet.pl_size) {
				/* Handle received packet. */
				handle_rx();
				raspi.rx_byte_ptr = 0;
			}
		}
	}

	/* Handle TX byte */
	data = 0;
	if (raspi.tx_packet_size) {
		p = (uint8_t *)&raspi.tx_packet;
		data = p[raspi.tx_byte_ptr];
		raspi.tx_byte_ptr++;
		if (raspi.tx_byte_ptr >= raspi.tx_packet_size) {
			/* All bytes sent. */
			raspi.tx_packet_size = 0;
		}
	}

	SPDR = data;
}

static void profibus_event(enum pb_event event, uint8_t value)
{
	switch (event) {
	case PB_EV_SDN_COMPLETE:
		raspi.rx_blocked = 0;
		queue_ack();
		break;
	case PB_EV_SRD_SENT:
		raspi.rx_blocked = 0;
		break;
	case PB_EV_SRD_COMPLETE:
		raspi.tx_packet_size = (uint16_t)value + RASPI_PACK_HDR_LEN;
		raspi.tx_packet.fc = RPI_PACK_PB_SRD_REPLY;
		raspi.tx_packet.pl_size = value;
		raspi.tx_packet.fcs = calculate_fcs(&raspi.tx_packet);
		raspi_irq_set();
		break;
	case PB_EV_SRD_ERROR:
		queue_nack();
		break;
	}
}

void raspi_init(void)
{
	memset(&raspi, 0, sizeof(raspi));

	/* Register Profibus event handler. */
	pb_set_notifier(profibus_event);

	/* SPI slave mode 0 with IRQ enabled. */
	DDRB |= (1 << 4/*MISO*/);
	DDRB &= ~((1 << 5/*SCK*/) | (1 << 3/*MOSI*/) | (1 << 2/*SS*/));

	/* Initialize IRQ line. */
	RASPI_IRQ_DDR |= (1 << RASPI_IRQ_BIT);
	raspi_irq_clear();

	/* Enable the SPI transceiver. */
	SPCR = (1 << SPE) | (1 << SPIE) | (0 << CPOL) | (0 << CPHA);
	(void)SPSR; /* clear state */
	(void)SPDR; /* clear state */
}
