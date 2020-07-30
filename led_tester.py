import os
os.system("sudo pigpiod")

import pigpio as GPIO


pi = GPIO.pi()

led_pins = [[25, 0], [26, 0], [16, 0]]

for pin in led_pins:
		pi.set_mode(pin[0], GPIO.OUTPUT)
		pi.write(pin[0], 0)

user_input = "0"


while user_input != "*":
    user_input = int(user_input)

    led_pins[user_input][1] = not(led_pins[user_input][1])
    pi.write(led_pins[user_input][0], led_pins[user_input][1])

    user_input = input("Ingrese el led que quiere que se ilumine: ")


pi.stop()
os.system('sudo killall pigpiod')