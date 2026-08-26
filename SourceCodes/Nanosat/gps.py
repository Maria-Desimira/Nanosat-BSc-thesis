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

def get_position():

    msg= _read_message()

    return msg.latitude, msg.longitude


def get_altitude():
    msg = _read_message()
    return msg.altitude

def get_satellites():

    msg = _read_message()
    return int(msg.num_sats)



if __name__ == "__main__":
    while True:

        print ("--------")
        print ("latitude: ", get_position()[0])
        print ("longitude: ", get_position()[1])
        print ("altitude: ", get_altitude())
        print ("satellites:", get_satellites())
