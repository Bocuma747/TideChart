import matplotlib.pyplot as plt
import numpy as np
import pytz
from timezonefinder import TimezoneFinder
import json
import webbrowser
import urllib
from urllib import request
from datetime import date, datetime, timedelta, timezone
from tkinter import Tk, ttk, messagebox, Grid, IntVar, StringVar, Toplevel


# Convert UTC datetime to Pacific time. This takes DST into account.
def utc_to_local(utc_time, tz):
    return pytz.utc.localize(utc_time).astimezone(pytz.timezone(tz))

# Gets a url and parses it.
def getjsonURL(url):
    response = urllib.request.urlopen(url)
    return json.loads(response.read())

# Get time zone from lat/long coordinates.
def gettimezone(latitude, longitude):
    tf = TimezoneFinder()
    return tf.timezone_at(lat=latitude, lng = longitude)

# Opens a link in tkinter.
def callback_url(url):
    webbrowser.open_new(url)

# Pass this the station number as a string, and the start/end dates as UTC datetime objects.
def fetchTides(station, startdate, enddate):
    formattedStartDate = startdate.strftime("%Y%m%d")
    formattedEndDate = enddate.strftime("%Y%m%d")
    # Get tide prediction data.
    tidedata = getjsonURL('https://tidesandcurrents.noaa.gov/api/datagetter?product=predictions&application=testing123&begin_date=%s&end_date=%s&datum=MLLW&station=%s&time_zone=gmt&units=english&interval=1&format=json' % (formattedStartDate, formattedEndDate, station))
    if 'error' in tidedata:
        return None
    else:
        return tidedata

def stationMetadata(station):
    try:
        metadata = getjsonURL('https://tidesandcurrents.noaa.gov/api/datagetter?product=water_level&application=tides_and_currents&begin_date=20200101&end_date=20200102&datum=MLLW&station=%s&time_zone=lst_ldt&units=english&interval=1440&format=json' % station)
    except Exception as e:
        raise Exception("Exception raised while retrieving station metadata:\n\"%s\"" % e)
    if 'error' in metadata:
        raise Exception("Server returned error while retrieving station metadata:\n\"%s\"" % metadata['error']['message'])
    else:
        return metadata['metadata']


class GUI:

    def __init__(self, master):

        # !!!!! GUI shit ahead !!!!!
        self.master = master
        master.title("Tidetimes")
        Grid.rowconfigure(master, 0, weight=1)
        Grid.rowconfigure(master, 1, weight=1)
        Grid.rowconfigure(master, 2, weight=1)
        Grid.rowconfigure(master, 3, weight=1)
        Grid.rowconfigure(master, 4, weight=1)
        Grid.rowconfigure(master, 5, weight=1)
        Grid.rowconfigure(master, 6, weight=1)
        Grid.rowconfigure(master, 7, weight=1)
        style = ttk.Style()
        style.configure("URL.TLabel", foreground="blue")

        self.labelStation = ttk.Label(master,
                                     text="Station number (click here to find yours)",
                                     style="URL.TLabel", cursor="hand2")
        self.labelStation.bind("<Button-1>", lambda e: callback_url("https://tidesandcurrents.noaa.gov/"))
        self.labelStation.grid(row=0, column=0, sticky='sew', columnspan=3, padx=5, pady=5)

        self.varStation = StringVar()
        self.entryStation = ttk.Entry(master, textvariable=self.varStation, justify='left')
        self.entryStation.grid(row=1, column=0, sticky='new', padx=5, pady=(0, 10))

        ttk.Label(master, text="Show tides at:").grid(row=2, column=0, sticky='sew', padx=5, pady=5)
        self.varRiseSet = StringVar()
        self.varRiseSet.set("Sunrise")
        self.comboRiseSet = ttk.Combobox(master, state="readonly",
                                         textvariable=self.varRiseSet,
                                         values=("Sunrise", "Sunset"))
        self.comboRiseSet.grid(row=3, column=0, sticky='new', padx=5, pady=(0, 5))

        ttk.Label(master, text="From:").grid(row=4, column=0, sticky='sew', padx=5, pady=5)

        self.varMonthStart = StringVar()
        self.varMonthStart.set("January")
        self.comboMonthStart = ttk.Combobox(master, state="readonly",
                                       textvariable=self.varMonthStart,
                                       values=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'], width=15)
        self.comboMonthStart.grid(row=5, column=0, sticky='new', padx=5, pady=(0, 5))

        self.varDayStart = IntVar()
        self.varDayStart.set(1)
        self.entryDayStart = ttk.Entry(master, textvariable=self.varDayStart, width=5)
        self.entryDayStart.grid(row=5, column=1, sticky='nw', padx=5, pady=(0, 5))

        self.varYearStart = IntVar()
        self.varYearStart.set(2020)
        self.entryYearStart = ttk.Entry(master, textvariable=self.varYearStart, width=10)
        self.entryYearStart.grid(row=5, column=2, sticky='nw', padx=5, pady=(0, 5))

        ttk.Label(master, text="To:").grid(row=6, column=0, sticky='sew', padx=5, pady=5)

        self.varMonthEnd = StringVar()
        self.varMonthEnd.set("January")
        self.comboMonthEnd = ttk.Combobox(master, state="readonly",
                                       textvariable=self.varMonthEnd,
                                       values=['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'], width=15)
        self.comboMonthEnd.grid(row=7, column=0, sticky='new', padx=5, pady=(0, 5))

        self.varDayEnd = IntVar()
        self.varDayEnd.set(1)
        self.entryDayEnd = ttk.Entry(master, textvariable=self.varDayEnd, width=5)
        self.entryDayEnd.grid(row=7, column=1, sticky='nw', padx=5, pady=(0, 5))

        self.varYearEnd = IntVar()
        self.varYearEnd.set(2020)
        self.entryYearEnd = ttk.Entry(master, textvariable=self.varYearEnd, width=10)
        self.entryYearEnd.grid(row=7, column=2, sticky='nw', padx=5, pady=(0, 5))


        def go():
            # Make sure date entries are valid, then convert them to datetime objects.
            try:
                self.dateStart = datetime.strptime((str(self.varYearStart.get()) + self.varMonthStart.get() + str(self.varDayStart.get())), "%Y%B%d")
                self.dateEnd = datetime.strptime((str(self.varYearEnd.get()) + self.varMonthEnd.get() + str(self.varDayEnd.get())), "%Y%B%d")
            except Exception as e:
                messagebox.showerror("Error", "Error: Invalid date entered.\n\n(%s)" % e)
                raise
                self.progresswindow.destroy()

            # Make a progress window.
            self.progresswindow = Toplevel(self.master)
            self.progresstextvar = StringVar()
            ttk.Label(self.progresswindow, text="", textvariable=self.progresstextvar).grid(row=0, column=0)
            ttk.Progressbar(self.progresswindow, mode='indeterminate').grid(row=1, column=0)
            self.progresswindow.update()

            # Get NOAA station metadata.
            self.progresstextvar.set("Fetching station metadata...")
            self.progresswindow.update()
            try:
                self.metadata = stationMetadata(self.varStation.get())
            except Exception as e:
                messagebox.showerror("Error", "%s" % e)
                self.progresswindow.destroy()
                raise

            # [datelist] will contain the formatted dates and times to be displayed on the x-axis of the graph.
            datelist = []
            # [waterlevellist] will contain the tide levels to be graphed.
            waterlevellist = []

            tz = gettimezone(float(self.metadata['lat']), float(self.metadata['lon']))

            self.progresstextvar.set("Fetching NOAA tide data...\nThis may take a while.")
            self.progresswindow.update()
            try:
                # Start and end dates are padded by -/+ 1 day to compensate for UTC often being a day away from local time.
                self.dataTides = fetchTides(self.varStation.get(), self.dateStart-timedelta(days=1), self.dateEnd+timedelta(days=1))
            except Exception as e:
                messagebox.showerror("Error", "Exception raised while retrieving tide data:\n\n(%s)" % e)
                raise
                self.progresswindow.destroy()
            if 'error' in self.dataTides:
                messagebox.showerror("Error", "Server returned error while retrieving tide data:\n\n(%s)" % self.dataTides['error']['message'])
                raise Exception("Server returned error while retrieving tide data: %s" % self.dataTides['error']['message'])
                self.progresswindow.destroy()

            self.tidesDict = {}
            for datum in self.dataTides['predictions']:
                self.tidesDict[datum['t']] = datum['v']

            thisDate = self.dateStart
            # Iterate through each date in the range.
            while thisDate <= self.dateEnd:
                # Fetch sunrise/sunset data for this date and location.
                # Get lat/long from station metadata.
                self.progresstextvar.set("Fetching sunrise/sunset data for %s at %s, %s..." % (str(thisDate)[:10], self.metadata['lat'], self.metadata['lon']))
                self.progresswindow.update()
                self.dataSun = getjsonURL("https://api.sunrise-sunset.org/json?lat=%s&lng=%s&date=%s&formatted=0" % (self.metadata['lat'],
                                                                                                                     self.metadata['lon'],
                                                                                                                     str(thisDate)[:10]))
                # The exact time of sunrise/set in UTC.
                sunTime = self.dataSun['results'][str.lower(self.varRiseSet.get())][0:-9]
                # Convert it to a datetime object.
                sunDatetime = datetime.strptime(sunTime, "%Y-%m-%dT%H:%M")
                # Add formatted datetime to [datelist] to be graphed on x-axis.
                sunDatetimeLocal = utc_to_local(sunDatetime, tz)
                datelist.append(sunDatetimeLocal.strftime("%#m/%#d\n%#I:%M\n%p"))

                # Add tide levels to [waterlevellist] to be graphed on y-axis.
                waterlevellist.append(float(self.tidesDict[sunDatetime.strftime("%Y-%m-%d %H:%M")]))

                # Move on to the next day in the range.
                thisDate += timedelta(days=1)

            # Exit progress window when done loading data.
            self.progresswindow.destroy()

            # Graph data.
            y_pos = np.arange(len(datelist))
            plt.clf()
            plt.bar(y_pos, waterlevellist, align='center')
            plt.xticks(y_pos, datelist)
            plt.xlabel("%s date/time (Timezone: %s)" % (self.varRiseSet.get(), tz))
            plt.ylabel("Height (ft.)")
            plt.title("Tide levels at %s at station %s (%s)" % (str.lower(self.varRiseSet.get()), self.metadata['name'], self.metadata['id']))
            plt.show()



        self.buttonGo = ttk.Button(text="Go", command=go).grid(row=8, column=0, columnspan=6, padx=5, pady=(10, 5))


if __name__ == '__main__':
    root = Tk()
    RUN_GUI = GUI(root)
    root.mainloop()
