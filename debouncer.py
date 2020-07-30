import os
os.system("sudo pigpiod")

import pigpio as GPIO
import time

pi = GPIO.pi()

a = 0
t_debounce_ini = 0

def funcion_activacion(gpio, level, tick):
    
    global a
    global t_debounce_ini
    t_debounce_end = time.time()
    
    t_debounce = t_debounce_end - t_debounce_ini

    if t_debounce >= 1:
        print(gpio, level, tick)
        a += 1
        print("Hola: {}".format(a))

    t_debounce_ini = time.time()

cb1 = pi.callback(6, 1, funcion_activacion)

while True:
    pass