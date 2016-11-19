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
	
	def testNoFiles(self):
		res = self.client.get("/v1/diff/1") 
		self.assertEquals(res.status_code, status.HTTP_404_NOT_FOUND)

	def testAddEmptyFile(self):
		res = self.client.put("/v1/diff/2/left", data = '{}')
		self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

	def testAddFiles(self):
		res = self.client.put("/v1/diff/3/left", data = '{"data": "filedata"}')
		self.assertEquals(res.status_code, status.HTTP_201_CREATED)
		res = self.client.put("/v1/diff/3/right", data = '{"data": "filedata"}')
		self.assertEquals(res.status_code, status.HTTP_201_CREATED)

	def testAddFakeFile(self):
		res = self.client.put("/v1/diff/4/fake", data = '{"data": "filedata"}')
		self.assertEquals(res.status_code, status.HTTP_404_NOT_FOUND)

	def testMissedFile(self):
		res = self.client.put("/v1/diff/5/right", data = '{"data": "filedata"}')
		res = self.client.get("/v1/diff/5")
		self.assertEquals(res.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

	def testDiff(self):
		res = self.client.put("/v1/diff/6/left", data = '{"data": "filedata1"}')
		res = self.client.put("/v1/diff/6/right", data = '{"data": "filedata2"}')
		res = self.client.get("/v1/diff/6")
		self.assertEquals(res.status_code, status.HTTP_200_OK)
		self.assertEquals(eval(res.get_data())["task_id"], 6)

	def tearDown(self):
		pass

if __name__ == "__main__":
	suite = unittest.TestLoader().loadTestsFromTestCase(TestDiffer)
	unittest.TextTestRunner(verbosity = 2).run(suite)
