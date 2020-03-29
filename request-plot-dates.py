import requests
import csv
import datetime
import matplotlib
import matplotlib.pyplot as plt
from contextlib import closing

confirmed_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

data = {}
#countries_filter = ['Argentina','Spain','United Kingdom','Canada','Italy','Brazil','US','Sweden']
#countries_filter = ['Argentina','Spain','Italy','Brazil','Sweden']
countries_filter = ['Argentina']

class Date_Series():
	def __init__(self, x):
		self.x = x
		self.confirmed = []
	def SetConfirmed(self, seriesData):
		self.confirmed = seriesData

class Over_Threshold_Series():
	def __init__(self):
		self.x = []
		self.confirmed = []
	def SetConfirmed(self, values):		
		x = []
		y = []
		j = 0
		overthreshold = False
		for i in range(len(values)):
			if int(values[i]) > 100 or overthreshold == True:
				overthreshold = True
			if overthreshold == True:
				x.append(j)
				y.append(int(values[i]))
				j += 1
		self.x = x
		self.confirmed = y

class Country_Data():
	def __init__(self, country, datesStringList):
		self.name = country
		self.dates = [datetime.datetime.strptime(s, '%m/%d/%y') for s in datesStringList]
		self.date_series = Date_Series(matplotlib.dates.date2num(self.dates))
		self.over_threshold_series = Over_Threshold_Series()
		
	def SetConfirmed(self, seriesData):
		self.date_series.SetConfirmed(seriesData)
		self.over_threshold_series.SetConfirmed(seriesData)

with closing(requests.get(confirmed_url)) as r:
	f = (line.decode('utf-8') for line in r.iter_lines())
	reader = csv.reader(f, delimiter=',', quotechar='"')
	headers = next(reader)[4:]
	for row in reader:
		name = row[1]
		if (not name in data) and name in countries_filter:
			data[name] = Country_Data(name, headers)
			data[name].SetConfirmed(row[4:])

fig1 = plt.figure()
ax1 = fig1.add_subplot(111)
for name in countries_filter:
	country_data = data[name]
	ax1.plot_date(country_data.date_series.x, country_data.date_series.confirmed, label=country_data.name)
	
ax1.legend(loc=2)
plt.show()

fig2 = plt.figure()
ax2 = fig2.add_subplot(222)
for name in countries_filter:
	country_data = data[name]
	ax2.plot(country_data.over_threshold_series.x, country_data.over_threshold_series.confirmed, label=country_data.name)

plt.title('Confirmed case progression per day after 100')
#fig2.legend(loc=2)
ax2.set_ylim(top=4000)
ax2.set_xlim(right=20)
plt.show()
