import matplotlib.pyplot as plt
import numpy as np
import pytz
import json
import urllib
import webbrowser
from urllib import request
from datetime import date, datetime, timedelta, timezone
from tkinter import Tk, filedialog, ttk, font, messagebox, scrolledtext, Grid, Toplevel, IntVar, StringVar

# Convert UTC datetime to Pacific time. This takes DST into account.
def utc_to_local(utc_time):
    return pytz.utc.localize(utc_time).astimezone(pytz.timezone('America/Los_Angeles'))

def getjsonURL(url):
    response = urllib.request.urlopen(url)
    return jason.loads(response.read())

def callback_url(url):
    webbrowser.open_new(url)

# Pass this the station number as a string and the start/end dates as datetime objects.
def fetchTides(station, startdate, enddate):
    formattedStartDate = startdate.strftime('%Y%m%d')
    formattedEndDate = enddate.strftime('%Y%m%d')
    getjsonURL('https://tidesandcurrents.noaa.gov/api/datagetter?product=predictions&application=NOS.COOPS.TAC.WL&begin_date=%s&end_date=%s&datum=MLLW&station=%s&time_zone=lst_ldt&units=english&interval=1&format=json' % (station, formattedStartDate, formattedEndDate))


class GUI:
    def __init__(self, master):
        self.master = master
        master.title("Tidetimes")

        style = ttk.Style()
        style.configure("URL.TLabel", foreground="blue")

        self.labelStation = ttk.Label(master,
                                     text="Station number (click here to find yours)",
                                     style="URL.TLabel", cursor="hand2")
        self.labelStation.bind("<Button-1>", lambda e: callback_url("https://tidesandcurrents.noaa.gov/"))
        self.labelStation.grid(row=0, column=0)

        self.varStation = IntVar()
        self.entryStation = ttk.Entry(master, textvariable=self.varStation)
        self.entryStation.grid(row=1, column=0)

        ttk.Label(master, text="Show tides at:").grid(row=2, column=0)
        self.varRiseSet = StringVar()
        self.varRiseSet.set("Sunrise")
        self.comboRiseSet = ttk.Combobox(master, state="readonly",
                                         textvariable=self.varRiseSet,
                                         values=("Sunrise", "Sunset"))
        self.comboRiseSet.grid(row=3, column=0)

        ttk.Label(master, text="From:").grid(row=4, column=0)

        self.varMonthStart = StringVar()
        self.varMonthStart.set("January")
        self.comboMonthStart = ttk.Combobox(master, state="readonly",
                                       textvariable=self.varMonthStart,
                                       values=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])
        self.comboMonthStart.grid(row=5, column=0)

        self.varDayStart = IntVar()
        self.varDayStart.set(1)
        self.entryDayStart = ttk.Entry(master, textvariable=self.varDayStart)
        self.entryDayStart.grid(row=5, column=1)

        self.varYearStart = IntVar()
        self.varYearStart.set(2020)
        self.entryYearStart = ttk.Entry(master, textvariable=self.varYearStart)
        self.entryYearStart.grid(row=5, column=2)

        ttk.Label(master, text="To:").grid(row=6, column=0)

        self.varMonthEnd = StringVar()
        self.varMonthEnd.set("January")
        self.comboMonthEnd = ttk.Combobox(master, state="readonly",
                                       textvariable=self.varMonthEnd,
                                       values=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])
        self.comboMonthEnd.grid(row=7, column=0)

        self.varDayEnd = IntVar()
        self.varDayEnd.set(1)
        self.entryDayEnd = ttk.Entry(master, textvariable=self.varDayEnd)
        self.entryDayEnd.grid(row=7, column=1)

        self.varYearEnd = IntVar()
        self.varYearEnd.set(2020)
        self.entryYearEnd = ttk.Entry(master, textvariable=self.varYearEnd)
        self.entryYearEnd.grid(row=7, column=2)

        self.buttonGo = ttk.Button(text="Go").grid(row=8, column=0)






if __name__ == '__main__':
    root = Tk()
    RUN_GUI = GUI(root)
    root.mainloop()

print("Enter start date (ex.: 2020-01-08): ")
startdateInput = input()
startdate = date(int(startdateInput[0:4]), int(startdateInput[5:7]), int(startdateInput[8:10]))
formattedStartDate = startdate.strftime('%Y%m%d')

print("Enter end date (ex.: 2020-01-09): ")
enddateInput = input()
enddate = date(int(enddateInput[0:4]), int(enddateInput[5:7]), int(enddateInput[8:10]))
formattedEndDate = enddate.strftime('%Y%m%d')


print("Fetching NOAA tide data...")
noaaURL = 'https://tidesandcurrents.noaa.gov/api/datagetter?product=predictions&application=NOS.COOPS.TAC.WL&begin_date=%s&end_date=%s&datum=MLLW&station=9410230&time_zone=lst_ldt&units=english&interval=1&format=json' % (formattedStartDate, formattedEndDate)
responseNOAA = urllib.request.urlopen(noaaURL)
dataNOAA = json.loads(responseNOAA.read())
print("Tide data loaded.\n")

datelist = []
waterlevellist = []
thisDate = startdate
print("Fetching sunrise data...")
while thisDate <= enddate:
    sunriseURL = "https://api.sunrise-sunset.org/json?lat=32.842674&lng=-117.257767&date=%s&formatted=0" % str(thisDate)
    responseSunrise = urllib.request.urlopen(sunriseURL)
    dataSunrise = json.loads(responseSunrise.read())

    sunriseTime = dataSunrise['results']['sunset'][0:-6]
    sunriseDatetime = utc_to_local(datetime.strptime(sunriseTime, "%Y-%m-%dT%H:%M:%S"))

    for datum in dataNOAA['predictions']:
        if datum['t'] == str(sunriseDatetime)[0:-9]:
            datelist.append(sunriseDatetime.strftime("%#m/%#d\n%#I:%M"))
            waterlevellist.append(float(datum['v']))

    thisDate += timedelta(days=1)

print("Sunrise data loaded.\nGraphing...")

y_pos = np.arange(len(datelist))
plt.bar(y_pos, waterlevellist, align='center')
plt.xticks(y_pos, datelist)
plt.ylabel("Height (ft.)")
plt.show()
