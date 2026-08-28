from temperature import temp_c, temp_k
from RH_RF95 import RH_RF95
from gps import position, altitude, satellites
from imu import acceleration, gyroscope, magnfield

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
        temp = temp_c()

        response = f"{temp:.2f} C"

        radio.send(response.encode() + b"\x00")
        radio.waitPacketSent()

        time.sleep(1)

    elif current_mode == "temp_k":
        temp = temp_k()

        response = f"{temp:.2f} K"

        radio.send(response.encode() + b"\x00")
        radio.waitPacketSent()

        time.sleep(1)

    elif current_mode == "gps":
        lat, long = position()

        response = f"{lat:.6f},{long:.6f}"
        radio.send(response.encode() + b"\x00")
        radio.waitPacketSent()

        time.sleep(1)

    elif current_mode == "alt":
        alt = altitude()
        response = f"{alt:.2f} m"

        radio.send(response.encode() + b"\x00")
        radio.waitPacketSent()
        
        time.sleep(1)
        

    elif current_mode == "satellites":
        sat = satellites()
        response = str(sat)

        radio.send(response.encode() + b"\x00")
        radio.waitPacketSent()
        
        time.sleep(1)

    elif current_mode == "acc":
        ax, ay, az = acceleration()

        response = (
            f"ACC X:{ax:.2f} "
            f"Y:{ay:.2f} "
            f"Z:{az:.2f} g"
        )

        radio.send(response.encode() + b"\x00")
        radio.waitPacketSent()

        time.sleep(1)

    elif current_mode == "gyro":
        gx, gy, gz = gyroscope()

        response = (
            f"GYRO X:{gx:.2f} "
            f"Y:{gy:.2f} "
            f"Z:{gz:.2f} dps"
        )

        radio.send(response.encode() + b"\x00")
        radio.waitPacketSent()

        time.sleep(1)

    elif current_mode == "mag":
        magn = magnfield()

        if magn is not None:
            mx, my, mz = magn

            response = (
                f"MAG X:{mx:.2f} "
                f"Y:{my:.2f} "
                f"Z:{mz:.2f} uT"
            )

            radio.send(response.encode() + b"\x00")
            radio.waitPacketSent()

        time.sleep(1)

    elif current_mode == "data":

        temp_c = temp_c()
        temp_k = temp_k()
        lat, long = position()
        altitude = altitude()
        satellites = satellites()
        ax, ay, az = acceleration()
        gx, gy, gz = gyroscope()
        magn = magnfield()

        if magn is not None:
            mx, my, mz = magn
        else:
            mx = 0
            my = 0
            mz = 0

        response = (
            f"T:{temp_c:.2f}C "
            f"GPS:{lat:.6f},{long:.6f} "
            f"ALT:{alt:.2f}m "
            f"SAT:{sat} "
            f"ACC:{ax:.2f},{ay:.2f},{az:.2f} "
            f"GYRO:{gx:.2f},{gy:.2f},{gz:.2f} "
            f"MAG:{mx:.2f},{my:.2f},{mz:.2f}"
        )

        radio.send(response.encode() + b"\x00")
        radio.waitPacketSent()

        time.sleep(1)