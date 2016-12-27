#
#	config_door_detect.py
#
#	Defines functions and constants used by door detect server only
#

import RPi.GPIO as io
from config_door_common import *

# GPIO pin for each door
pin = {GARAGE: 23, MAN: 24}

def get_doors_state():
	"""Get state of both doors from GPIO pins"""

	### Inputs ###
	#
	#	None
	#
	### Outputs ###
	#
	#	state: dictionary of doors states
	#
	###

	state = {}
	io.setmode(io.BCM)	# set appropriate mode for reading GPIO
	for door in doors:
		io.setup(pin[door], io.IN, pull_up_down=io.PUD_UP)

	for door in doors:

		# get state of door
		if io.input(pin[door]):	# door open
			state[door] = OPEN
		else:
			state[door] = CLOSED

	return state
