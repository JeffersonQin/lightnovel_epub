
def is_null(data):
	if data is None:
		return True
	if data == {}:
		return True
	if data == []:
		return True
	if data == "":
		return True
	return False

def is_not_null(data):
	return not is_null(data)
