""" CLI application to try the brailfun features. """

import os
os.system("sudo pigpiod")
import pigpio as GPIO
import brailfun

braille_cell = brailfun.NewCell(power=3, time_on=1, time_off=0.5, signal_type=1)
pigpio_controller = braille_cell.pi
braille_cell.init()

pin_indicador_encendido = 25
pigpio_controller.set_mode(pin_indicador_encendido, GPIO.OUTPUT)
pigpio_controller.write(pin_indicador_encendido, 1)

user_command = "_"

while user_command[0] != "e":
    user_command = input(
    """\nWrite a brailfun command
    \n[pi]nout\n[pa]rameters\n[t]rigger active_pins -> t 126\n[w]riter word -> w hola\n[g]enerator\n[rl]random_letter\n[rp]random_pattern\n[e]xit\n\nCommand: """)

    user_command = user_command.split()

    if user_command[0] == "pi":
        gpio_pins = [4, 5, 6, 12, 13, 16, 17, 18, 22, 23, 24, 26, 27]
        new_pinout = braille_cell.pinout()
        print(f"Input the bcm pin value, remember it has to be a gpio pin ({gpio_pins})\nIf you don't want to change the pin value write an *\n")

        for pin_name in new_pinout.keys():
            new_pin = 0
            while new_pin not in gpio_pins:
                new_pin = input(f"{pin_name}: ")
                if new_pin == "*":
                    break
                
                new_pin = int(new_pin)
                if new_pin in gpio_pins:
                    new_pinout[pin_name] = new_pin

        braille_cell.pinout(new_pinout["signal_pin"], new_pinout["d1"], new_pinout["d2"], new_pinout["d3"], new_pinout["d4"], new_pinout["d5"], new_pinout["d6"])

    if user_command[0] == "pa":
        new_parameters = braille_cell.parameters()
        print(f"\nCurrent parameters {new_parameters}")
        print("Input the braille cell parameters within the ranges, if you don't want to change a parameter write an *\n\npower(int): 1-5\ntime_on(float): 0.5-infinite\ntime_off(float): 0.5-infinite\nsignal_type(int): 1-8\n")

        for parameter in new_parameters.keys():
            input_check = False
            while parameter in ["power", "time_on", "time_off", "signal_type"]:
                user_input = input(f"{parameter}: ")
                if user_input == "*":
                    break
                
                user_input = float(user_input)
                if parameter == "power" and user_input in range(1,6):
                    input_check = True
                elif parameter == "time_on" and user_input >= 0.5:
                    input_check = True
                elif parameter == "time_off" and user_input >= 0.5:
                    input_check = True
                elif parameter == "signal_type" and user_input in range(1,9):
                    input_check = True

                if input_check:
                    new_parameters[parameter] = user_input
                    break
        
        braille_cell.parameters(int(new_parameters["power"]), new_parameters["time_on"], new_parameters["time_off"], int(new_parameters["signal_type"]))

    if user_command[0] == "t":
        braille_pattern = [0, 0, 0, 0, 0, 0]
        for active_pin in user_command[1]:
            braille_pattern[int(active_pin)-1] = 1

        braille_cell.trigger(braille_pattern)

    if user_command[0] == "w":
        braille_cell.writer(user_command[1])

    if user_command[0] == "g":
        braille_cell.generator()
    
    if user_command[0] == "rl":
        letter,_ = braille_cell.random_letter()
        print(f"\nletter: {letter}\n")

    if user_command[0] == "rp":
        pattern = braille_cell.random_pattern()
        print(f"\npattern: {pattern}\n")  

pigpio_controller.write(pin_indicador_encendido, 0)
braille_cell.close()
os.system('sudo killall pigpiod')