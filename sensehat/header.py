from csv import writer
with open('/home/pi/data.csv', 'a') as f:
    data = writer(f)
    data.writerow(['temperature (Celsius)','pressure (~ 1000 millibars)','humidity (40-60%)','datetime'])
