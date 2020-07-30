import os
os.system("sudo pigpiod")

import pigpio as GPIO
import time
import threading

pi = GPIO.pi()

led_pins = [[25, 0], [26, 0], [16, 0]]
stop_blinking = False

for pin in led_pins:
		pi.set_mode(pin[0], GPIO.OUTPUT)
		pi.write(pin[0], 0)

user_input = "0"

def blinker():
    global stop_blinking
    while True:
        pi.write(25, 0)
        time.sleep(1)
        pi.write(25, 1)
        time.sleep(1)

        if stop_blinking:
            break

blinker_thread = threading.Thread(target=blinker)

blinker_thread.start()

while user_input != "*":
    user_input = int(user_input)

    led_pins[user_input][1] = not(led_pins[user_input][1])
    pi.write(led_pins[user_input][0], led_pins[user_input][1])

    user_input = input("Ingrese el led que quiere que se ilumine: ")


stop_blinking = True
blinker_thread.join()

pi.stop()
os.system('sudo killall pigpiod')