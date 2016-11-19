from flask import Flask, request
from flask_restful import Resource, Api

app = Flask("differ")
api = Api(app)

class Accepter(Resource):
	"""
	Controller for receiving left and right files
	Request should provide task ID
	If task_id already exists then re-create file
	Example:
		curl http://127.0.0.1:5000/v1/diff/123/left -X PUT -d '{"data": "foobar"}'
	"""
	def put(self, task_id, side):
		# fetch json data ignoring Content-Type header by force flag
		json_data = request.get_json(force = True)
		#FIXME: check data key in json
		data = json_data["data"]
		return {
			"task_id": "%s" % task_id,
			"side": "%s" % side,
			"data": "%s" % data
		}

class Result(Resource):
	"""
	Controller that returns result of file comparison
    Request should provide task ID
    Returns error if file or files do not exist
	Example:
		curl http://127.0.0.1:5000/v1/diff/123 -X GET
	"""
	def get(self, task_id):
		return {
			"task_id": "%s" % task_id
		}

api.add_resource(Result, "/v1/diff/<int:task_id>")
api.add_resource(Accepter, "/v1/diff/<int:task_id>/<string:side>")

if __name__ == '__main__':
    app.run(debug = True)
