from clients.esm.shakemap import Shakemap

smap = Shakemap()
stationlist = smap.query(
    eventid='20170524_0000045', catalog='EMSC', format='event_dat')
for station in stationlist.get_stations():
    print(station['name'])

    for component in station['components']:
        print(component['name'], component['acc'])

