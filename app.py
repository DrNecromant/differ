from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_api import status
from flask_restful import Resource, Api
from consts import *
from errors import *

app = Flask("differ")
api = Api(app, catch_all_404s = True)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///production.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
db = SQLAlchemy(app)

class Data(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	task_id = db.Column(db.Integer)
	side = db.Column(db.String(10))
	data = db.Column(db.String(100), default = "")

	def __init__(self, task_id, side):
		self.task_id = task_id
		self.side = side
		if side not in (LEFT, RIGHT):
			raise InvalidValue("Invalid side column value: %s" % side)

class Diff(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	task_id = db.Column(db.Integer)
	offset = db.Column(db.Integer)
	length = db.Column(db.Integer)

	def __init__(self, task_id, offset, length):
		self.task_id = task_id
		self.offset = offset
		self.length = length

db.create_all()

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
			return {
				"message": "Bad request. json 'data' key is requied."
			}, status.HTTP_400_BAD_REQUEST
		data = Data.query.filter_by(task_id = task_id, side = side).first()
		if not data:
			data = Data(task_id, side)
			db.session.add(data)
		data.data = json_data["data"]
		db.session.commit()
		return {
			"message": "Created",
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
		query = Data.query.filter_by(task_id = task_id)
		files = query.all()
		if not files:
			return {
				"message": "Task %s is not found on server" % task_id
			}, status.HTTP_404_NOT_FOUND
		if len(files) == 1:
			side = files[0].side
			return {
				"message": "Only %s data is found on server" % side
			}, status.HTTP_500_INTERNAL_SERVER_ERROR
		if len(files) > 2:
			return {
				"message": "Too many data for one task %s" % task_id
			}, status.HTTP_500_INTERNAL_SERVER_ERROR
		data_left = query.filter_by(side = LEFT).one().data
		data_right = query.filter_by(side = RIGHT).one().data
		# Process data here
		return {
			"message": "OK",
			"task_id": task_id,
			"diff": "TBD"
		}, status.HTTP_200_OK

api.add_resource(Result, "%s/<int:task_id>" % BASEURL)
api.add_resource(Accepter, "%s/<int:task_id>/<any(%s, %s):side>" % (BASEURL, LEFT, RIGHT))

if __name__ == '__main__':
    app.run(debug = True)
