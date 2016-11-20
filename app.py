import os
import base64
import hashlib
import numpy

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_api import status
from flask_restful import Resource, Api

from consts import *
from errors import *

app = Flask("differ")
# Load config for app
if __name__ == '__main__':
	app.config.from_object('consts.ProductionConfig')
else:
	app.config.from_object('consts.TestingConfig')
api = Api(app, catch_all_404s = True)
db = SQLAlchemy(app)

class Data(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	task_id = db.Column(db.Integer)
	side = db.Column(db.String(10))
	sha = db.Column(db.String(64), default = "")

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

class Record(object):
	"""
	Class describes storored objects
	It has base64 encoded data, sha and fs path params
	Record is stored as sha in DB and as file on fs
	"""
	def __init__(self, storage = app.config["RECORD_STORAGE_PATH"], \
				data = "", sha = ""):
		if not data and not sha:
			raise EmptyRecord("Empty data is not permitted for storing")
		if not os.path.exists(storage):
			os.makedirs(storage)
		self.storage = storage
		self.data = data
		self.sha = sha
		self.path = ""

	def _getPathFromSha(self):
		"""
		Store file on fs the way to not damage in case of big amount of files
		"""
		x = self.sha
		return os.path.join(self.storage, x[:2], x[2:4], x[4:6], x)

	def getData(self):
		"""
		Returns decoded data
		"""
		if self.data:
			return self.data
		if not self.path:
			self.path = self._getPathFromSha()
		with open(self.path, "rb") as f:
			self.data = base64.b64encode(f.read())
		return self.data

	def getPath(self):
		"""
		Return filepath for record
		"""
		if self.path:
			return self.path
		if self.sha:
			return self._getPathFromSha()
		h = hashlib.new("sha256")
		h.update(base64.b64decode(self.data))
		self.sha = h.hexdigest()
		self.path = self._getPathFromSha()
		return self.path

	def getSha(self):
		"""
		Return file sha that is suppored to be stored in DB
		"""
		if self.sha:
			return self.sha
		if self.path:
			return "".join(self.path.split(os.path.sep))
		h = hashlib.new("sha256")
		h.update(base64.b64decode(self.data))
		self.sha = h.hexdigest()
		return self.sha

	def saveOnDisk(self):
		"""
		Store record on fs
		"""
		self.path = self.getPath()
		self.data = self.getData()
		dirname = os.path.dirname(self.path)
		if not os.path.exists(dirname):
			os.makedirs(dirname)
		with open(self.path, "wb") as f:
			f.write(base64.b64decode(self.data))

	def removeFromDisk(self):
		"""
		On record replacement new file will be stored on another location
		This method is needed to remove old useless files
		"""
		self.path = self.getPath()
		if os.path.exists(self.path):
			os.unlink(self.path)

class Accepter(Resource):
	"""
	Controller for receiving left and right data
	Request should provide task ID
	If task_id already exists then re-create data
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
			# If data does not exist then create new one
			data = Data(task_id, side)
			db.session.add(data)
		else:
			# If data exists then remove old file on disk first
			old_record = Record(sha = data.sha)
			old_record.removeFromDisk()
		record = Record(data = json_data["data"])
		# Store decoded file on a disk
		record.saveOnDisk()
		# Store file sha in DB
		data.sha = record.getSha()
		db.session.commit()
		return {
			"message": "Created",
			"task_id": task_id,
			"side": side
		}, status.HTTP_201_CREATED

class Result(Resource):
	"""
	Controller that returns result of data comparison
	Request should provide task ID
	Returns error if data does not exist
	Example:
		curl http://127.0.0.1:5000/v1/diff/123 -X GET
	"""
	def get(self, task_id):
		"""
		Method is looking for task ID on storage and takes corresponding data
		After that method compares binary data and return result
		- if data are equal, return that
		- if data has different size, return that
		- if data are differ but equal size, returns diff in the next format:
		{"offset1": "length1", "offset2": "lenght2", ...}
		"""
		db_diffs = Diff.query.filter_by(task_id = task_id).all()
		if db_diffs:
			# Return cached diff from DB
			binary_diff = {}
			for db_diff in db_diffs:
				binary_diff[db_diff.offset] = db_diff.lenght
			return {
				"message": "OK",
				"task_id": task_id,
				"diff": {
					"equal_content": "false",
					"equal_size": "true",
					"binary_diff": binary_diff
				}
			}, status.HTTP_200_OK

		query = Data.query.filter_by(task_id = task_id)
		data = query.all()
		if not data:
			return {
				"message": "Task %s is not found on server" % task_id
			}, status.HTTP_404_NOT_FOUND
		if len(data) == 1:
			side = data[0].side
			return {
				"message": "Only %s data is found on server" % side
			}, status.HTTP_500_INTERNAL_SERVER_ERROR
		if len(data) > 2:
			return {
				"message": "Too many data for one task %s" % task_id
			}, status.HTTP_500_INTERNAL_SERVER_ERROR
		sha_left = query.filter_by(side = LEFT).one().sha
		record_left = Record(sha = sha_left)
		sha_right = query.filter_by(side = RIGHT).one().sha
		record_right = Record(sha = sha_right)
		diff = getDiff(record_left.getPath(), record_right.getPath())
		# Add diff to DB as cache
		for offset, length in diff["binary_diff"].items():
			db.session.add(Diff(task_id, offset, length))
		db.session.commit()
		return {
			"message": "OK",
			"task_id": task_id,
			"diff": diff
		}, status.HTTP_200_OK

def getDiff(file1, file2):
	"""
	Main function that compares actual binary files
	Should return json result according to requirements
	"""
	byte_array1 = numpy.fromfile(file1, numpy.int8)
	byte_array2 = numpy.fromfile(file2, numpy.int8)
	diff_offsets = numpy.where(byte_array1 != byte_array2)[0]
	if len(diff_offsets) == 0:
		return {
			"equal_content": "true",
			"equal_size": "true",
			"binary_diff": {}
		}
	if len(byte_array1) != len(byte_array2):
		return {
			"equal_content": "false",
			"equal_size": "false",
			"binary_diff": "null"
		}
	# transform diff offsets to binary_diff
	# for example, [3, 4, 5, 7, 8] -> {3:3, 7:2}
	offset = diff_offsets[0]
	binary_diff = {offset: 1}
	for i in range(1, len(diff_offsets)):
		if diff_offsets[i - 1] == diff_offsets[i] - 1:
			binary_diff[offset] += 1
		else:
			offset = diff_offsets[i]
			binary_diff[offset] = 1
	return {
		"equal_content": "false",
		"equal_size": "true",
		"binary_diff": binary_diff
	}

api.add_resource(Result, "%s/<int:task_id>" % BASEURL)
api.add_resource(Accepter, "%s/<int:task_id>/<any(%s, %s):side>" % (BASEURL, LEFT, RIGHT))

if __name__ == '__main__':
	app.run(debug = True)
