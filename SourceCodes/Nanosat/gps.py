import serial
import pynmea2

gps = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=1)

def _read_message():

    while True:

        line=gps.readline().decode("ascii",errors="ignore").strip()

        if line.startswith("$GNGGA") or line.startswith("$GPGGA"):
            try:
                return pynmea2.parse(line)

            except pynmea2.ParseError:
                pass

def position():

    msg= _read_message()

    return msg.lat, msg.long


def altitude():
    msg = _read_message()
    return msg.alt

def satellites():

    msg = _read_message()
    return int(msg.num_sats)



if __name__ == "__main__":
    while True:

        print ("--------")
        print ("latitude: ", position()[0])
        print ("longitude: ", position()[1])
        print ("altitude: ", altitude())
        print ("satellites:", satellites())
