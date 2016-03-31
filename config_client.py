#
#	config_client.py
#
#	Defines constants used in client door application
#

import RPi.GPIO as io
from config_door import OPEN, CLOSED, doors, pin

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
