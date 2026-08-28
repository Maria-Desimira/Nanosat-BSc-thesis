from smbus import SMBus
import time

ICM_ADDRESS = 0x69

AK_ADDRESS = 0x0C

PWR_MGMT_1 = 0x6B

ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

AK_ST1 = 0x10
AK_HXL = 0x11
AK_CNTL2 = 0x31
AK_CNTL3 = 0x32

AK_CONTINUOUS_100HZ = 0x08

bus = SMBus(1)

def initialize():
 
    bus.write_byte_data(
        ICM_ADDRESS,
        PWR_MGMT_1,
        0x01
    )

    time.sleep(0.1)

    bus.write_byte_data(
        AK_ADDRESS,
        AK_CNTL3,
        0x01
    )

    time.sleep(0.1)

    bus.write_byte_data(
        AK_ADDRESS,
        AK_CNTL2,
        AK_CONTINUOUS_100HZ
    )

    time.sleep(0.1)

def _read_icm_word(register): 
    high = bus.read_byte_data(
        ICM_ADDRESS,
        register
    )

    low = bus.read_byte_data(
        ICM_ADDRESS,
        register + 1
    )

    value = (high << 8) | low

    if value >= 32768:
        value -= 65536

    return value


def _convert_little_endian(low, high):  
    value = (high << 8) | low

    if value >= 32768:
        value -= 65536

    return value

def acceleration():
    
    ax_raw = _read_icm_word(ACCEL_XOUT_H)
    ay_raw = _read_icm_word(ACCEL_XOUT_H + 2)
    az_raw = _read_icm_word(ACCEL_XOUT_H + 4)

    ax = ax_raw / 16384.0
    ay = ay_raw / 16384.0
    az = az_raw / 16384.0

    return ax, ay, az

def gyroscope():

    gx_raw = _read_icm_word(GYRO_XOUT_H)
    gy_raw = _read_icm_word(GYRO_XOUT_H + 2)
    gz_raw = _read_icm_word(GYRO_XOUT_H + 4)

    gx = gx_raw / 131.0
    gy = gy_raw / 131.0
    gz = gz_raw / 131.0

    return gx, gy, gz

def magnfield():

    status = bus.read_byte_data(
        AK_ADDRESS,
        AK_ST1
    )

    if not status & 0x01:
        return None

    data = bus.read_i2c_block_data( AK_ADDRESS, AK_HXL, 8)

    mx_raw = _convert_little_endian(
        data[0],
        data[1]
    )

    my_raw = _convert_little_endian(
        data[2],
        data[3]
    )

    mz_raw = _convert_little_endian(
        data[4],
        data[5]
    )

    if data[7] & 0x08:
        return None

    mx = mx_raw * 0.15
    my = my_raw * 0.15
    mz = mz_raw * 0.15

    return mx, my, mz

initialize()