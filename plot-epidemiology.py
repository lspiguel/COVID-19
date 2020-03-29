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
		headers = next(reader)[4:]
		values = [0 for i in range(len(headers))]
		for row in reader:
			if country == row[1]:
				row = row[4:]
				for i in range(len(row)):
					values[i] += int(row[i])
		
		x = []
		y = []
		j = 0
		overthreshold = False
		for i in range(len(values)):
			if values[i] > 100 or overthreshold == True:
				overthreshold = True
			if overthreshold == True:
				x.append(j)
				y.append(values[i])
				j += 1
		
		plt.plot(x, y, label=country)

plt.title('Confirmed case progression per day after 100')
plt.legend(loc=2)
plt.ylim(top=4000)
plt.xlim(right=20)
plt.show()
