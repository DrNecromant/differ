class InvalidValue(Exception):
	# That error is raised in case of DB record or part of url is not acceptable
	pass

class EmptyRecord(Exception):
	# That error occures when someone want to save empty record in DB or fs for comparison
	pass
