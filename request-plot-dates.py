import requests
import csv
import datetime
import matplotlib
import matplotlib.pyplot as plt
from contextlib import closing

confirmed_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

data = {}
countries_filter = ['Argentina','Spain','United Kingdom','Canada','Italy','Brazil','US','Sweden']
#countries_filter = ['Argentina']

class Country_Data():
	def __init__(self, country, datesStringList):
		self.name = country
		self.dates = [datetime.datetime.strptime(s, '%m/%d/%y') for s in datesStringList]
		self.x = matplotlib.dates.date2num(self.dates)
		self.confirmed = []
	def SetConfirmed(self, seriesData):
		self.confirmed = seriesData

with closing(requests.get(confirmed_url)) as r:
	f = (line.decode('utf-8') for line in r.iter_lines())
	reader = csv.reader(f, delimiter=',', quotechar='"')
	headers = next(reader)[4:]
	for row in reader:
		name = row[1]
		if (not name in data) and name in countries_filter:
			data[name] = Country_Data(name, headers)
			data[name].SetConfirmed(row[4:])

for name in countries_filter:
	country_data = data[name]
	plt.plot_date(country_data.x, country_data.confirmed, label=country_data.name)
	
plt.legend(loc=2)
plt.show()
