from sense_hat import SenseHat
from datetime import datetime
from csv import writer

# setup
sense = SenseHat()
sense.clear()

# lib
def get_sense_data():
    sense_data = []
    sense_data.append(datetime.now())
    sense_data.append(round(sense.get_temperature_from_pressure(), 2)) # more accurate
    sense_data.append(round(sense.get_pressure(), 2))
    sense_data.append(round(sense.get_humidity(), 2))
    return sense_data

# main
with open('/home/pi/data.csv', 'a') as f:
    sense.clear(64,64,64)
    data_writer = writer(f)
    data_writer.writerow(get_sense_data())
    sense.clear()
