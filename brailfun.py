import pigpio as GPIO
import math
import time
import random
#import numpy as np
#from numpy import interp	# To scale values


# This code uses BCM pins
# Tested on python 3.5.3

class new_cell:

	# The default phyisical pins are 12, 7, 11, 13, 15, 16 and 18
	# The first value is the signal BCM pin (pwm) then the next values are the vibrator BCM pins from 1 to 6

	vibration_pins = [18, 4, 17, 27, 22, 23, 24]

	#GPIO setup
	pi = GPIO.pi()

	for pin in vibration_pins:
		pi.set_mode(pin, GPIO.OUTPUT)
		pi.write(pin, 0)

	def __init__(self, power = 5, time_on = 3, time_off = 1, signal_type = 1):
		self.power = power
		self.time_on = time_on
		self.time_off = time_off
		self.signal_type = signal_type

	@classmethod
	def pinout(cls, signal_pin = vibration_pins[0], v1 = vibration_pins[1], v2 = vibration_pins[2], v3 = vibration_pins[3], v4 = vibration_pins[4], v5 = vibration_pins[5], v6 = vibration_pins[6]):
		""" This function prints the pinout and helps the user change the vibration pinout, the first parameter is the signal pin (pwm) and the v1 to v6 parameters are the i/o pins for each vibrator"""
		cls.vibration_pins = [signal_pin, v1, v2, v3, v4, v5, v6]

		for pin in cls.vibration_pins:
			new_cell.pi.set_mode(pin, GPIO.OUTPUT)
			new_cell.pi.write(pin, 0)

		print("\nPinout\nSignal pin: {}\nVibrator pins: {}".format(cls.vibration_pins[0], cls.vibration_pins[1:]))

	@staticmethod
	def clamp(value):
		""" this functiton limitates the value between 0 and 255"""
		
		if(value>255):
			return 255
		elif(value<0):
			return 0
		else:
			return value

	@classmethod
	def close(cls):
		cls.pi.stop()

	def s_square(self):
		#square signal

		output=255*(self.power/5.0)
		new_cell.pi.set_PWM_dutycycle(new_cell.vibration_pins[0], output)
			
		time.sleep(self.time_on)
		
		output=0
		new_cell.pi.set_PWM_dutycycle(new_cell.vibration_pins[0], output)
		
		time.sleep(self.time_off)

	#señal triangular

	def s_triad(self):

		t_ini = time.time()
		
		# In this cycle the vibration signal is calculated and activated through a pwm signal
		
		while time.time() <= (t_ini + self.time_on):
			
			if time.time() < (t_ini + self.time_on/2.0):
				# First half of the cycle, t_current is calculated from 0 to time_on/2

				output = (255*(self.power/5.0))/(self.time_on/2.0)*(time.time()-t_ini)  # Here we calculate the output based on the line equation
				t_ini1 = time.time() 													# Aux variable to know the exact moment when the first cycle ends
				
			else:
		
				# Second half of the cycle, t_current is calculated from time_on/2 to time_on
				output = -(255*(self.power/5.0))/(self.time_on/2.0)*(time.time()-t_ini1)+(255*(self.power/5.0))
				
			
			output = new_cell.clamp(output)
			new_cell.pi.set_PWM_dutycycle(new_cell.vibration_pins[0],output)
		
			
		output=0
		new_cell.pi.set_PWM_dutycycle(new_cell.vibration_pins[0],output)
		time.sleep(self.time_off)


	#señal seno

	def s_sine(self):
		
		t_ini = time.time()
		
		# In this cycle the vibration signal is calculated and activated through a pwm signal
		
		while time.time() <= (t_ini + self.time_on):
			
			output = (255*(self.power/5.0))*math.sin((math.pi/self.time_on)*(time.time()-t_ini))	# In this line we calcule the half cycle of the sin function going from 0 to time_on and having a 255 in amplitude
			new_cell.pi.set_PWM_dutycycle(new_cell.vibration_pins[0],output)
					
		output=0
		new_cell.pi.set_PWM_dutycycle(new_cell.vibration_pins[0], output)
		time.sleep(self.time_off)


	#señal logaritmica
	
	def s_log(self):
		t_ini = time.time()
		
		# In this cycle the vibration signal is calculated and activated through a pwm signal
		
		while time.time() <= (t_ini + self.time_on):
			
			if time.time() < (t_ini + self.time_on/2.0):
				# First half of the cycle, t_current is calculated from 0 to time_on/2

				t_current = (2*(10-1)/(self.time_on))*(time.time() - t_ini) + 1 	# In this line we remap the time so that is goes from 1 to 10
				t_ini1 = time.time()
				
			else:
				# Second half of the cycle, t_current is calculated from time_on/2 to time_on
				
				t_current = (2*(1-10)/(self.time_on))*(time.time() - t_ini1) + 10 	# In this line we remap the time so that is goes from 10 to 1
					
					
			output = (255.0*math.log10(t_current))*(self.power/5.0)
			output = new_cell.clamp(output)
			
			
			new_cell.pi.set_PWM_dutycycle(new_cell.vibration_pins[0],output)
			
		output=0
		new_cell.pi.set_PWM_dutycycle(new_cell.vibration_pins[0],output)
		time.sleep(self.time_off)


	#señal exponencial
	
	def s_exp(self):
		
		t_ini = time.time()
		
		# In this cycle the vibration signal is calculated and activated through a pwm signal
		
		while time.time() <= (t_ini + self.time_on):
			
			if time.time() < (t_ini + self.time_on/2.0):
				# First half of the cycle, t_current is calculated from 0 to time_on/2

				t_current = (2*(math.log(10)-(-math.log(10)))/(self.time_on))*(time.time() - t_ini) + (-math.log(10)) # In this line we remap the time so that is goes from -ln(10) to ln(10)
				t_ini1 = time.time()
				
			else:
				# Second half of the cycle, t_current is calculated from time_on/2 to time_on
				
				t_current = (2*((-math.log(10))-math.log(10))/(self.time_on))*(time.time() - t_ini1) + math.log(10) # In this line we remap the time so that is goes from ln(10) to -ln(10)
					
					
			output = (25.5*math.exp(t_current))*(self.power/5.0)
			output = new_cell.clamp(output)
			
			new_cell.pi.set_PWM_dutycycle(new_cell.vibration_pins[0], output)
			
		output=0
		new_cell.pi.set_PWM_dutycycle(new_cell.vibration_pins[0],output)
		time.sleep(self.time_off)


	#señal click (logratimica + exponencial)
	
	def s_click(self):
		
		t_ini = time.time()
		
		# In this cycle the vibration signal is calculated and activated through a pwm signal
		
		while time.time() <= (t_ini + self.time_on):
			
			if time.time() < (t_ini + self.time_on/2.0):
				# First half of the cycle, t_current is calculated from 0 to time_on/2 
				
				t_current = (2*(10-1)/(self.time_on))*(time.time() - t_ini) + 1 # In this line we remap the time so that is goes from 10 to 1
				output = (255.0*math.log10(t_current))*(self.power/5.0)
				t_ini1 = time.time()
				
			else:
				# Second half of the cycle, t_current is calculated from time_on/2 to time_on
				
				t_current = (2*((-math.log(10))-math.log(10))/(self.time_on))*(time.time() - t_ini1) + math.log(10) # In this line we remap the time so that is goes from -ln(10) to ln(10)
				output = (25.5*math.exp(t_current))*(self.power/5.0)
					
			
			output = new_cell.clamp(output)
			
			new_cell.pi.set_PWM_dutycycle(new_cell.vibration_pins[0],output)
			
		output=0
		new_cell.pi.set_PWM_dutycycle(new_cell.vibration_pins[0],output)
		time.sleep(self.time_off)


	#señal rev-click (exponencial + logartimica)

	def s_revclick(self):
		
		t_ini = time.time()
		
		# In this cycle the vibration signal is calculated and activated through a pwm signal
		
		while time.time() <= (t_ini + self.time_on):
			
			if time.time() < (t_ini + self.time_on/2.0):
				# First half of the cycle, t_current is calculated from 0 to time_on/2
				
				t_current = (2*(math.log(10)-(-math.log(10)))/(self.time_on))*(time.time() - t_ini) + (-math.log(10)) # In this line we remap the time so that is goes from -ln(10) to ln(10)
				t_ini1 = time.time()
				output = (25.5*math.exp(t_current))*(self.power/5.0)
			else:
				# Second half of the cycle, t_current is calculated from time_on/2 to time_on

				t_current = (2*(1-10)/(self.time_on))*(time.time() - t_ini1) + 10 # In this line we remap the time so that is goes from 10 to 1
				output = (255.0*math.log10(t_current))*(self.power/5.0)
					
			
			output = new_cell.clamp(output)
			
			new_cell.pi.set_PWM_dutycycle(new_cell.vibration_pins[0],output)
			
		output=0
		new_cell.pi.set_PWM_dutycycle(new_cell.vibration_pins[0],output)
		time.sleep(self.time_off)


	#señal rampa
	
	def s_ramp(self):
		
		t_ini = time.time()
		
		# In this cycle the vibration signal is calculated and activated through a pwm signal
		
		while time.time() <= (t_ini + self.time_on):
		
			output = (255*(self.power/5.0))/(self.time_on)*(time.time()-t_ini)
			new_cell.pi.set_PWM_dutycycle(new_cell.vibration_pins[0],output)
					
		output=0
		new_cell.pi.set_PWM_dutycycle(new_cell.vibration_pins[0],output)
		time.sleep(self.time_off)

	@staticmethod
	def randletter():

		# This function generates a random letter

		alfabeto_regular = "abcdefghijklmnñopqrstuvwxyz"
		return alfabeto_regular[random.randint(0,26)]
  
	@staticmethod
	def translator(letter):

		# This function translates a letter to a braille dot pattern

		letter.lower()

		regular_alphabet = "abcdefghijklmnñopqrstuvwxyz"
		braille_alphabet = [[0,0,0,0,0,0,0,0],[1,0,0,0,0,0,0,0],[1,1,0,0,0,0,0,0],[1,0,0,1,0,0,0,0],[1,0,0,1,1,0,0,0],[1,0,0,0,1,0,0,0],[1,1,0,1,0,0,0,0],[1,1,0,1,1,0,0,0],[1,1,0,0,1,0,0,0],[0,1,0,1,0,0,0,0],[0,1,0,1,1,0,0,0],[1,0,1,0,0,0,0,0],[1,1,1,0,0,0,0,0],[1,0,1,1,0,0,0,0],[1,0,1,1,1,0,0,0],[1,1,0,1,1,1,0,0],[1,0,1,0,1,0,0,0],[1,1,1,1,0,0,0,0],[1,1,1,1,1,0,0,0],[1,1,1,0,1,0,0,0],[0,1,1,1,0,0,0,0],[0,1,1,1,1,0,0,0],[1,0,1,0,0,1,0,0],[1,1,1,0,0,1,0,0],[0,1,0,1,1,1,0,0],[1,0,1,1,0,1,0,0],[1,0,1,1,1,1,0,0],[1,0,1,0,1,1,0,0]]

		braille_dictionary = dict(zip(regular_alphabet, braille_alphabet))

		return braille_dictionary[letter]

	
	def trigger(self, dot_pattern):
			
		'''This function triggers the actuator
		
			V_braille   ==> braille pattern, it's a boolean array with 6 values, ex {1,0,0,1,1,0}
			signal      ==> type of vibratino signal, it's a number between 1 and 8,    1 - Square signal
																						2 - Triangle signal
																						3 - Click signal (logarithmic + exponential)
																						4 - Ramp signal
																						5 - Exponential signal
																						6 - Sin signal
																						7 - Reverse click signal (exponential + logarithmic)
																						8 - logarithmic signal
																						
		'''
		
		for iteration_num in range(6):
			new_cell.pi.write(new_cell.vibration_pins[iteration_num+1], dot_pattern[iteration_num])

		if self.signal_type == 1:
			self.s_square()
			
		elif self.signal_type == 2:
			
			self.s_triad()
			
		elif self.signal_type == 6:
			
			self.s_sine()
			
		elif self.signal_type == 8:
			
			self.s_log()
			
		elif self.signal_type == 5:
			
			self.s_exp()
			
		elif self.signal_type == 3:
			
			self.s_click()
			
		elif self.signal_type == 7:
			
			self.s_revclick()
			
		elif self.signal_type == 4:
			
			self.s_ramp()
			
		else:
			print("Error: wrong signal selector")

		for iteration_num in range(6):
			new_cell.pi.write(new_cell.vibration_pins[iteration_num+1], 0)
			

	def generator(self):
		
		# This function activates all the dots in the cell going one by one
		
		for active_dot in range(0,6):
			vector_generador = [0,0,0,0,0,0]
			vector_generador[active_dot] = 1
			self.trigger(vector_generador)
		
			
	def writer(self, sentence):
		
		# This function writes the sentence in the braille cell, the sentence can be a letter, a word or a paragraph.
		
		for letter in sentence:
			caracter_braille = self.translator(letter)
			self.trigger(caracter_braille)


	def randomvib(self):
		
		# This function actives dots randomly in the cell
		
		vector_random = [0,0,0,0,0,0]
		
		for dot in range(0,6):
			vector_random[dot] = random.randint(0,1)
		
		self.trigger(vector_random)



	
	

