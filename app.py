from flask import Flask, request
from flask.ext.api import status
from flask_restful import Resource, Api
from collections import defaultdict

app = Flask("differ")
api = Api(app, catch_all_404s = True)

# Temporarily storage for tasks in memory
# Will be replace with sqlite DB soon
tasks = defaultdict(dict)

#FIXME: change harcoded error codes with flask consts
#FIXME: change harcoded "left", "right" with consts

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
		"""
		json_data = request.get_json(force = True)
		if not json_data.has_key("data"):
			return {"message": "Bad request. json 'data' key is requied."}, status.HTTP_400_BAD_REQUEST
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
		data_left = tasks[task_id]["left"]
		data_right = tasks[task_id]["right"]
		# Process data here
		return {
			"message": "OK",
			"task_id": task_id
			"diff": "TBD"
		}, stauts.HTTP_200_OK

api.add_resource(Result, "/v1/diff/<int:task_id>")
api.add_resource(Accepter, "/v1/diff/<int:task_id>/<any(right, left):side>")

if __name__ == '__main__':
    app.run(debug = True)
