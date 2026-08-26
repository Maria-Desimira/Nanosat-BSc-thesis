import serial
import time

class RHUartDriver:

    RH_WRITE_MASK = 0x80

    def __init__(self, port="/dev/ttyAMA3", baudrate=57600, timeout=1.0, debug=False):

        self.debug = debug

        self.ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout
        )

        if not self.ser.is_open:
            self.ser.open()

    def close(self):
        if self.ser.is_open:
            self.ser.close()

    def flush(self):
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()

    # Low level UART
    def uartAvailable(self):
        return self.ser.in_waiting

    def uartRead(self):
        b = self.ser.read(1)
        if len(b) == 0:
            return None
        return b[0]

    def uartTx(self, reg, data):

        packet = bytearray()

        packet.append(ord('W'))
        packet.append(reg)
        packet.append(len(data))
        packet.extend(data)

        if self.debug:
            print("TX:", packet.hex(" "))

        self.ser.write(packet)

    def uartRx(self, reg, length):

        packet = bytearray()

        packet.append(ord('R'))
        packet.append(reg)
        packet.append(length)

        self.ser.reset_input_buffer()

        if self.debug:
            print("TX:", packet.hex(" "))

        self.ser.write(packet)

        data = self.ser.read(length)

        if self.debug:
            print("RX:", data.hex(" "))

        return bytearray(data)

    # Register access
    def read(self, reg):

        data = self.uartRx(reg & ~self.RH_WRITE_MASK, 1)

        if len(data) != 1:
            raise RuntimeError(
                f"Register 0x{reg:02X}: expected 1 byte, got {len(data)}"
            )

        return data[0]

    def write(self, reg, value):

        self.uartTx(
            reg | self.RH_WRITE_MASK,
            bytes([value])
        )

    def burstRead(self, reg, length):

        return self.uartRx(
            reg & ~self.RH_WRITE_MASK,
            length
        )

    def burstWrite(self, reg, data):

        self.uartTx(
            reg | self.RH_WRITE_MASK,
            data
        )
