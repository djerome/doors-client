#!local/bin/python
#
# File: detect_door.py
#
#	Detects opening or closing of garage man door or main door and sends event using REST to server
#

from config_door import *
import datetime
import RPi.GPIO as io
import threading
import errno
import logging
import httplib2
import os
from flask import Flask, request, json, jsonify


# Configure log file
logging.basicConfig(filename=log_file, level=logging.DEBUG, format=log_format, datefmt=date_format)
logging.debug('RESTART DOORS-'+os.path.basename(__file__))	# log program restart

# Initialize GPIO
io.setmode(io.BCM)	# set appropriate mode for reading GPIO
for door in doors:
	io.setup(pin[door], io.IN, pull_up_down=io.PUD_UP)

# For each door, get initial state
state = {}	# keep track of current state of each door
for door in doors:

	# get initial state of door
	if io.input(pin[door]):	# door open
		state[door] = OPEN
	else:
		state[door] = CLOSED

# Loop and wait for a new event - only send event when a change of state occurs
while True:
	for door in doors:
		event = ''
		if io.input(pin[door]):			# door open
			if state[door] == CLOSED:	# if door was previously closed, send open message
				state[door] = OPEN
				event = OPEN
		else:
			if state[door] == OPEN:		# if door was previously open, send closed message
				state[door] = CLOSED
				event = CLOSED

		if event:
			timestamp = datetime.datetime.now()
#			timestamp = str(time.time())
			httplib2.debuglevel     = 0
			http                    = httplib2.Http()
			content_type_header     = "application/json"
			url = "http://" + door_server + ":5000/api/door_event"

			data = {'door': door, 'event': event}

			event_str = str(timestamp) + ',' + door + ',' + event
			headers = {'Content-Type': content_type_header}

			server_down = True
			while server_down:
				try:
					print "Sending data to " + door_server
		        		response, content = http.request(url, 'POST', json.dumps(data), headers=headers)

					# log OK message
					log_str = event_str + ',OK'
					logging.debug(log_str)

					server_down = False

				# if error
				except:
					print "Error Connecting"
					log_str = event_str + ',ERROR'
					logging.debug(log_str)

					# keep doubling wait time on every failure up to max_wait_time
					time.sleep(wait_time)
					if wait_time < max_wait_time:
						wait_time = wait_time + wait_time
