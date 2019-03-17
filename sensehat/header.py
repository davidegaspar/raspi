from csv import writer
with open('/home/pi/data.csv', 'a') as f:
    data = writer(f)
    data.writerow(['datetime','temperature (C)','pressure (millibars)','humidity (%)'])
