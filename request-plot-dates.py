import requests
import csv
import datetime
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from contextlib import closing

class Date_Series():
	def __init__(self, x):
		self.x = x
		self.confirmed = []
		self.confirmed_delta = []
		self.recovered = []
		self.deaths = []
	def SetConfirmed(self, seriesData):
		self.confirmed = seriesData
		self.ProcessConfirmedDelta()
	def SetRecovered(self, seriesData):
		self.recovered = seriesData
	def SetDeaths(self, seriesData):
		self.deaths = seriesData
	def ProcessConfirmedDelta(self):
		deltas = []
		deltas.append(0)
		for i in range(1, len(self.confirmed)):
			deltas.append(self.confirmed[i] - self.confirmed[i - 1])
		self.confirmed_delta = np.array(deltas)

class Over_Threshold_Series():
	def __init__(self):
		self.threshold = 100
		self.confirmed_x = np.array([])
		self.confirmed = np.array([])
		self.confirmed_delta = np.array([])
		self.confirmed_doubling_time = np.array([])
		self.recovered_x = np.array([])
		self.recovered = np.array([])
		self.deaths_x = np.array([])
		self.deaths = np.array([])
	def SetConfirmed(self, values):		
		x = []
		y = []
		if values[0] < self.threshold:
			j = 0
			overthreshold = False
			for i in range(len(values)):
				if int(values[i]) >= self.threshold or overthreshold == True:
					overthreshold = True
				if overthreshold == True:
					x.append(j)
					y.append(int(values[i]))
					j += 1
		self.confirmed_x = np.array(x)
		self.confirmed = np.array(y)
		self.ProcessConfirmedDelta()
	def SetRecovered(self, values):		
		x = []
		y = []
		if values[0] < self.threshold:
			j = 0
			overthreshold = False
			for i in range(len(values)):
				if int(values[i]) >= self.threshold or overthreshold == True:
					overthreshold = True
				if overthreshold == True:
					x.append(j)
					y.append(int(values[i]))
					j += 1
		self.recovered_x= np.array(x)
		self.recovered = np.array(y)
	def SetDeaths(self, values):		
		x = []
		y = []
		if values[0] < self.threshold:
			j = 0
			overthreshold = False
			for i in range(len(values)):
				if int(values[i]) >= self.threshold or overthreshold == True:
					overthreshold = True
				if overthreshold == True:
					x.append(j)
					y.append(int(values[i]))
					j += 1
		self.deaths_x = np.array(x)
		self.deaths = np.array(y)
	def ProcessConfirmedDelta(self):
		deltas = []
		if len(self.confirmed) > 0:
			deltas.append(0)
			for i in range(1, len(self.confirmed)):
				deltas.append(self.confirmed[i] - self.confirmed[i - 1])
		doublings = []
		if len(deltas) > 3:
			doublings.append(float("inf"))
			doublings.append(float("inf"))
			for i in range(2, len(self.confirmed)):
				avg = float(deltas[i - 2] + deltas[i - 1] + deltas[i]) / 3
				if avg != 0:
					doublings.append(float(self.confirmed[i]) / avg)
				else:
					doublings.append(float("inf"))
		self.confirmed_delta = np.array(deltas)
		self.confirmed_doubling_time = np.array(doublings)
			
class Country_Data():
	def __init__(self, country, datesStringList):
		self.name = country
		self.dates = [datetime.datetime.strptime(s, '%m/%d/%y') for s in datesStringList]
		self.date_series = Date_Series(matplotlib.dates.date2num(self.dates))
		self.over_threshold_series = Over_Threshold_Series()
		self.confirmed = []
		self.recovered = []
		self.deaths = []
	def SetConfirmed(self, confirmed):
		self.confirmed = [int(v) for v in confirmed]
		self.date_series.SetConfirmed(self.confirmed)
		self.over_threshold_series.SetConfirmed(self.confirmed)
	def SetRecovered(self, recovered):
		self.recovered = [int(v) for v in recovered]
		self.date_series.SetRecovered(self.recovered)
		self.over_threshold_series.SetRecovered(self.recovered)
	def SetDeaths(self, deaths):
		self.deaths = [int(v) for v in deaths]
		self.date_series.SetDeaths(self.deaths)
		self.over_threshold_series.SetDeaths(self.deaths)
	def AddConfirmed(self, seriesData):
		for i in range(len(self.confirmed)):
			self.confirmed[i] += int(seriesData[i])
		self.date_series.SetConfirmed(self.confirmed)
		self.over_threshold_series.SetConfirmed(self.confirmed)
	def AddRecovered(self, recovered):
		for i in range(len(self.recovered)):
			self.recovered[i] += int(recovered[i])
		self.date_series.SetRecovered(self.recovered)
		self.over_threshold_series.SetRecovered(self.recovered)
	def AddDeaths(self, deaths):
		for i in range(len(self.deaths)):
			self.deaths[i] += int(deaths[i])
		self.date_series.SetDeaths(self.deaths)
		self.over_threshold_series.SetDeaths(self.deaths)
	def HasConfirmedData(self):
		if len(self.confirmed) > 0:
			return True
		else:
			return False
	def HasRecoveredData(self):
		if len(self.recovered) > 0:
			return True
		else:
			return False
	def HasDeathsData(self):
		if len(self.deaths) > 0:
			return True
		else:
			return False

def Load(url_confirmed, deaths_url, recovered_url, filter):
	return_data = {}
	headers = []
	with closing(requests.get(url_confirmed)) as r:
		f = (line.decode('utf-8') for line in r.iter_lines())
		reader = csv.reader(f, delimiter=',', quotechar='"')
		headers = next(reader)[4:]
		for row in reader:
			name = row[1]
			if name in filter:
				if (not name in return_data):
					return_data[name] = Country_Data(name, headers)
					return_data[name].SetConfirmed(row[4:])
				else:
					return_data[name].AddConfirmed(row[4:])
					
	with closing(requests.get(deaths_url)) as r:
		f = (line.decode('utf-8') for line in r.iter_lines())
		reader = csv.reader(f, delimiter=',', quotechar='"')
		next(reader)
		for row in reader:
			name = row[1]
			if name in filter:
				if name in return_data:
					if not return_data[name].HasDeathsData():
						return_data[name].SetDeaths(row[4:])
					else:
						return_data[name].AddDeaths(row[4:])
					
	with closing(requests.get(recovered_url)) as r:
		f = (line.decode('utf-8') for line in r.iter_lines())
		reader = csv.reader(f, delimiter=',', quotechar='"')
		next(reader)
		for row in reader:
			name = row[1]
			if name in filter:
				if name in return_data:
					if not return_data[name].HasRecoveredData():
						return_data[name].SetRecovered(row[4:])
					else:
						return_data[name].AddRecovered(row[4:])

	return return_data

def Load_Countries_Filter():
	countries = []
	try:
		with open('countries.txt') as csvcountries:
			reader = csv.reader(csvcountries)
			for row in reader:
				for col in row:
					countries.append(col)
	except:
		countries = ['Argentina','Spain','United Kingdom','Italy','US','Sweden','Brazil','Canada','China','Germany','Chile','India']
		#countries = ['Argentina']
	return countries

def Graph_Daily_Confirmed_Lineal(data, filter, timestamp):
	linestyles = ['-','--','-.',':']
	fig1 = plt.figure(dpi=300)
	ax1 = plt.axes([0.1, 0.1, 0.8, 0.8]) #xticks=[], yticks=[]
	i = 0
	for name in filter:
		country_data = data[name]
		if len(country_data.date_series.confirmed) > 0:
			ax1.plot_date(country_data.date_series.x, country_data.date_series.confirmed,linestyles[(i//6)%4], label=country_data.name)
			i += 1
		
	fig1.suptitle('Total confirmed cases, by date', fontsize=14)
	ax1.set_title(timestamp, fontsize=9)
	ax1.legend(loc=2, fontsize='10')
	#ax1.set_xlim(left=matplotlib.dates.date2num(datetime.date.today()))
	plt.show()
	plt.close(fig1)

def Graph_Daily_Deaths_Lineal(data, filter, timestamp):
	linestyles = ['-','--','-.',':']
	fig1 = plt.figure(dpi=300)
	ax1 = plt.axes([0.1, 0.1, 0.8, 0.8]) #xticks=[], yticks=[]
	i = 0
	for name in filter:
		country_data = data[name]
		if len(country_data.date_series.deaths) > 0:
			ax1.plot_date(country_data.date_series.x, country_data.date_series.deaths,linestyles[(i//6)%4], label=country_data.name)
			i += 1
		
	fig1.suptitle('Total deaths, by date', fontsize=14)
	ax1.set_title(timestamp, fontsize=9)
	ax1.legend(loc=2, fontsize='10')
	#ax1.set_xlim(left=matplotlib.dates.date2num(datetime.date.today()))
	plt.show()
	plt.close(fig1)
	
def Graph_Confirmed_Over_Threshold_Lineal(data, filter, timestamp):
	linestyles = ['-','--','-.',':']
	fig2 = plt.figure(dpi=300) #figsize=(16,8),dpi=200
	ax2 = plt.axes([0.1, 0.1, 0.8, 0.8])
	i = 0
	for name in filter:
		country_data = data[name]
		if len(country_data.over_threshold_series.confirmed) > 0:
			ax2.plot(country_data.over_threshold_series.confirmed_x, country_data.over_threshold_series.confirmed, label=country_data.name,ls=linestyles[(i//6)%4],marker='')
			i += 1

	fig2.suptitle('Confirmed case progression per day after 100 cases', fontsize=14)
	ax2.set_title(timestamp, fontsize=9)
	ax2.legend(loc=2, fontsize='10')
	ax2.set_ylim(top=4000,bottom=0)
	ax2.set_xlim(right=20,left=0)
	plt.show()
	plt.close(fig2)

def Graph_Confirmed_Over_Threshold_Log(data, filter, timestamp):
	linestyles = ['-','--','-.',':']
	fig2 = plt.figure(dpi=300) #figsize=(16,8),dpi=200
	ax2 = plt.axes([0.1, 0.1, 0.8, 0.8],yscale='log')
	i = 0
	for name in filter:
		country_data = data[name]
		if len(country_data.over_threshold_series.confirmed) > 0:
			ax2.plot(country_data.over_threshold_series.confirmed_x, country_data.over_threshold_series.confirmed, label=country_data.name,ls=linestyles[(i//6)%4],marker='')
			i += 1

	fig2.suptitle('Confirmed case progression per day after 100 cases (log scale)', fontsize=14)
	ax2.set_title(timestamp, fontsize=9)
	ax2.legend(loc=2, fontsize='10')
	ax2.set_ylim(top=20000,bottom=0)
	ax2.set_xlim(right=20,left=0)
	plt.show()
	plt.close(fig2)

def Graph_Deaths_Over_Threshold_Log(data, filter, timestamp):
	linestyles = ['-','--','-.',':']
	fig2 = plt.figure(dpi=300) #figsize=(16,8),dpi=200
	ax2 = plt.axes([0.1, 0.1, 0.8, 0.8], yscale='log')
	i = 0
	for name in filter:
		country_data = data[name]
		if len(country_data.over_threshold_series.deaths) > 0:
			ax2.plot(country_data.over_threshold_series.deaths_x, country_data.over_threshold_series.deaths, label=country_data.name,ls=linestyles[(i//6)%4],marker='')
			i += 1

	fig2.suptitle('Total deaths per day after 100 deaths (log scale)', fontsize=14)
	ax2.set_title(timestamp, fontsize=9)
	ax2.legend(loc=2, fontsize='10')
	ax2.set_ylim(bottom=0,top=20000)
	ax2.set_xlim(right=20,left=0)
	plt.show()
	plt.close(fig2)

def Graph_Confirmed_Deltas_Bar(data, filter, timestamp):
	colors = ['b','g','r','c','m','y','k']
	fig3 = plt.figure(dpi=300) #figsize=(16,8),dpi=200
	ax3 = plt.axes([0.1, 0.1, 0.8, 0.8])
	i = 0
	for name in filter:
		country_data = data[name]
		if len(country_data.over_threshold_series.confirmed_delta) > 0:
			x = [x + i / 7 for x in country_data.over_threshold_series.confirmed_x]
			ax3.bar(x, country_data.over_threshold_series.confirmed_delta, label=country_data.name,align='center',width=.15,color=colors[i%7],edgecolor='w')
			i += 1
		if i >= 6:
			break
	fig3.suptitle('Confirmed case difference per day after 100 cases', fontsize=14)
	ax2.set_title(timestamp, fontsize=9)
	ax3.legend(loc=2, fontsize='10')
	ax3.set_ylim(top=2000,bottom=0)
	ax3.set_xlim(right=20,left=0)
	plt.show()
	plt.close(fig3)

def Graph_Doubling_Time_Over_Threshold_Lineal(data, filter, timestamp):
	linestyles = ['-','--','-.',':']
	fig2 = plt.figure(dpi=300) #figsize=(16,8),dpi=200
	ax2 = plt.axes([0.1, 0.1, 0.8, 0.8])
	i = 0
	for name in filter:
		country_data = data[name]
		if len(country_data.over_threshold_series.confirmed_doubling_time) > 0:
			ax2.plot(country_data.over_threshold_series.confirmed_x, country_data.over_threshold_series.confirmed_doubling_time, label=country_data.name,ls=linestyles[(i//6)%4],marker='')
			i += 1

	fig2.suptitle('Confirmed case doubling time in days, per day after 100 cases (3 day average)', fontsize=14)
	ax2.set_title(timestamp, fontsize=9)
	ax2.legend(loc=2, fontsize='10')
	ax2.set_ylim(bottom=0,top=20)
	ax2.set_xlim(right=20,left=0)
	plt.show()
	plt.close(fig2)


def main():
	confirmed_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
	deaths_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
	recovered_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
	timestamp = 'Source: John Hopkins - ' + datetime.datetime.now(tz=datetime.timezone.utc).isoformat(' ', timespec='seconds')

	countries_filter = Load_Countries_Filter()
	countries_data = Load(confirmed_url, deaths_url, recovered_url, countries_filter)

	Graph_Daily_Confirmed_Lineal(countries_data, countries_filter, timestamp)
	Graph_Daily_Deaths_Lineal(countries_data, countries_filter, timestamp)
	Graph_Confirmed_Over_Threshold_Lineal(countries_data, countries_filter, timestamp)
	Graph_Confirmed_Over_Threshold_Log(countries_data, countries_filter, timestamp)
	Graph_Deaths_Over_Threshold_Log(countries_data, countries_filter, timestamp)
	#Graph_Confirmed_Deltas_Bar(countries_data, countries_filter, timestamp)
	Graph_Doubling_Time_Over_Threshold_Lineal(countries_data, countries_filter, timestamp)

if __name__ == '__main__':
	main()
	
