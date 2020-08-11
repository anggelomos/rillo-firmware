"""Create a cell object to control a braille cell through pwm signals in the gpio ports (BCM) in the raspberry pi zero."""

import pigpio as GPIO
import math
import time
import random
import unicodedata
from typing import Union

class NewCell:
	"""Control a braille cell through pwm signals in the gpio ports (BCM)

	Attributes
	-------
	braille_pins: dict
		Dictionary with the BCM pins used to control the dots in the braille cell, by default {"signal_pin":18, "d1": 4, "d2": 17, "d3": 27, "d4": 22, "d5": 23, "d6": 24}
	
	power: int(1 to 5)
		Integer indicating in a scall from 1 to 5 the braille cell vibration power, by default 5

	time_on: float(0.5 to inf)
		Activation signal time.

	time_off: float(0.5 to inf)
		Time between one activation signal and another one

	signal_type: int(1 to 8)
		Activation signal type, by default 1
			1 - Square signal
			2 - Triangle signal
			3 - Ramp signal
			4 - Exponential signal
			5 - logarithmic signal
			6 - Sine signal
			7 - Click signal (logarithmic + exponential)
			8 - Reverse click signal (exponential + logarithmic)

	Methods
	-------
	init
		Initialize all the pins.
	
	close
		Stop pigpio session.
		
	pinout
		Assign and initialize the braille cell bcm gpio pins.

	parameters
		Change braille cell attributes.

	trigger
		Activate the braille cell according to the cell parameters and the dot pattern

	writer
		Write the text in the braille cell activating consecutively each alphanumer letter.

	generator
		Activate each dot in the braille cell consecutively.

	random_letter
		Write a random letter in the braille cell.

	random_pattern
		Generate a random braille pattern and activate it in the braille cell.
	"""

	def __init__(self, braille_pins: dict={"signal_pin":18, "d1": 22, "d2": 23, "d3": 24, "d4": 27, "d5": 4, "d6": 17}, power: int=5, time_on: float=3, time_off: float=1, signal_type: int=1):
		self.braille_pins = braille_pins
		self.power = power
		self.time_on = time_on
		self.time_off = time_off
		self.signal_type = signal_type

	def __repr__(self):
		return f"NewCell({self.braille_pins}, {self.power}, {self.time_on}, {self.time_off}, {self.signal_type})"

	def __str__(self):
		return f"Braille Cell\npins: {self.braille_pins}\npower: {self.power}\nActive time: {self.time_on}\nTime between pulses: {self.time_off}\nSignal type: {self.signal_type}\n"
	
	# GPIO setup
	pi = GPIO.pi()

	def init(self):
		"""Initialize all the pins."""
		for pin in self.braille_pins.values():
			NewCell.pi.set_mode(pin, GPIO.OUTPUT)
			NewCell.pi.write(pin, 0)

	@classmethod
	def close(cls):
		"""Stop pigpio session."""
		cls.pi.stop()

	def pinout(self, signal_pin: int=None, d1: int=None, d2: int=None, d3: int=None, d4: int=None, d5: int=None, d6: int=None) -> dict:
		"""Assign and initialize the braille cell bcm gpio pins.

		Parameters
		----------
		signal_pin : int, optional
			Signal gpio pin number (BCM), by default None.
		d1-d6 : int, optional
			Braille dot gpio pin number (BCM), by default None.

		Returns
		-------
		pinout: dict
			Pinout dictionary, Ex. {"signal_pin":18, "d1":4, "d2":17, "d3":27, "d4":22, "d5":23, "d6":24}.
		"""
		function_arguments = locals()

		for key, value in function_arguments.items():
			if key != "self" and isinstance(value, int):
				self.braille_pins[key] = value

		for _, pin in self.braille_pins.items():
			NewCell.pi.set_mode(pin, GPIO.OUTPUT)
			NewCell.pi.write(pin, 0)

		print(f"\nPinout\n{self.braille_pins}\n")

		return self.braille_pins

	def parameters(self, power: int=None, time_on: float=None, time_off: float=None, signal_type: int=None) -> dict:
		"""Change braille cell attributes  

		Parameters
		----------
		power: int(1 to 5)
		Integer indicating in a scall from 1 to 5 the braille cell vibration power, by default 5

		time_on: float(0.5 to inf)
			Activation signal time.

		time_off: float(0.5 to inf)
			Time between one activation signal and another one

		signal_type: int(1 to 8)
			Activation signal type, by default 1
				1 - Square signal
				2 - Triangle signal
				3 - Ramp signal
				4 - Exponential signal
				5 - logarithmic signal
				6 - Sine signal
				7 - Click signal (logarithmic + exponential)
				8 - Reverse click signal (exponential + logarithmic)
		
		Returns
		-------
		braille_parameters: dict
			Braille cell parameters, Ex. {"power":5, "time_on":12, "time_off":3, "signal_type":7}.
		"""

		if isinstance(power, int):
			self.power = power
		
		if isinstance(time_on, float):
			self.time_on = time_on

		if isinstance(time_off, float):
			self.time_off = time_off

		if isinstance(signal_type, int):
			self.signal_type = signal_type
		
		braille_parameters = {"power":self.power, "time_on":self.time_on, "time_off":self.time_off, "signal_type":self.signal_type}
		return braille_parameters

	@staticmethod
	def _clamp(value: Union[int, float]) -> Union[int, float]:
		"""Limitate the input value between 255 and 0.

		Parameters
		----------
		value : int, float
			Input value to be truncated.

		Returns
		-------
		value : int, float
			A value between 0 and 255.
		"""
		
		if(value>255):
			return 255
		elif(value<0):
			return 0
		else:
			return value

	def _signal_square(self, braille_pattern: list) -> int:
		"""Activate a braille pattern with a square signal for time_on seconds and then waits for time_off seconds.

		Parameters
		----------
		braille_pattern : list(bool)
			6-value braille pattern list, 1 means the braille dot is activated and 0 means it isn't.

		Returns
		-------
		signal_value: int

		"""

		signal_value=255*(self.power/5.0)
		NewCell.pi.set_PWM_dutycycle(self.braille_pins["signal_pin"], signal_value)
		for index, value in enumerate(self.braille_pins.values()):
			if index == 0:
				continue
			NewCell.pi.set_PWM_dutycycle(value, 255*braille_pattern[index-1])
			
		time.sleep(self.time_on)
		
		NewCell.pi.set_PWM_dutycycle(self.braille_pins["signal_pin"], 0)
		for index, value in enumerate(self.braille_pins.values()):
			if index == 0:
				continue
			NewCell.pi.set_PWM_dutycycle(value, 0)
		
		time.sleep(self.time_off)

		return signal_value

	def _signal_triangle(self, braille_pattern: list) -> list:
		"""Activate a braille pattern with a triangle signal for time_on seconds and then waits for time_off seconds.

		Parameters
		----------
		braille_pattern : list(bool)
			6-value braille pattern list, 1 means the braille dot is activated and 0 means it isn't.

		Returns
		-------
		signal: list
			List with the values the signal takes over time.
		"""

		signal = []
		t_ini = time.time()
		
		for index, value in enumerate(self.braille_pins.values()):
			if index == 0:
				continue
			NewCell.pi.set_PWM_dutycycle(value, 255*braille_pattern[index-1])

		while time.time() <= (t_ini + self.time_on):
			if time.time() < (t_ini + self.time_on/2.0):
				signal_value = (255*(self.power/5.0))/(self.time_on/2.0)*(time.time()-t_ini)  
				t_ini1 = time.time() 													
			else:
				signal_value = (255*(self.power/5.0))-(255*(self.power/5.0))/(self.time_on/2.0)*(time.time()-t_ini1)
			
			signal_value = NewCell._clamp(signal_value)
			signal.append(signal_value)
			NewCell.pi.set_PWM_dutycycle(self.braille_pins["signal_pin"], signal_value)
			
		NewCell.pi.set_PWM_dutycycle(self.braille_pins["signal_pin"], 0)
		for index, value in enumerate(self.braille_pins.values()):
			if index == 0:
				continue
			NewCell.pi.set_PWM_dutycycle(value, 0)

		time.sleep(self.time_off)

		return signal

	def _signal_ramp(self, braille_pattern: list) -> list:
		"""Activate a braille pattern with a ramp signal for time_on seconds and then waits for time_off seconds.

		Parameters
		----------
		braille_pattern : list(bool)
			6-value braille pattern list, 1 means the braille dot is activated and 0 means it isn't.

		Returns
		-------
		signal: list
			List with the values the signal takes over time.
		"""

		signal = []
		t_ini = time.time()
		
		for index, value in enumerate(self.braille_pins.values()):
			if index == 0:
				continue
			NewCell.pi.set_PWM_dutycycle(value, 255*braille_pattern[index-1])

		while time.time() <= (t_ini + self.time_on):
			signal_value = (255*(self.power/5.0))/(self.time_on)*(time.time()-t_ini)

			signal_value = NewCell._clamp(signal_value)
			signal.append(signal_value)
			NewCell.pi.set_PWM_dutycycle(self.braille_pins["signal_pin"], signal_value)
					

		NewCell.pi.set_PWM_dutycycle(self.braille_pins["signal_pin"], 0)
		for index, value in enumerate(self.braille_pins.values()):
			if index == 0:
				continue
			NewCell.pi.set_PWM_dutycycle(value, 0)

		time.sleep(self.time_off)

		return signal

	def _signal_sine(self, braille_pattern: list) -> list:
		"""Activate a braille pattern with a sine signal (positive side) for time_on seconds and then waits for time_off seconds.

		Parameters
		----------
		braille_pattern : list(bool)
			6-value braille pattern list, 1 means the braille dot is activated and 0 means it isn't.

		Returns
		-------
		signal: list
			List with the values the signal takes over time.
		"""

		signal = []
		t_ini = time.time()
		
		for index, value in enumerate(self.braille_pins.values()):
			if index == 0:
				continue
			NewCell.pi.set_PWM_dutycycle(value, 255*braille_pattern[index-1])
		
		while time.time() <= (t_ini + self.time_on):
			signal_value = (255*(self.power/5.0))*math.sin((math.pi/self.time_on)*(time.time()-t_ini))
			
			signal_value = NewCell._clamp(signal_value)
			signal.append(signal_value)
			NewCell.pi.set_PWM_dutycycle(self.braille_pins["signal_pin"], signal_value)

		NewCell.pi.set_PWM_dutycycle(self.braille_pins["signal_pin"], 0)
		for index, value in enumerate(self.braille_pins.values()):
			if index == 0:
				continue
			NewCell.pi.set_PWM_dutycycle(value, 0)

		time.sleep(self.time_off)

		return signal

	def _signal_log(self, braille_pattern: list) -> list:
		"""Activate a braille pattern with a logarithmic signal for time_on seconds and then waits for time_off seconds.

		Parameters
		----------
		braille_pattern : list(bool)
			6-value braille pattern list, 1 means the braille dot is activated and 0 means it isn't.

		Returns
		-------
		signal: list
			List with the values the signal takes over time.
		"""

		signal = []
		t_ini = time.time()

		for index, value in enumerate(self.braille_pins.values()):
			if index == 0:
				continue
			NewCell.pi.set_PWM_dutycycle(value, 255*braille_pattern[index-1])
	
		while time.time() <= (t_ini + self.time_on):
			if time.time() < (t_ini + self.time_on/2.0):
				t_current = (2*(10-1)/(self.time_on))*(time.time() - t_ini) + 1 	
				t_ini1 = time.time()
				
			else:				
				t_current = (2*(1-10)/(self.time_on))*(time.time() - t_ini1) + 10
					
			signal_value = (255.0*math.log10(t_current))*(self.power/5.0)
			
			signal_value = NewCell._clamp(signal_value)
			signal.append(signal_value)
			NewCell.pi.set_PWM_dutycycle(self.braille_pins["signal_pin"], signal_value)
			
		NewCell.pi.set_PWM_dutycycle(self.braille_pins["signal_pin"], 0)
		for index, value in enumerate(self.braille_pins.values()):
			if index == 0:
				continue
			NewCell.pi.set_PWM_dutycycle(value, 0)

		time.sleep(self.time_off)

		return signal

	def _signal_exp(self, braille_pattern: list) -> list:
		"""Activate a braille pattern with a exponential signal for time_on seconds and then waits for time_off seconds.

		Parameters
		----------
		braille_pattern : list(bool)
			6-value braille pattern list, 1 means the braille dot is activated and 0 means it isn't.

		Returns
		-------
		signal: list
			List with the values the signal takes over time.
		"""

		signal = []
		t_ini = time.time()
		
		for index, value in enumerate(self.braille_pins.values()):
			if index == 0:
				continue
			NewCell.pi.set_PWM_dutycycle(value, 255*braille_pattern[index-1])
		
		while time.time() <= (t_ini + self.time_on):
			if time.time() < (t_ini + self.time_on/2.0):
				t_current = (2*(math.log(10)-(-math.log(10)))/(self.time_on))*(time.time() - t_ini) + (-math.log(10)) 
				t_ini1 = time.time()
				
			else:
				# Second half of the cycle, t_current is calculated from time_on/2 to time_on
				
				t_current = (2*((-math.log(10))-math.log(10))/(self.time_on))*(time.time() - t_ini1) + math.log(10) # In this line we remap the time so that is goes from ln(10) to -ln(10)
					
					
			signal_value = (25.5*math.exp(t_current))*(self.power/5.0)
			
			signal_value = NewCell._clamp(signal_value)
			signal.append(signal_value)
			NewCell.pi.set_PWM_dutycycle(self.braille_pins["signal_pin"], signal_value)
			
		NewCell.pi.set_PWM_dutycycle(self.braille_pins["signal_pin"], 0)
		for index, value in enumerate(self.braille_pins.values()):
			if index == 0:
				continue
			NewCell.pi.set_PWM_dutycycle(value, 0)

		time.sleep(self.time_off)

		return signal

	def _signal_click(self, braille_pattern: list) -> list:
		"""Activate a braille pattern with a click signal (first half logarithmic, second half exponential) for time_on seconds and then waits for time_off seconds.

		Parameters
		----------
		braille_pattern : list(bool)
			6-value braille pattern list, 1 means the braille dot is activated and 0 means it isn't.

		Returns
		-------
		signal: list
			List with the values the signal takes over time.
		"""
		
		signal = []
		t_ini = time.time()
		
		for index, value in enumerate(self.braille_pins.values()):
			if index == 0:
				continue
			NewCell.pi.set_PWM_dutycycle(value, 255*braille_pattern[index-1])
		
		while time.time() <= (t_ini + self.time_on):
			
			if time.time() < (t_ini + self.time_on/2.0):				
				t_current = (2*(10-1)/(self.time_on))*(time.time() - t_ini) + 1 
				signal_value = (255.0*math.log10(t_current))*(self.power/5.0)
				t_ini1 = time.time()
				
			else:				
				t_current = (2*((-math.log(10))-math.log(10))/(self.time_on))*(time.time() - t_ini1) + math.log(10) # In this line we remap the time so that is goes from -ln(10) to ln(10)
				signal_value = (25.5*math.exp(t_current))*(self.power/5.0)
					
			signal_value = NewCell._clamp(signal_value)
			signal.append(signal_value)
			NewCell.pi.set_PWM_dutycycle(self.braille_pins["signal_pin"], signal_value)
			
		NewCell.pi.set_PWM_dutycycle(self.braille_pins["signal_pin"], 0)
		for index, value in enumerate(self.braille_pins.values()):
			if index == 0:
				continue
			NewCell.pi.set_PWM_dutycycle(value, 0)

		time.sleep(self.time_off)

		return signal

	def _signal_revclick(self, braille_pattern: list) -> list:
		"""Activate a braille pattern with a click signal (first half exponential, second half logarithmic) for time_on seconds and then waits for time_off seconds.

		Parameters
		----------
		braille_pattern : list(bool)
			6-value braille pattern list, 1 means the braille dot is activated and 0 means it isn't.

		Returns
		-------
		signal: list
			List with the values the signal takes over time.
		"""

		signal = []
		t_ini = time.time()
		
		for index, value in enumerate(self.braille_pins.values()):
			if index == 0:
				continue
			NewCell.pi.set_PWM_dutycycle(value, 255*braille_pattern[index-1])
		
		while time.time() <= (t_ini + self.time_on):
			if time.time() < (t_ini + self.time_on/2.0):
				t_current = (2*(math.log(10)-(-math.log(10)))/(self.time_on))*(time.time() - t_ini) + (-math.log(10))
				t_ini1 = time.time()
				signal_value = (25.5*math.exp(t_current))*(self.power/5.0)
			else:
				t_current = (2*(1-10)/(self.time_on))*(time.time() - t_ini1) + 10
				signal_value = (255.0*math.log10(t_current))*(self.power/5.0)
					
			signal_value = NewCell._clamp(signal_value)
			signal.append(signal_value)
			NewCell.pi.set_PWM_dutycycle(self.braille_pins["signal_pin"], signal_value)
			
		NewCell.pi.set_PWM_dutycycle(self.braille_pins["signal_pin"], 0)
		for index, value in enumerate(self.braille_pins.values()):
			if index == 0:
				continue
			NewCell.pi.set_PWM_dutycycle(value, 0)

		time.sleep(self.time_off)

		return signal
  
	@staticmethod
	def _translator(letter: str) -> list:
		"""Translate a letter to a braille dot pattern, Ex. "a" -> [1, 0, 0, 0, 0, 0], " " -> [0, 0, 0, 0, 0, 0]

		Parameters
		----------
		letter : str
			Input letter to be translated.

		Returns
		-------
		braille_letter: list
			6-value boolean list representing  the input letter
		"""

		letter = letter.lower()
		if letter == "ñ":
			clean_letter = "ñ"
		else:
			clean_letter = unicodedata.normalize('NFD', letter).encode('ascii', 'ignore').decode("utf-8")

		regular_alphabet = " abcdefghijklmnñopqrstuvwxyz"
		braille_alphabet = [[0,0,0,0,0,0],[1,0,0,0,0,0],[1,1,0,0,0,0],[1,0,0,1,0,0],[1,0,0,1,1,0],[1,0,0,0,1,0],[1,1,0,1,0,0],[1,1,0,1,1,0],[1,1,0,0,1,0],[0,1,0,1,0,0],[0,1,0,1,1,0],[1,0,1,0,0,0],[1,1,1,0,0,0],[1,0,1,1,0,0],[1,0,1,1,1,0],[1,1,0,1,1,1],[1,0,1,0,1,0],[1,1,1,1,0,0],[1,1,1,1,1,0],[1,1,1,0,1,0],[0,1,1,1,0,0],[0,1,1,1,1,0],[1,0,1,0,0,1],[1,1,1,0,0,1],[0,1,0,1,1,1],[1,0,1,1,0,1],[1,0,1,1,1,1],[1,0,1,0,1,1]]

		braille_dictionary = dict(zip(regular_alphabet, braille_alphabet))
		return braille_dictionary[clean_letter]

	def trigger(self, dot_pattern: list):
		"""Activate the braille cell according to the cell parameters and the dot pattern
		
		Parameters
		----------
		dot_pattern : list
			Boolean braille pattern where 1 means active and zero means unactive, Ex. [1, 0, 1, 1, 0, 0]
		"""

		if self.signal_type == 1:
			self._signal_square(dot_pattern)
			
		elif self.signal_type == 2:
			self._signal_triangle(dot_pattern)
			
		elif self.signal_type == 3:
			self._signal_ramp(dot_pattern)
						
		elif self.signal_type == 4:
			self._signal_exp(dot_pattern)
			
		elif self.signal_type == 5:
			self._signal_log(dot_pattern)
			
		elif self.signal_type == 6:
			self._signal_sine(dot_pattern)			

		elif self.signal_type == 7:			
			self._signal_click(dot_pattern)

		elif self.signal_type == 8:			
			self._signal_revclick(dot_pattern)			
		else:
			print("ERROR: Wrong signal selector")

	def generator(self):
		"""Activate each dot in the braille cell consecutively."""
		
		for active_dot in range(6):
			vector_generador = [0,0,0,0,0,0]
			vector_generador[active_dot] = 1
			self.trigger(vector_generador)
		
	def writer(self, text: str):
		"""Write the text in the braille cell activating consecutively each alphanumer letter.

		Parameters
		----------
		text : str
			String to be written in the braille cell
		"""
		
		for letter in text:
			if letter.isalpha() or letter == " ":
				caracter_braille = self._translator(letter)
				self.trigger(caracter_braille)
			else:
				pass

	def random_letter(self) -> str:
		"""Write a random letter in the braille cell

		Returns
		-------
		random_letter: str
			Random letter from the alphabet including ñ
		"""

		alfabeto_regular = "abcdefghijklmnñopqrstuvwxyz"
		letter = alfabeto_regular[random.randint(0,26)]
		braille_letter = self._translator(letter)
		self.trigger(braille_letter)

		return [letter, braille_letter]

	def random_pattern(self) -> list:
		"""Generate a random braille pattern and activate it in the braille cell."""
		
		vector_random = [0,0,0,0,0,0]
		
		for dot in range(6):
			vector_random[dot] = random.randint(0,1)
		
		self.trigger(vector_random)

		return vector_random