from smbus import SMBus
import time

# I2C адреси

# ICM20600:
# - 3-осен акселерометър
# - 3-осен жироскоп
ICM_ADDRESS = 0x69

# AK09918:
# - 3-осен магнитометър
AK_ADDRESS = 0x0C

# Регистри на ICM20600
PWR_MGMT_1 = 0x6B

ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43


# Регистри на AK09918
AK_ST1 = 0x10
AK_HXL = 0x11
AK_CNTL2 = 0x31
AK_CNTL3 = 0x32

# Режим за непрекъснато измерване с 100 Hz
AK_CONTINUOUS_100HZ = 0x08


# Стандартната I2C шина на Raspberry Pi
bus = SMBus(1)

# Инициализация
def initialize():
    #Стартира ICM20600 и AK09918

    # Събуждане на ICM20600
    bus.write_byte_data(
        ICM_ADDRESS,
        PWR_MGMT_1,
        0x01
    )

    time.sleep(0.1)

    # Reset на магнитометъра
    bus.write_byte_data(
        AK_ADDRESS,
        AK_CNTL3,
        0x01
    )

    time.sleep(0.1)

    # Непрекъснато измерване на магнитното поле
    bus.write_byte_data(
        AK_ADDRESS,
        AK_CNTL2,
        AK_CONTINUOUS_100HZ
    )

    time.sleep(0.1)

# Помощни функции
def _read_icm_word(register): #чете 16-битова знакова стойност от ICM20600 като ICM20600 изпраща първо старшия байт, след това младшия
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


def _convert_little_endian(low, high):  #Обединява два байта от AK09918.
   # AK09918 изпраща първо младшия байт,след това старшия байтa
    value = (high << 8) | low

    if value >= 32768:
        value -= 65536

    return value

# Акселерометър
def get_acceleration():  #Връща ускорението по X, Y и Z в g.
    
    ax_raw = _read_icm_word(ACCEL_XOUT_H)
    ay_raw = _read_icm_word(ACCEL_XOUT_H + 2)
    az_raw = _read_icm_word(ACCEL_XOUT_H + 4)

    # Стандартен диапазон ±2 g:
    # 16384 сурови единици = 1 g
    ax = ax_raw / 16384.0
    ay = ay_raw / 16384.0
    az = az_raw / 16384.0

    return ax, ay, az

# Жироскоп
def get_gyroscope():
    #Връща ъгловата скорост по X, Y и Z в градуси за секунда — dps.

    gx_raw = _read_icm_word(GYRO_XOUT_H)
    gy_raw = _read_icm_word(GYRO_XOUT_H + 2)
    gz_raw = _read_icm_word(GYRO_XOUT_H + 4)

    # Стандартен диапазон ±250 dps: 131 сурови единици = 1 dps
    gx = gx_raw / 131.0
    gy = gy_raw / 131.0
    gz = gz_raw / 131.0

    return gx, gy, gz

# Магнитометър
def get_magnetic_field():
    #Връща магнитното поле по X, Y и Z в микротесла — uT.
    #Ако все още няма готово измерване, връща None.

    status = bus.read_byte_data(
        AK_ADDRESS,
        AK_ST1
    )

    # Бит 0 показва дали има готови нови данни
    if not status & 0x01:
        return None

    # Четем:
    # HXL, HXH, HYL, HYH, HZL, HZH, TMPS, ST2
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

    # ST2 е последният прочетен байт.
    # Бит 3 показва препълване на измерването.
    if data[7] & 0x08:
        return None

    # Чувствителност на AK09918:
    # 0.15 микротесла за една сурова единица
    mx = mx_raw * 0.15
    my = my_raw * 0.15
    mz = mz_raw * 0.15

    return mx, my, mz

# Автоматично стартиране при import imu
initialize()