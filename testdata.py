class TestData(object):
	path = "test_data/78/d3/74/78d374355055544920af93639cd38abb4cfd6ea811c0c584ef2d325c7d9cb427"
	data = open("test_data/echo_data").read()
	sha = "78d374355055544920af93639cd38abb4cfd6ea811c0c584ef2d325c7d9cb427"
	path1 = "test_data/8c/cc/7d/8ccc7ddcdce79da7376782b407a0ddbbd8b68881188887a154b515ca49e03ab9"
	data1 = open("test_data/echo1_data").read()
	sha1 = "8ccc7ddcdce79da7376782b407a0ddbbd8b68881188887a154b515ca49e03ab9"
	path2 = "test_data/53/a1/21/53a121ba03d9c55d688217bae9d358af4046f2bacd3fafaafc4cb28daa5f0448"
	data2 = open("test_data/echo2_data").read()
	sha2 = "53a121ba03d9c55d688217bae9d358af4046f2bacd3fafaafc4cb28daa5f0448"
	correct_diff = {"50": 3, "989": 2, "1222": 10}

# Create pool of IDs for testing
ids = range(1, 100)

