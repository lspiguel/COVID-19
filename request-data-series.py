import requests

r = requests.get('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')

with open('time_series_covid19_confirmed_global.csv', 'w') as f:
	f.write(r.text)
