import requests
import csv
import datetime
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from contextlib import closing

class Configuration():
	def __init__(self, draw, save, dpi, titlefontsize, subtitlefontsize, legendfontsize, days):
		self.draw = draw
		self.save = save
		self.dpi = dpi
		self.titlefontsize = titlefontsize
		self.subtitlefontsize = subtitlefontsize
		self.legendfontsize = legendfontsize
		self.days = days

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
			lastavg = float("inf")
			doublings.append(float("inf"))
			doublings.append(float("inf"))
			for i in range(2, len(self.confirmed)):
				avg = float(deltas[i - 2] + deltas[i - 1] + deltas[i]) / 3
				if avg > 0:
					lastavg = float(self.confirmed[i]) / avg
					doublings.append(lastavg)
				else:
					doublings.append(lastavg)
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
			try:
				name = row[1]
				if name in filter:
					if (not name in return_data):
						return_data[name] = Country_Data(name, headers)
						return_data[name].SetConfirmed(row[4:])
					else:
						return_data[name].AddConfirmed(row[4:])
			except:
				pass
					
	with closing(requests.get(deaths_url)) as r:
		f = (line.decode('utf-8') for line in r.iter_lines())
		reader = csv.reader(f, delimiter=',', quotechar='"')
		next(reader)
		for row in reader:
			try:
				name = row[1]
				if name in filter:
					if name in return_data:
						if not return_data[name].HasDeathsData():
							return_data[name].SetDeaths(row[4:])
						else:
							return_data[name].AddDeaths(row[4:])
			except:
				pass
					
	with closing(requests.get(recovered_url)) as r:
		f = (line.decode('utf-8') for line in r.iter_lines())
		reader = csv.reader(f, delimiter=',', quotechar='"')
		next(reader)
		for row in reader:
			try:
				name = row[1]
				if name in filter:
					if name in return_data:
						if not return_data[name].HasRecoveredData():
							return_data[name].SetRecovered(row[4:])
						else:
							return_data[name].AddRecovered(row[4:])
			except:
				pass

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

def Graph_Daily_Confirmed_Lineal(config, data, filter, timestamp):
	linestyles = ['-','--','-.',':']
	fig = plt.figure(dpi=config.dpi)
	axis = plt.axes([0.1, 0.1, 0.8, 0.8]) #xticks=[], yticks=[]
	i = 0
	for name in filter:
		country_data = data[name]
		if len(country_data.date_series.confirmed) > 0:
			axis.plot_date(country_data.date_series.x, country_data.date_series.confirmed, linestyles[(i//6)%4], label=country_data.name)
			i += 1
		
	fig.suptitle('Total confirmed cases, by date', fontsize=config.titlefontsize)
	axis.set_title(timestamp, fontsize=config.subtitlefontsize)
	axis.legend(loc=2, fontsize=config.legendfontsize)
	#axis.set_xlim(left=matplotlib.dates.date2num(datetime.date.today()))
	if(config.draw):
		plt.show()
	if(config.save):
		fig.savefig('Graph_Daily_Confirmed_Lineal.png')
	plt.close(fig)

def Graph_Daily_Deaths_Lineal(config, data, filter, timestamp):
	linestyles = ['-','--','-.',':']
	fig = plt.figure(dpi=config.dpi)
	axis = plt.axes([0.1, 0.1, 0.8, 0.8]) #xticks=[], yticks=[]
	i = 0
	for name in filter:
		country_data = data[name]
		if len(country_data.date_series.deaths) > 0:
			axis.plot_date(country_data.date_series.x, country_data.date_series.deaths, linestyles[(i//6)%4], label=country_data.name)
			i += 1
		
	fig.suptitle('Total deaths, by date', fontsize=config.titlefontsize)
	axis.set_title(timestamp, fontsize=config.subtitlefontsize)
	axis.legend(loc=2, fontsize=config.legendfontsize)
	#axis.set_xlim(left=matplotlib.dates.date2num(datetime.date.today()))
	if(config.draw):
		plt.show()
	if(config.save):
		fig.savefig('Graph_Daily_Deaths_Lineal.png')
	plt.close(fig)

def Graph_Daily_ConfirmedRecoveredDeaths_Lineal(config, data, filter, timestamp):
	fig = plt.figure(dpi=config.dpi)
	axis = plt.axes([0.1, 0.1, 0.8, 0.8]) #xticks=[], yticks=[]
	i = 0
	name = filter[0]
	country_data = data[name]
	first = len(country_data.date_series.x) // 2

	axis.plot_date(country_data.date_series.x[first:], country_data.date_series.confirmed[first:], label='Confirmed', linestyle='-')
	axis.plot_date(country_data.date_series.x[first:], country_data.date_series.recovered[first:], label='Recovered', linestyle='-')
	axis.plot_date(country_data.date_series.x[first:], country_data.date_series.deaths[first:], label='Deaths', linestyle='-')
		
	fig.suptitle('Confirmed/Recovered/Deaths for ' + name + ', by date', fontsize=config.titlefontsize)
	axis.set_title(timestamp, fontsize=config.subtitlefontsize)
	axis.legend(loc=2, fontsize=config.legendfontsize)
	#axis.set_xlim(left=matplotlib.dates.date2num(datetime.date.today()))
	if(config.draw):
		plt.show()
	if(config.save):
		fig.savefig('Graph_Daily_ConfirmedRecoveredDeaths_Lineal.png')
	plt.close(fig)

def Graph_Confirmed_Over_Threshold_Lineal(config, data, filter, timestamp):
	linestyles = ['-','--','-.',':']
	fig = plt.figure(dpi=config.dpi) #figsize=(16,8),dpi=200
	axis = plt.axes([0.1, 0.1, 0.8, 0.8])
	i = 0
	for name in filter:
		country_data = data[name]
		if len(country_data.over_threshold_series.confirmed) > 0:
			axis.plot(country_data.over_threshold_series.confirmed_x, country_data.over_threshold_series.confirmed, label=country_data.name, ls=linestyles[(i//6)%4],marker='')
			i += 1

	fig.suptitle('Confirmed case progression per day after 100 cases', fontsize=config.titlefontsize)
	axis.set_title(timestamp, fontsize=config.subtitlefontsize)
	axis.legend(loc=2, fontsize=config.legendfontsize)
	axis.set_ylim(top=10000, bottom=0)
	axis.set_xlim(right=config.days, left=0)
	if(config.draw):
		plt.show()
	if(config.save):
		fig.savefig('Graph_Confirmed_Over_Threshold_Lineal.png')
	plt.close(fig)

def Graph_Confirmed_Over_Threshold_Log(config, data, filter, timestamp):
	linestyles = ['-','--','-.',':']
	fig = plt.figure(dpi=config.dpi) #figsize=(16,8),dpi=200
	axis = plt.axes([0.1, 0.1, 0.8, 0.8],yscale='log')
	i = 0
	for name in filter:
		country_data = data[name]
		if len(country_data.over_threshold_series.confirmed) > 0:
			axis.plot(country_data.over_threshold_series.confirmed_x, country_data.over_threshold_series.confirmed, label=country_data.name,ls=linestyles[(i//6)%4],marker='')
			i += 1

	fig.suptitle('Confirmed case progression per day after 100 cases (log scale)', fontsize=config.titlefontsize)
	axis.set_title(timestamp, fontsize=config.subtitlefontsize)
	axis.legend(loc=2, fontsize=config.legendfontsize)
	axis.set_ylim(top=5000000)
	axis.set_xlim(right=config.days, left=0)
	if(config.draw):
		plt.show()
	if(config.save):
		fig.savefig('Graph_Confirmed_Over_Threshold_Log.png')
	plt.close(fig)

def Graph_Deaths_Over_Threshold_Log(config, data, filter, timestamp):
	linestyles = ['-','--','-.',':']
	fig = plt.figure(dpi=config.dpi) #figsize=(16,8),dpi=200
	axis = plt.axes([0.1, 0.1, 0.8, 0.8], yscale='log')
	i = 0
	for name in filter:
		country_data = data[name]
		if len(country_data.over_threshold_series.deaths) > 0:
			axis.plot(country_data.over_threshold_series.deaths_x, country_data.over_threshold_series.deaths, label=country_data.name,ls=linestyles[(i//6)%4],marker='')
			i += 1

	fig.suptitle('Total deaths per day after 100 deaths (log scale)', fontsize=config.titlefontsize)
	axis.set_title(timestamp, fontsize=config.subtitlefontsize)
	axis.legend(loc=2, fontsize=config.legendfontsize)
	axis.set_ylim(top=5000000)
	axis.set_xlim(right=config.days, left=0)
	if(config.draw):
		plt.show()
	if(config.save):
		fig.savefig('Graph_Deaths_Over_Threshold_Log.png')
	plt.close(fig)

def Graph_Confirmed_Deltas_Bar(config, data, filter, timestamp):
	colors = ['b','g','r','c','m','y','k']
	fig = plt.figure(dpi=config.dpi) #figsize=(16,8),dpi=200
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
	fig.suptitle('Confirmed case difference per day after 100 cases', fontsize=config.titlefontsize)
	ax3.set_title(timestamp, fontsize=config.subtitlefontsize)
	ax3.legend(loc=2, fontsize=config.legendfontsize)
	ax3.set_ylim(top=3000, bottom=0)
	ax3.set_xlim(right=config.days, left=0)
	if(config.draw):
		plt.show()
	if(config.save):
		fig.savefig('Graph_Confirmed_Deltas_Bar.png')
	plt.close(fig3)

def Graph_Doubling_Time_Over_Threshold_Lineal(config, data, filter, timestamp):
	linestyles = ['-','--','-.',':']
	fig = plt.figure(dpi=config.dpi) #figsize=(16,8),dpi=200
	axis = plt.axes([0.1, 0.1, 0.8, 0.8])
	i = 0
	for name in filter:
		country_data = data[name]
		if len(country_data.over_threshold_series.confirmed_doubling_time) > 0:
			axis.plot(country_data.over_threshold_series.confirmed_x, country_data.over_threshold_series. confirmed_doubling_time, label=country_data.name, ls=linestyles[(i//6)%4], marker='')
			i += 1

	fig.suptitle('Confirmed case doubling time in days, per day after 100 cases (3 day average)', fontsize=config.titlefontsize)
	axis.set_title(timestamp, fontsize=config.subtitlefontsize)
	axis.legend(loc=2, fontsize=config.legendfontsize)
	axis.set_ylim(bottom=0, top=120)
	axis.set_xlim(right=config.days, left=0)
	if(config.draw):
		plt.show()
	if(config.save):
		fig.savefig('Graph_Doubling_Time_Over_Threshold_Lineal.png')
	plt.close(fig)

def main():
	# Urls to get data from John Hopkins (GitHub raw repositories, master branch)
	confirmed_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
	deaths_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'
	recovered_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
	timestamp = 'Source: John Hopkins - ' + datetime.datetime.now(tz=datetime.timezone.utc).isoformat(' ', timespec='seconds')

	# Load data
	countries_filter = Load_Countries_Filter()
	countries_data = Load(confirmed_url, deaths_url, recovered_url, countries_filter)

	# This is where a configuration is set
	# The parameters are as follows:
	# Show - display plots on screen (boolean),
	# Save - whether to save plots (boolean),
	# DPI - Dots per inch to use on plots (integer),
	# Font size for title (integer),
	# Font size for subtitle (integer),
	# Font size for legends (integer),
	# Number of days to plot on over threshold graphs (integer)
	config = Configuration(True, True, 300, 14, 10, 9, 90)

	# Do the plots 
	Graph_Daily_Confirmed_Lineal(config, countries_data, countries_filter, timestamp)
	Graph_Daily_Deaths_Lineal(config, countries_data, countries_filter, timestamp)
	Graph_Daily_ConfirmedRecoveredDeaths_Lineal(config, countries_data, countries_filter, timestamp)
	Graph_Confirmed_Over_Threshold_Lineal(config, countries_data, countries_filter, timestamp)
	Graph_Confirmed_Over_Threshold_Log(config, countries_data, countries_filter, timestamp)
	Graph_Deaths_Over_Threshold_Log(config, countries_data, countries_filter, timestamp)
	#Graph_Confirmed_Deltas_Bar(config, countries_data, countries_filter, timestamp)
	Graph_Doubling_Time_Over_Threshold_Lineal(config, countries_data, countries_filter, timestamp)

if __name__ == '__main__':
	main()
	
