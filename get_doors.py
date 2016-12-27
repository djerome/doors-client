#!local/bin/python
#
# File: get_doors.py
#
#	Gets state of all doors and returns it to client
#

from config_door_detect import *
import os
from flask import Flask, jsonify

# Configure log file
log_setup(os.path.basename(__file__))

app = Flask(__name__)


# URL for getting state of doors
@app.route("/api/get_doors", methods=['GET'])
def api_get_doors():

	print "Getting door state"
	return jsonify(get_doors_state())

if __name__ == '__main__':
    app.run(host = '0.0.0.0', debug = True, use_reloader=False)
