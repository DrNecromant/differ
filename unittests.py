import os
import unittest
import base64
import hashlib

from app import app, db, Data, Diff, Record
from flask_api import status

from consts import *
from errors import *

db.create_all()

# Create pool of IDs for testing
ids = range(1, 100)

# Create testdata
class TestData(object):
	path1 = "test_data/66/cb/ca/66cbca2264581ba7223adf85b3840a6ef662968bae56acfc91d31961029e3c04"
	data1 = open("test_data/Clare.jpg_data").read()
	sha1 = "66cbca2264581ba7223adf85b3840a6ef662968bae56acfc91d31961029e3c04"
	path2 = "test_data/a4/aa/17/a4aa17e3ba5d2849461a17559b0bae6f1f00a8ccab1a7f17d7f73225f9086fec"
	data2 = open("test_data/Clare_modified.jpg_data").read()
	sha2 = "a4aa17e3ba5d2849461a17559b0bae6f1f00a8ccab1a7f17d7f73225f9086fec"

class TestRecord(unittest.TestCase):
	"""
	Unittest for Record object.
	Testing convering here
	Record object can accept data or sha
	"""
	def setUp(self):
		self.td = TestData()

	def testConvertShaToPath(self):
		r = Record(sha = self.td.sha1)
		path = r.getPath()
		self.assertEquals(path, self.td.path1)

	def testConvertDataToPath(self):
		r = Record(data = self.td.data1)
		path = r.getPath()
		self.assertEquals(path, self.td.path1)

	def testConvertShaToData(self):
		r = Record(sha = self.td.sha1)
		data = r.getData()
		self.assertEquals(data, self.td.data1)

	def testConvertDataToSha(self):
		r = Record(data = self.td.data1)
		sha = r.getSha()
		self.assertEquals(sha, self.td.sha1)

	def testSaveDataOnDisk(self):
		"""
		Store data to disk
		Check path and sha
		"""
		r = Record(data = self.td.data1)
		r.path = "test_data/fake"
		if os.path.exists(r.path):
			os.unlink(r.path)
		r.saveOnDisk()
		self.assertTrue(os.path.exists(r.path))

	def testRemoveFileFromDisk(self):
		"""
		Check record can remove file from disk
		"""
		r = Record(data = "fake")
		r.path = "test_data/fake"
		with open(r.path, 'w') as f:
			f.write("fake")
		r.removeFromDisk()
		self.assertFalse(os.path.exists(r.path))

class TestDB(unittest.TestCase):
	"""
	Unittests for db
	"""
	def setUp(self):
		pass

	def testData(self):
		"""
		Try to create record in a table Data
		"""
		data = Data(task_id = ids.pop(), side = "left")
		db.session.add(data)
		data.sha = "somedata"
		db.session.commit()

	def testInvalidData(self):
		"""
		Try to create record in a table Data
		"""
		try:
			data = Data(task_id = ids.pop(), side = "fake")
		except InvalidValue:
			return
		raise Exception("fake value is not acceptable for side column")

	def testDiff(self):
		"""
		Try to create record in a table Diff
		"""
		diff = Diff(task_id = ids.pop(), offset = 10, length = 30)
		db.session.add(diff)
		db.session.commit()

	def tearDown(self):
		pass

class TestEndpoints(unittest.TestCase):
	"""
	Unittests for endpoints
	"""
	def setUp(self):
		self.client = app.test_client()
		self.td = TestData()

	def _getUrl(self, side):
		return "%s/%s/%s" % (BASEURL, self.task, side)

	def getTaskUrl(self):
		return "%s/%s" % (BASEURL, self.task)

	def getLeftDataUrl(self):
		return self._getUrl(LEFT)

	def getRightDataUrl(self):
		return self._getUrl(RIGHT)

	def getFakeDataUrl(self):
		return self._getUrl("fake")

	def testNoData(self):
		"""
		Try to get difference if there is no data for task
		Returns 404 for task URL
		"""
		self.task = ids.pop()
		res = self.client.get(self.getTaskUrl())
		self.assertEquals(res.status_code, status.HTTP_404_NOT_FOUND)

	def testAddEmptyData(self):
		"""
		Try to send json without "data" key
		Returns 400 for data url
		"""
		self.task = ids.pop()
		res = self.client.put(self.getLeftDataUrl(), data = '{}')
		self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

	def testAddData(self):
		"""
		Try to add data to compare
		Returns 201 for data urls
		"""
		self.task = ids.pop()
		res = self.client.put(self.getLeftDataUrl(), data = '{"data": "%s"}' % self.td.data1)
		self.assertEquals(res.status_code, status.HTTP_201_CREATED)
		res = self.client.put(self.getRightDataUrl(), data = '{"data": "%s"}' % self.td.data2)
		self.assertEquals(res.status_code, status.HTTP_201_CREATED)

	def testAddFakeData(self):
		"""
		Try to add data by different url
		Returns 404 for fake data url
		"""
		self.task = ids.pop()
		res = self.client.put(self.getFakeDataUrl(), data = '{"data": "%s"}' % self.td.data1)
		self.assertEquals(res.status_code, status.HTTP_404_NOT_FOUND)

	def testMissedData(self):
		"""
		Try to run comparison task with one data only
		Returns 505 for task url
		"""
		self.task = ids.pop()
		res = self.client.put(self.getRightDataUrl(), data = '{"data": "%s"}' % self.td.data2)
		res = self.client.get(self.getTaskUrl())
		self.assertEquals(res.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

	def testDiff(self):
		"""
		Try to diff existed data
		Returns 200 for task url
		"""
		self.task = ids.pop()
		res = self.client.put(self.getLeftDataUrl(), data = '{"data": "%s"}' % self.td.data1)
		res = self.client.put(self.getRightDataUrl(), data = '{"data": "%s"}' % self.td.data2)
		res = self.client.get(self.getTaskUrl())
		self.assertEquals(res.status_code, status.HTTP_200_OK)
		self.assertEquals(eval(res.get_data())["task_id"], self.task)

	def tearDown(self):
		pass

if __name__ == "__main__":
	suites = list()
	for test in (TestRecord, TestDB, TestEndpoints):
		suites.append(unittest.TestLoader().loadTestsFromTestCase(test))
	suite = unittest.TestSuite(suites)
	results = unittest.TextTestRunner(verbosity = 2).run(suite)
