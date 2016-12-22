#!local/bin/python
#
# File: detect_door.py
#
#	Detects opening or closing of garage man door or main door and sends event
#	using REST to door server.  Door event is formatted using JSON.  Format is:
#
#		event_data = {'time': event_time, 'door': door, 'event': event}
#		
#	The event is pushed onto a queue and a separate thread is used to service
#	the queue and send the events to the door server.  The 2 threads are:
#
#		Main
#		1. listen for event
#		2. get event
#		3. put event on queue
#		4. repeat
#
#		Thread 1
#		1. check queue for events
#		2. if any events in queue, try sending to server
#		3. remove event from queue
#		4. repeat

from config_door import *
from config_client import *
import time
from datetime import datetime
import RPi.GPIO as io
import threading
import errno
import logging
import httplib2
import os
from flask import Flask, request, json, jsonify
import Queue

# define ServiceQ thread which services the event queue
class ServiceQ(threading.Thread):
	"""Service event Queue"""

	def run(self):

		print "Starting ServiceQ thread ..."
		# define REST machinery for sending event to door server
		httplib2.debuglevel     = 0
		http                    = httplib2.Http()
		content_type_header     = "application/json"
		url = "http://" + door_server + ":5000/api/door_event"
		headers = {'Content-Type': content_type_header}

		# loop to check for events
		while True:

			# while the event queue is not empty, try to send events to door server
			if not event_queue.empty():
				# get an event off the queue
				event_data = event_queue.get()

				# send to door server
				empty = rest_conn(door_server, "5000", "/api/door_event", "POST", event_data)


# MAIN

# Configure log file and log program restart
logger = log_restart(os.path.basename(__file__))

# For each door, get initial state
state = get_doors_state()	# keep track of current state of each door
for door in doors:
	logger.info('INIT: ' + door + ',' + state[door])	# log initial door state
	print 'INIT: ' + door + ',' + state[door]	# log initial door state

# Create event queue
event_queue = Queue.Queue()

# Start thread to service event queue
ServiceQ().start()

# Loop and wait for a new event - only send event when a change of state occurs
while True:
	for door in doors:
		event = ''
		if io.input(pin[door]):			# door open
			if state[door] == CLOSED:	# if door was previously closed, send open message
				state[door] = OPEN
				event = OPEN
		else:					# door closed
			if state[door] == OPEN:		# if door was previously open, send closed message
				state[door] = CLOSED
				event = CLOSED

		# if an event has occurred, put event on event queue
		if event:
#			event_time = datetime.now()
			event_time = time.time()
			event_data = {'timestamp': event_time, 'door': door, 'event': event}
			print "Putting Event Data on Q:"
			print event_data
			event_queue.put(event_data)
			if not event_queue.empty():
				print "Queue Size: " + str(event_queue.qsize())

			logger.info('EVENT: ' + door + ',' + state[door])	# log event
