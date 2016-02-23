#!local/bin/python
#
# File: get_door.py
#
#	Gets state of all doors and returns it to client
#

from config_door import *
import RPi.GPIO as io
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)


# Configure log file
logging.basicConfig(filename=log_file, level=logging.DEBUG, format=log_format, datefmt=date_format)
logging.debug('RESTART DOORS-Get')	# log program restart

# URL for getting state of doors
@app.route("/api/get_doors", methods=['GET'])
def api_get_doors():

	state = {}
	io.setmode(io.BCM)	# set appropriate mode for reading GPIO
	for door in doors:
		io.setup(pin[door], io.IN, pull_up_down=io.PUD_UP)

	for door in doors:

		# get initial state of door
		if io.input(pin[door]):	# door open
			state[door] = OPEN
			print door + " is OPEN"
		else:
			state[door] = CLOSED
			print door + " is CLOSED"

	print "Got state"

	return jsonify(state)

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = True)
