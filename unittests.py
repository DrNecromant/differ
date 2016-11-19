import unittest

from app import app
from flask_api import status
from consts import *

class TestDiffer(unittest.TestCase):
	"""
	Unittests for differ
	"""
	def setUp(self):
		self.client = app.test_client()

	def _getUrl(self, side):
		return "%s/%s/%s" % (BASEURL, self.task, side)

	def getTaskUrl(self):
		return "%s/%s" % (BASEURL, self.task)

	def getLeftFileUrl(self):
		return self._getUrl(LEFT)

	def getRightFileUrl(self):
		return self._getUrl(RIGHT)

	def getFakeFileUrl(self):
		return self._getUrl("fake")

	def testNoFiles(self):
		"""
		Try to get difference if there is no files for task
		Returns 404 for task URL
		"""
		self.task = 1
		res = self.client.get() 
		self.assertEquals(res.status_code, status.HTTP_404_NOT_FOUND)

	def testAddEmptyFile(self):
		"""
		Try to send json without "data" key
		Returns 400 for file url
		"""
		self.task = 2
		res = self.client.put(self.getLeftFileUrl(), data = '{}')
		self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

	def testAddFiles(self):
		"""
		Try to add files to compare
		Returns 201 for file urls
		"""
		self.task = 3
		res = self.client.put(self.getLeftFileUrl(), data = '{"data": "filedata"}')
		self.assertEquals(res.status_code, status.HTTP_201_CREATED)
		res = self.client.put(self.getRightFileUrl(), data = '{"data": "filedata"}')
		self.assertEquals(res.status_code, status.HTTP_201_CREATED)

	def testAddFakeFile(self):
		"""
		Try to add file different from left or right url
		Returns 404 for fake file url
		"""
		self.task = 4
		res = self.client.put(self.getFakeFileUrl(), data = '{"data": "filedata"}')
		self.assertEquals(res.status_code, status.HTTP_404_NOT_FOUND)

	def testMissedFile(self):
		"""
		Try to run comparison task with one file only
		Returns 505 for task url
		"""
		self.task = 5
		res = self.client.put(self.getRightFileUrl(), data = '{"data": "filedata"}')
		res = self.client.get(self.getTaskUrl())
		self.assertEquals(res.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

	def testDiff(self):
		"""
		Try to diff existed files
		Returns 200 for task url
		"""
		self.task = 6
		res = self.client.put(self.getLeftFileUrl(), data = '{"data": "filedata1"}')
		res = self.client.put(self.getRightFileUrl(), data = '{"data": "filedata2"}')
		res = self.client.get(self.getTaskUrl())
		self.assertEquals(res.status_code, status.HTTP_200_OK)
		self.assertEquals(eval(res.get_data())["task_id"], self.task)

	def tearDown(self):
		pass

if __name__ == "__main__":
	suite = unittest.TestLoader().loadTestsFromTestCase(TestDiffer)
	unittest.TextTestRunner(verbosity = 2).run(suite)
