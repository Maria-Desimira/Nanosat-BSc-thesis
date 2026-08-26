from temperature import get_temperature_c, get_temperature_k
from RH_RF95 import RH_RF95
from gps import get_position, get_altitude, get_satellites
from imu import get_acceleration, get_gyroscope, get_magnetic_field

import time

radio = RH_RF95(
    port="/dev/ttyAMA3",
    debug=False
)

radio.init()
radio.setFrequency(434.0)

radio.setHeaderTo(0xFF)
radio.setHeaderFrom(0xFF)
radio.setHeaderId(0)
radio.setHeaderFlags(0)

current_mode = None

print("Waiting for command...")


while True:

    message = radio.recv()

    if message is not None:
        command = (
            message
            .rstrip(b"\x00")
            .decode("utf-8")
            .strip()
            .lower()
        )

        print("Command:", command)

        if command == "temp_c":
            current_mode = "temp_c"

        elif command == "temp_k":
            current_mode = "temp_k"

        elif command == "gps":
            current_mode = "gps"

        elif command == "alt":
            current_mode = "alt"

        elif command == "satellites":
            current_mode = "satellites"

        elif command == "acc":
            current_mode = "acc"

        elif command == "gyro":
            current_mode = "gyro"

        elif command == "mag":
            current_mode = "mag"

        elif command == "data":
            current_mode = "data"

    if current_mode == "temp_c":
        temperature = get_temperature_c()

        response = f"{temperature:.2f} C"

        radio.send(response.encode() + b"\x00")
        radio.waitPacketSent()

        time.sleep(1)

    elif current_mode == "temp_k":
        temperature = get_temperature_k()

        response = f"{temperature:.2f} K"

        radio.send(response.encode() + b"\x00")
        radio.waitPacketSent()

        time.sleep(1)

    elif current_mode == "gps":
        latitude, longitude = get_position()

        response = f"{latitude:.6f},{longitude:.6f}"
        radio.send(response.encode() + b"\x00")
        radio.waitPacketSent()

        time.sleep(1)

    elif current_mode == "alt":
        altitide = get_altitude()
        response = f"{altitide:.2f} m"

        radio.send(response.encode() + b"\x00")
        radio.waitPacketSent()
        
        time.sleep(1)
        

    elif current_mode == "satellites":
        satellites = get_satellites()
        response = str(satellites)

        radio.send(response.encode() + b"\x00")
        radio.waitPacketSent()
        
        time.sleep(1)

    elif current_mode == "acc":
        ax, ay, az = get_acceleration()

        response = (
            f"ACC X:{ax:.2f} "
            f"Y:{ay:.2f} "
            f"Z:{az:.2f} g"
        )

        radio.send(response.encode() + b"\x00")
        radio.waitPacketSent()

        time.sleep(1)

    elif current_mode == "gyro":
        gx, gy, gz = get_gyroscope()

        response = (
            f"GYRO X:{gx:.2f} "
            f"Y:{gy:.2f} "
            f"Z:{gz:.2f} dps"
        )

        radio.send(response.encode() + b"\x00")
        radio.waitPacketSent()

        time.sleep(1)

    elif current_mode == "mag":
        magnetic = get_magnetic_field()

        if magnetic is not None:
            mx, my, mz = magnetic

            response = (
                f"MAG X:{mx:.2f} "
                f"Y:{my:.2f} "
                f"Z:{mz:.2f} uT"
            )

            radio.send(response.encode() + b"\x00")
            radio.waitPacketSent()

        time.sleep(1)

    elif current_mode == "data":

        temp_c = get_temperature_c()
        temp_k = get_temperature_k()
        latitude, longitude = get_position()
        altitude = get_altitude()
        satellites = get_satellites()
        ax, ay, az = get_acceleration()
        gx, gy, gz = get_gyroscope()
        magnetic = get_magnetic_field()

        if magnetic is not None:
            mx, my, mz = magnetic
        else:
            mx = 0
            my = 0
            mz = 0

        response = (
            f"T:{temp_c:.2f}C "
            f"GPS:{latitude:.6f},{longitude:.6f} "
            f"ALT:{altitude:.2f}m "
            f"SAT:{satellites} "
            f"ACC:{ax:.2f},{ay:.2f},{az:.2f} "
            f"GYRO:{gx:.2f},{gy:.2f},{gz:.2f} "
            f"MAG:{mx:.2f},{my:.2f},{mz:.2f}"
        )

        radio.send(response.encode() + b"\x00")
        radio.waitPacketSent()

        time.sleep(1)