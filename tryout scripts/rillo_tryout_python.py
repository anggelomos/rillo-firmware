import os
os.system("sudo pigpiod")

import pigpio as GPIO
import spidev

pi = GPIO.pi()
spi = spidev.SpiDev()
spi.open(0,0) 

pin_boton_activacion = 6            #pin 31
pin_boton_bateria = 5               #pin 29
toggle_pins = [[25, 0], [18, 0], [24, 0], [23, 0], [22, 0], [27, 0], [4, 0], [17, 0], [12, 0], [13, 0], [16, 0]]

pi.set_mode(pin_boton_activacion, GPIO.INPUT)
pi.set_mode(pin_boton_bateria, GPIO.INPUT)
for pin in toggle_pins:
                pi.set_mode(pin[0], GPIO.OUTPUT)
                pi.write(pin[0], 0)

pi.set_glitch_filter(pin_boton_activacion, 2000)
pi.set_glitch_filter(pin_boton_bateria, 500)

def yield_activation(gpio, level, tick):
    print("\nBoton de activacion!\n")

def yield_bateria(gpio, level, tick):
    print("\nBoton de bateria!\n")

    canal_input_bateria = 0

    spi.max_speed_hz = 1350000
    adc = spi.xfer2([1,(8+canal_input_bateria)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]

    print(data)
    nivel_bateria = data*5.0/1023
    print(f"Nivel de bateria: {nivel_bateria}\n")

interrupcion_activacion = pi.callback(pin_boton_activacion, GPIO.EITHER_EDGE, yield_activation)
interrupcion_bateria = pi.callback(pin_boton_bateria, GPIO.RISING_EDGE, yield_bateria)

user_input = "0"

while user_input != "*":
    user_input = int(user_input)

    toggle_pins[user_input][1] = not(toggle_pins[user_input][1])
    # print(f"{user_input} - {toggle_pins[user_input][1]}\n")
    print(f"\n{toggle_pins}\n")
    pi.write(toggle_pins[user_input][0], toggle_pins[user_input][1])

    user_input = input("Ingrese el pin del cual quiere cambiar su estado: ")

pi.stop()
spi.close()
