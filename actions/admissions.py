import requests
import json


def Admissions(institute, location):
    base_url = "http://localhost:3001/admissions"

    # Final_url = base_url + "appid=" + API_key + "&q=" + city + "&units=metric"
    Final_url = base_url
    PARAMS = {'institute': institute, 'location': location}
    admissions_data = requests.post(Final_url, params=PARAMS)

    print("Hello World", PARAMS)
    return admissions_data.json()
