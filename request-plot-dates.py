import requests
import csv
import datetime
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from contextlib import closing

confirmed_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
countries_filter = ['Argentina','Spain','United Kingdom','Italy','US','Brazil','Canada','Sweden','China','Germany']
#countries_filter = ['Argentina']
threshold = 100
data = {}

class Date_Series():
	def __init__(self, x):
		self.x = x
		self.confirmed = []
		self.confirmed_delta = []
	def SetConfirmed(self, seriesData):
		self.confirmed = seriesData
		self.ProcessConfirmedDelta()
	def ProcessConfirmedDelta(self):
		self.confirmed_delta = [0]
		for i in range(1, len(self.confirmed)):
			self.confirmed_delta.append(self.confirmed[i] - self.confirmed[i - 1])

class Over_Threshold_Series():
	def __init__(self):
		self.x = np.array([])
		self.confirmed = np.array([])
		self.confirmed_delta = np.array([])
	def SetConfirmed(self, values):		
		x = []
		y = []
		if values[0] < threshold:
			j = 0
			overthreshold = False
			for i in range(len(values)):
				if int(values[i]) >= threshold or overthreshold == True:
					overthreshold = True
				if overthreshold == True:
					x.append(j)
					y.append(int(values[i]))
					j += 1
		self.x = np.array(x)
		self.confirmed = np.array(y)
		self.ProcessConfirmedDelta()
	def ProcessConfirmedDelta(self):
		deltas = [0]
		for i in range(1, len(self.confirmed)):
			deltas.append(self.confirmed[i] - self.confirmed[i - 1])
		self.confirmed_delta = np.array(deltas)
			
class Country_Data():
	def __init__(self, country, datesStringList):
		self.name = country
		self.dates = [datetime.datetime.strptime(s, '%m/%d/%y') for s in datesStringList]
		self.date_series = Date_Series(matplotlib.dates.date2num(self.dates))
		self.over_threshold_series = Over_Threshold_Series()
		self.confirmed = []
	def SetConfirmed(self, seriesData):
		self.confirmed = [int(v) for v in seriesData]
		self.date_series.SetConfirmed(self.confirmed)
		self.over_threshold_series.SetConfirmed(self.confirmed)
	def AddConfirmed(self, seriesData):
		for i in range(len(self.confirmed)):
			self.confirmed[i] += int(seriesData[i])
		self.date_series.SetConfirmed(self.confirmed)
		self.over_threshold_series.SetConfirmed(self.confirmed)

with closing(requests.get(confirmed_url)) as r:
	f = (line.decode('utf-8') for line in r.iter_lines())
	reader = csv.reader(f, delimiter=',', quotechar='"')
	headers = next(reader)[4:]
	for row in reader:
		name = row[1]
		if name in countries_filter:
			if (not name in data):
				data[name] = Country_Data(name, headers)
				data[name].SetConfirmed(row[4:])
			else:
				data[name].AddConfirmed(row[4:])

fig1 = plt.figure(dpi=100)
ax1 = plt.axes([0.1, 0.1, 0.8, 0.8]) #xticks=[], yticks=[]
for name in countries_filter:
	country_data = data[name]
	if len(country_data.date_series.confirmed) > 0:
		ax1.plot_date(country_data.date_series.x, country_data.date_series.confirmed, label=country_data.name,ls='-')

plt.title('Confirmed daily cases')
ax1.legend(loc=2)
plt.show()
plt.close(fig1)

linestyles = ['-','--','-.',':']
fig2 = plt.figure(dpi=100) #figsize=(16,8),dpi=200
ax2 = plt.axes([0.1, 0.1, 0.8, 0.8])
i = 0
for name in countries_filter:
	country_data = data[name]
	if len(country_data.over_threshold_series.confirmed) > 0:
		ax2.plot(country_data.over_threshold_series.x, country_data.over_threshold_series.confirmed, label=country_data.name,ls=linestyles[(i//6)%4])
		i += 1

plt.title('Confirmed case progression per day after 100 cases')
ax2.legend(loc=2)
ax2.set_ylim(top=4000)
ax2.set_xlim(right=20)
plt.show()
plt.close(fig2)

#linestyles = ['-','--','-.',':']
#fig3 = plt.figure(dpi=100) #figsize=(16,8),dpi=200
#ax3 = plt.axes([0.1, 0.1, 0.8, 0.8])
#i = 0
#for name in countries_filter:
#	country_data = data[name]
#	if len(country_data.over_threshold_series.confirmed_delta) > 0:
#		ax3.plot(country_data.over_threshold_series.x, country_data.over_threshold_series.confirmed_delta, label=country_data.name,ls=linestyles[(i//6)%4])
#		i += 1

#plt.title('Confirmed case difference per day after 100 cases')
#ax3.legend(loc=2)
#ax3.set_ylim(top=4000)
#ax3.set_xlim(right=20)
#plt.show()
#plt.close(fig3)
