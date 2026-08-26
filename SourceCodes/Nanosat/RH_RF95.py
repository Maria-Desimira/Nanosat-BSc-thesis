import time

from RHUartDriver import RHUartDriver
from constants import *


class RH_RF95(RHUartDriver):

    def __init__(self,
                 port="/dev/ttyAMA3",
                 baudrate=57600,
                 timeout=1,
                 debug=False):

        super().__init__(port, baudrate, timeout, debug)

        self._mode = 0
        self._rxBufValid = False
        self._buf = bytearray(RH_RF95_FIFO_SIZE)
        self._bufLen = 0
        self._lastRssi = 0
        self._txHeaderTo = 0xFF
        self._txHeaderFrom = 0xFF
        self._txHeaderId = 0
        self._txHeaderFlags = 0
        self._thisAddress = 0xFF
        self._promiscuous = False
        self._rxGood = 0
        self._rxBad = 0
        self._txGood = 0

    def init(self):

        # LoRa + Sleep
        self.write(
            REG_OP_MODE,
            MODE_SLEEP | LONG_RANGE_MODE
        )

        time.sleep(0.01)

        value = self.read(REG_OP_MODE)

        if value != (MODE_SLEEP | LONG_RANGE_MODE):

            raise RuntimeError(
                f"LoRa init failed. REG_OP_MODE = 0x{value:02X}"
            )

        # FIFO
        self.write(REG_FIFO_TX_BASE_ADDR, 0)

        self.write(REG_FIFO_RX_BASE_ADDR, 0)

        # Standby
        self.setModeIdle()

        # Default modem
        self.setModemConfig(0)

        self.setPreambleLength(8)

        # IMPORTANT
        self.setFrequency(434.0)

        self.setTxPower(13)

        return True

    def setModeIdle(self):

        if self._mode != MODE_STDBY:

            self.write(
                REG_OP_MODE,
                MODE_STDBY
            )

            self._mode = MODE_STDBY
    def sleep(self):

        self.write(
            REG_OP_MODE,
            MODE_SLEEP
        )

        self._mode = MODE_SLEEP
    def setModeRx(self):

        if self._mode != MODE_RXCONTINUOUS:

            self.write(
                REG_OP_MODE,
                MODE_RXCONTINUOUS
            )

            self.write(
                REG_DIO_MAPPING1,
                0x00
            )

            self._mode = MODE_RXCONTINUOUS
    def setModeTx(self):

        if self._mode != MODE_TX:

            self.write(
                REG_OP_MODE,
                MODE_TX
            )

            self.write(
                REG_DIO_MAPPING1,
                0x40
            )

            self._mode = MODE_TX
    def setFrequency(self, freq):

        frf = int((freq * 1000000.0) / RH_RF95_FSTEP)

        self.write(REG_FRF_MSB, (frf >> 16) & 0xFF)

        self.write(REG_FRF_MID, (frf >> 8) & 0xFF)

        self.write(REG_FRF_LSB, frf & 0xFF)

        return True
    def setModemConfig(self, index):

        cfg = MODEM_CONFIG_TABLE[index]

        self.write(REG_MODEM_CONFIG1, cfg[0])

        self.write(REG_MODEM_CONFIG2, cfg[1])

        self.write(REG_MODEM_CONFIG3, cfg[2])
    def setPreambleLength(self, length):

        self.write(REG_PREAMBLE_MSB,
                   (length >> 8) & 0xFF)

        self.write(REG_PREAMBLE_LSB,
                   length & 0xFF)
    def setTxPower(self, power):

        if power > 23:
            power = 23

        if power < 5:
            power = 5

        if power > 20:
            self.write(REG_PA_DAC,
                       PA_DAC_ENABLE)
            power -= 3
        else:
            self.write(REG_PA_DAC,
                       PA_DAC_DISABLE)

        self.write(
            REG_PA_CONFIG,
            PA_SELECT | (power - 5)
        )

    def clearRxBuf(self):
        self._rxBufValid = False
        self._bufLen = 0

    def validateRxBuf(self):
        if self._bufLen < RH_RF95_HEADER_LEN:
            return

        self._rxHeaderTo = self._buf[0]
        self._rxHeaderFrom = self._buf[1]
        self._rxHeaderId = self._buf[2]
        self._rxHeaderFlags = self._buf[3]

        if (
            self._promiscuous
            or self._rxHeaderTo == self._thisAddress
            or self._rxHeaderTo == 0xFF
        ):

            self._rxGood += 1
            self._rxBufValid = True
    def handleInterrupt(self):

        irq_flags = self.read(REG_IRQ_FLAGS)

        # CRC error
        if (
            self._mode == MODE_RXCONTINUOUS
            and
            (irq_flags & (IRQ_RX_TIMEOUT | IRQ_PAYLOAD_CRC_ERROR))
        ):

            self._rxBad += 1

        # Packet received
        elif (
            self._mode == MODE_RXCONTINUOUS
            and
            (irq_flags & IRQ_RX_DONE)
        ):

            length = self.read(REG_RX_NB_BYTES)
            current_addr = self.read(REG_FIFO_RX_CURRENT_ADDR)
            self.write(REG_FIFO_ADDR_PTR, current_addr)
            self._buf = self.burstRead(REG_FIFO, length)
            self._bufLen = length
            self.write(REG_IRQ_FLAGS, 0xFF)
            self._lastRssi = self.read(REG_PKT_RSSI) - 137
            self.validateRxBuf()

            if self._rxBufValid:
                self.setModeIdle()

        # TX finished
        elif (
            self._mode == MODE_TX
            and
            (irq_flags & IRQ_TX_DONE)
        ):

            self._txGood += 1
            self.setModeIdle()

        self.write(REG_IRQ_FLAGS, 0xFF)

    def available(self):
        if self.uartAvailable():
            b = self.uartRead()

            if b == ord('I'):
                if self.debug:
                    print("Interrupt")

                self.handleInterrupt()

        if self._mode == MODE_TX:
            return False

        self.setModeRx()

        return self._rxBufValid

    def recv(self):
        if not self.available():
            return None

        payload = bytes(
            self._buf[
                RH_RF95_HEADER_LEN:self._bufLen
            ]
        )

        self.clearRxBuf()

        return payload

    def send(self, data):

        # If is string -> convert to bytes
        if isinstance(data, str):
            data = data.encode()

        # Max Len check
        if len(data) > RH_RF95_MAX_MESSAGE_LEN:
            return False

        # Изчаква предишно предаване
        self.waitPacketSent()

        # Standby
        self.setModeIdle()

        # FIFO pointer = 0
        self.write(REG_FIFO_ADDR_PTR, 0)

        # RadioHead headers
        self.write(REG_FIFO, self._txHeaderTo)
        self.write(REG_FIFO, self._txHeaderFrom)
        self.write(REG_FIFO, self._txHeaderId)
        self.write(REG_FIFO, self._txHeaderFlags)

        # Payload
        self.burstWrite(REG_FIFO, data)

        # Payload length
        self.write(
            REG_PAYLOAD_LENGTH,
            len(data) + RH_RF95_HEADER_LEN
        )

        # Започва предаване
        self.setModeTx()

        return True

    def waitPacketSent(self, timeout=5.0):

        start = time.time()

        while self._mode == MODE_TX:

            self.available()

            if time.time() - start > timeout:
                return False

            time.sleep(0.001)

        return True

    # RadioHead headers
    def setHeaderTo(self, value):
        self._txHeaderTo = value & 0xFF

    def setHeaderFrom(self, value):
        self._txHeaderFrom = value & 0xFF

    def setHeaderId(self, value):
        self._txHeaderId = value & 0xFF

    def setHeaderFlags(self, value):
        self._txHeaderFlags = value & 0xFF

    def lastRssi(self):
        return self._lastRssi

    def rxGood(self):
        return self._rxGood

    def rxBad(self):
        return self._rxBad

    def txGood(self):
        return self._txGood
