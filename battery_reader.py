import spidev
import time

spi = spidev.SpiDev()
spi.open(0,0)

canal_input_bateria = 0

while True:
    spi.max_speed_hz = 1350000
    adc = spi.xfer2([1,(8+canal_input_bateria)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]

    nivel_bateria = data*5.0/1023

    print(f"nivel de bateria: {nivel_bateria}")
    time.sleep(1)


spi.close()