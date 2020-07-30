import os
os.system("sudo pigpiod")

import pigpio as GPIO
import threading
import time

pi = GPIO.pi()

rillo_slept = False
pi.set_glitch_filter(5, 500)


def activate_rillo(gpio, level, tick):
    global rillo_slept
    global cb1

    rillo_slept = False
    print("pup")
    cb1.cancel()
    del(cb1)


def rillo_sleep():
    global rillo_slept
    global cb1

    rillo_slept = True
    t_ini = time.time()
    t_current = 0

    print("\nsleepy rillo")
    cb1 = pi.callback(5, 1, activate_rillo)

    while (t_current <= 10) and rillo_slept:
        t_current = time.time() - t_ini
        print("sleep time: {:.0f}".format(t_current))
        time.sleep(1)
    

    if rillo_slept:
        print("rillo out")
    else:
        rillo_active()


def rillo_active():

    t_ini = time.time()
    t_current = 0
    print("\nactive rillo")

    while t_current <= 10:
        t_current = time.time() - t_ini
        print("active time: {:.0f}".format(t_current))
        time.sleep(1)

    rillo_sleep()


rillo_active()