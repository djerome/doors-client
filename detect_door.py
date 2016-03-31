#!local/bin/python
#
# File: detect_door.py
#
#	Detects opening or closing of garage man door or main door and sends event using REST to server
#

from config_door import *
from config_client import *
import time
import RPi.GPIO as io
import threading
import errno
import logging
import httplib2
import os
from flask import Flask, request, json, jsonify


# Configure log file and log program restart
log_restart(os.path.basename(__file__))

# For each door, get initial state
state = get_doors_state()	# keep track of current state of each door
for door in doors:
	logging.debug('INIT: ' + door + ',' + state[door])	# log initial door state

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
			logging.debug('EVENT: ' + door + ',' + state[door])	# log receipt of event
			httplib2.debuglevel     = 0
			http                    = httplib2.Http()
			content_type_header     = "application/json"
			url = "http://" + door_server + ":5000/api/door_event"

			data = {'door': door, 'event': event}

			headers = {'Content-Type': content_type_header}

			server_down = True
			while server_down:
				try:
		        		response, content = http.request(url, 'POST', json.dumps(data), headers=headers)
					print "Response:"
				        print (response)
					print "Content:"
			       		print (content)

					# log OK message
					logging.debug('CONNECT-Send: ' + door_server + ',OK')	# log successful transmission of event

					server_down = False

				# if error
				except:
					print "Error Connecting"
					logging.debug('CONNECT-Send: ' + door_server + ',ERROR')	# log unsuccessful transmission of event

					# keep doubling wait time on every failure up to max_wait_time
					time.sleep(wait_time)
					if wait_time < max_wait_time:
						wait_time = wait_time + wait_time
