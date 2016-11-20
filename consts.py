LEFT = "left"
RIGHT = "right"
BASEURL = "/v1/diff"

class ProductionConfig(object):
	TESTING = False
	DEBUG = False
	SQLALCHEMY_DATABASE_URI = "sqlite:///production.db"
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	RECORD_STORAGE_PATH = "storage"

class TestingConfig(object):
	TESTING = True
	DEBUG = True
	DATABASE_URI = 'sqlite:///:memory:'
	SQLALCHEMY_TRACK_MODIFICATIONS = True
	RECORD_STORAGE_PATH = "test_data"
