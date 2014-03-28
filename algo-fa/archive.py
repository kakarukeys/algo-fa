import os.path


def dump(directory, symbol, csv_string):
	""" Writes to <directory> a file <symbol>.csv with content <csv_string> """
	with open(os.path.join(directory, symbol + ".csv"), 'w') as f:
		f.write(csv_string)
