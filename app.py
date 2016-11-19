from flask import Flask
from flask_restful import Resource, Api

app = Flask("differ")
api = Api(app)

class Accepter(Resource):
	# Controller for receiving left and right files
	# Request should provide task ID
	# If task_id already exists then re-create file
	def put(self, task_id, side):
		return {
			"task_id": "%s" % task_id,
			"side": "%s" % side
		}

class Result(Resource):
	# Controller that returns result of file comparison
    # Request should provide task ID
    # Returns error if file or files do not exist
	def get(self, task_id):
		return {
			"task_id": "%s" % task_id
		}

api.add_resource(Result, "/v1/diff/<int:task_id>")
api.add_resource(Accepter, "/v1/diff/<int:task_id>/<string:side>")

if __name__ == '__main__':
    app.run(debug = True)
