def print_point_labels(df, graph, x, y, label):
	""" Prints a text label beside each point
		df: plotted DataFrame object
		graph: the plot object
		x: column name for x
		y: column name for y
		label: column name for label
	"""
	xbound = graph.get_xbound()
	ybound = graph.get_ybound()
	offset_x = (xbound[1] - xbound[0]) * 0.01
	offset_y = (ybound[1] - ybound[0]) * 0.01

	for i, row in df.iterrows():
		graph.text(row[x] + offset_x , row[y] + offset_y, row[label])
