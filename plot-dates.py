import csv
import datetime
import matplotlib
import matplotlib.pyplot as plt

countries = []
with open('countries.txt') as csvcountries:
	reader = csv.reader(csvcountries)
	for row in reader:
		for col in row:
			countries.append(col)

for country in countries:
	with open('time_series_covid19_confirmed_global.csv') as csvfile:
		reader = csv.reader(csvfile)
		headers = next(reader)
		values = []
		for row in reader:
			if country == row[1] and row[0] == '':
				values = row
				break
		x = matplotlib.dates.date2num([datetime.datetime.strptime(s, '%m/%d/%y') for s in headers[4:]])
		y = [int(s) for s in values[4:]]
		plt.plot_date(x, y, label=country)

plt.legend(loc=2)
plt.show()

