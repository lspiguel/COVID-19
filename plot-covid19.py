import csv
import datetime
import matplotlib
import matplotlib.pyplot as plt

with open('time_series_covid19_confirmed_global.csv') as csvfile:
	reader = csv.reader(csvfile)
	headers = next(reader)
	values = []
	for row in reader:
		if 'Argentina' in row:
			values = row
			break
	x = matplotlib.dates.date2num([datetime.datetime.strptime(s, '%m/%d/%y') for s in headers[4:]])
	y = [int(s) for s in values[4:]]
	#print(x)
	#print(y)
	plt.plot_date(x, y)
	plt.show()
	
