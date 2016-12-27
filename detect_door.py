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

#from config_door_common import *
#from config_client import *
from config_door_detect import *
import time
import RPi.GPIO as io
import threading
import os
import Queue

# define ServiceQ thread which services the event queue
class ServiceQ(threading.Thread):
	"""Service event Queue"""

	def run(self):

		# loop to check for events
		while True:

			# while the event queue is not empty, try to send events to door server
			if not event_queue.empty():

				# get an event off the queue and send to door server
				event_data = event_queue.get()
				empty = rest_conn(door_server, "5000", "/api/door_event", "POST", event_data)


# MAIN

# Configure log file and log program restart
logger = log_setup(os.path.basename(__file__))

# For each door, get initial state
state = get_doors_state()	# keep track of current state of each door
for door in doors:
	logger.info('INIT: ' + door + ',' + state[door])	# log initial door state

# Create event queue and start thread to service event queue
event_queue = Queue.Queue()
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
			event_time = time.time()
			event_data = {'timestamp': event_time, 'door': door, 'event': event}
			event_queue.put(event_data)
			logger.info('EVENT: ' + door + ',' + state[door])	# log event
