#
#	config_door.py
#
#	Defines constants and functions used in door application
#

import httplib2
from flask import json
import logging
from logging.handlers import TimedRotatingFileHandler
import time

# Doors
GARAGE = "Garage"
MAN = "Man"
doors = [GARAGE, MAN]

# door states
OPEN = "Open"
CLOSED = "Closed"

OFF = "Off"
ON = "On"
TIMER = "Timer"
NIGHT = "Night"
VACATION = "Vacation"
ALL = "All"
INFO = "Info"
WARNING = "Warning"
CRITICAL = "Critical"
NONE = "None"
timer_severities = [WARNING, CRITICAL]
init_wait_time = 1
max_wait_time = 8193

# logging constants
log_file = "/var/log/doors/garage.log"
log_format = "%(asctime)s: %(message)s"
#date_format = "%m/%d/%Y %I:%M:%S %p"
date_format = "%m/%d/%Y %X"

# GPIO pin for each door
pin = {GARAGE: 23, MAN: 24}

# Servers and Clients
web_server = "blueberry"
door_server = "cranberry"
detect_server = "strawberry"

def rest_conn(host, port, path, method, data):
	"""Get/send content using REST from/to another host"""

	### Inputs ###
	#
	#	host: host to connect to
	#	port: port on host to communicate with
	#	path: path to rest resource
	#	method: http method being used - usually GET or POST
	#	data: dictionary of data to POST or empty if GET
	#
	### Outputs ###
	#
	#	data retrieved from url
	#
	###

	httplib2.debuglevel     = 0
	http                    = httplib2.Http()
	content_type_header     = "application/json"
	headers = {'Content-Type': content_type_header}
	url = "http://" + host + ":" + port + path

	# get initial state of both doors
	wait_time = init_wait_time
	host_down = True
	while host_down:

		try:
			status = 'OK'
			if method == 'GET':
				response, content = http.request(url, method, headers=headers)
				print "Response:"
				print response
				print "Content:"
				print content
				result =  json.loads(content)
			elif method == 'POST':
				response, content = http.request(url, method, json.dumps(data), headers=headers)
				print "Response:"
				print response
				print "Content:"
				print content
				result = {}
			host_down = False
			logger.info('CONNECT:' + url + ',' + method + ',OK')
			return result
		except:
			status = 'Error'
			print "Error Connecting ..."
			logger.error('CONNECT:' + url + ',' + method + ',Error')
			time.sleep(wait_time)
			if wait_time < max_wait_time:
				wait_time = wait_time + wait_time



def log_restart(script_name):
	"""Setup logger and log restart of script"""

	### Inputs ###
	#
	#	script_name: the filename of the script running
	#
	### Outputs ###
	#
	#	logger: the logger that performs the logging
	#
	###

	# create logger
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.DEBUG)

	# create timed rotating file handler and set level to debug
	fh = TimedRotatingFileHandler(log_file, when='D', interval=30, backupCount=12)
	fh.setLevel(logging.DEBUG)

	# create formatter
	formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

	# add formatter to fh
	fh.setFormatter(formatter)

	# add ch to logger
	logger.addHandler(fh)

	# log program restart
	logger.info('RESTART: ' + script_name)

	return logger
