import os
import unittest
import base64
import requests

from testdata import *
from consts import *

class TestDiffer(unittest.TestCase):
	"""
	Integration test for differ app
	"""
	def setUp(self):
		self.baseurl = "http://127.0.0.1:5000/v1/diff"
		self.td = TestData

	def testSimpleCheck(self):
		"""
		Test uploads two files
		Similar size and different content
		Check binary difference is correct
		"""
		# Generage task ID
		task = ids.pop()
		testfile = {
			LEFT: self.td.path1,
			RIGHT: self.td.path2
		}
		# Load data on server
		for side in (LEFT, RIGHT):
			# Prepare data from testfile
			base64_data = base64.b64encode(open(testfile[side], 'rb').read())
			url = "%s/%s/%s" % (self.baseurl, task, side)
			json_data = '{"data": "%s"}' % base64_data
			r = requests.put(url, data = json_data)
			self.assertEqual(r.status_code, 201)

		# Get difference and check it
		url = "%s/%s" % (self.baseurl, task)
		r = requests.get(url)
		self.assertEqual(r.status_code, 200)
		body = r.json()
		self.assertEqual(body["diff"]["binary_diff"], self.td.correct_diff)

	def tearDown(self):
		pass

if __name__ == '__main__':
    unittest.main()
