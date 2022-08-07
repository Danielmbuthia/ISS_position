import time
import requests
from datetime import datetime
import smtplib
from dotenv import dotenv_values

config = dotenv_values()


MY_LAT = int(config.get('MY_LAT'))
MY_LONG = int(config.get('MY_LONG'))
MY_EMAIL = config.get('MY_EMAIL')
MY_PASSWORD = config.get('MY_PASSWORD')


# Your position is within +5 or -5 degrees of the ISS position.
def is_near_my_position():
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()
    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])
    if MY_LAT - 5 >= iss_latitude <= MY_LAT + 5 and MY_LONG - 5 >= iss_longitude <= MY_LONG + 5:
        return True


def is_night():
    parameters = {
        "lat": MY_LAT,
        "lng": MY_LONG,
        "formatted": 0,
    }

    response = requests.get(url="http://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    data = response.json()

    sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])

    time_now = datetime.now()
    if time_now.hour >= sunset or time_now.hour <= sunrise:
        return True


while True:
    time.sleep(60)  # after every 60 sec
    if is_night() and is_near_my_position():
        with smtplib.SMTP('smtp.gmail.com') as connection:
            connection.starttls()
            connection.login(user=MY_EMAIL, password=MY_PASSWORD)
            connection.sendmail(
                from_addr=MY_EMAIL,
                to_addrs=MY_EMAIL,
                msg="Subject:ISS POSITION\n\nIss passing over look up!"
            )
