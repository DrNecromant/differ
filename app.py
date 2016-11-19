from flask import Flask, request
from flask_restful import Resource, Api

app = Flask("differ")
api = Api(app, catch_all_404s = True)

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
			return {"message": "Bad request. json 'data' key is requied."}, 400
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
api.add_resource(Accepter, "/v1/diff/<int:task_id>/<any(right, left):side>")

if __name__ == '__main__':
    app.run(debug = True)
