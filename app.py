from flask import Flask, request
from flask.ext.api import status
from flask_restful import Resource, Api
from consts import *

app = Flask("differ")
api = Api(app, catch_all_404s = True)

# Temporarily storage for tasks in memory
# Will be replace with sqlite DB soon
tasks = dict()

class Accepter(Resource):
	"""
	Controller for receiving left and right files
	Request should provide task ID
	If task_id already exists then re-create file
	Example:
		curl http://127.0.0.1:5000/v1/diff/123/left -X PUT -d '{"data": "foobar"}'
	"""
	def put(self, task_id, side):
		"""
		Fetch json data from body ignoring Content-Type header by force flag
		If body is not json flask restfull api automatically handles that
		Put fetched data to storage for further comparison
		"""
		json_data = request.get_json(force = True)
		if not json_data.has_key("data"):
			return {"message": "Bad request. json 'data' key is requied."}, status.HTTP_400_BAD_REQUEST
		if not tasks.has_key(task_id):
			tasks[task_id] = {}
		if tasks[task_id].has_key(side):
			message = "Replaced"
		else:
			message = "Created"
		tasks[task_id][side] = json_data["data"]
		return {
			"message": message,
			"task_id": task_id,
			"side": side
		}, status.HTTP_201_CREATED

class Result(Resource):
	"""
	Controller that returns result of file comparison
	Request should provide task ID
	Returns error if file or files do not exist
	Example:
		curl http://127.0.0.1:5000/v1/diff/123 -X GET
	"""
	def get(self, task_id):
		"""
		Method is looking for task ID on storage and takes corresponding files
		After that method compares binary files and return result
		- if files are equal, return that
		- if files has different size, return that
		- if files are differ but equal size, returns diff in the next format:
		{"offset1": "length1", "offset2": "lenght2", ...}
		"""
		error_message = "Requied task_id are missed on server"
		if not tasks.has_key(task_id):
			return {
				"message": "Task %s is not found on server" % task_id
			}, status.HTTP_404_NOT_FOUND
		task = tasks[task_id]
		for side in (LEFT, RIGHT):
			if not task.has_key(side):
				return {
					"message": "Resource %s is not found on server" % side
				}, status.HTTP_500_INTERNAL_SERVER_ERROR
		data_left = task[LEFT]
		data_right = task[RIGHT]
		# Process data here
		return {
			"message": "OK",
			"task_id": task_id,
			"diff": "TBD"
		}, status.HTTP_200_OK

api.add_resource(Result, "/v1/diff/<int:task_id>")
api.add_resource(Accepter, "/v1/diff/<int:task_id>/<any(%s, %s):side>" % (LEFT, RIGHT))

if __name__ == '__main__':
    app.run(debug = True)
