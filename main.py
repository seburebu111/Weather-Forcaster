
import configparser
from datetime import datetime
import json
import requests


class WeatherForecaster:
    def __init__(self): 
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.apiUrl = config['API']['apiUrl']
        self.apiKey = config['API']['apikey']
        self.city = config['LOCATION']['city']
        
    def _writeResponse(self, jsonStr: str):
        with open('response.json', 'w') as file:
            json.dump(jsonStr, file)
    
    def _makeRequest(self):
        requestParams = {
            'access_key' : self.apiKey,
            'query' : self.city
        }
        response = requests.get(url = self.apiUrl, params = requestParams)
        if response.status_code == 200:
            if response.json().get('error', False):
                print("Could not see clearly...", response.json()['error']['info'])
                return False
            self._writeResponse(response.json())
            return True
        else:
            print("Could not see clearly...")
            return False
        
    def _isExpired(self) -> bool:
        with open('response.json', 'r') as file:
            obs = json.load(file)
        try:
            dtObs = datetime.strptime(obs['location']['localtime'], "%Y-%m-%d %H:%M")
            minDif = (datetime.now() - dtObs).total_seconds() / 60
            minDif = int(minDif)
            print("The observation is", minDif, "min old.")
            if minDif < 10:
                print("No need for a new request, observation is fresh!")
                return False
            else:
                print("I need to observe the sky again, please wait!")
                return True
        except:
                print("My last observation was not proper, trying again!")
                return True
             
    def _readWeather(self):
        with open('response.json', 'r') as file:
            jsonObj = json.load(file)
        
        textFormat = "In {}, at {}, the temperature is {}, with the forecast being {}"
        try:
            place = jsonObj['location']['name'] + ', ' + jsonObj['location']['country']
            time = jsonObj['current']['observation_time']
            temp = jsonObj['current']['temperature']
            forecast = "".join(jsonObj['current']['weather_descriptions'])
        except:
            print("Observation was faulty, try again!") 
            return

        message = textFormat.format(place, time, temp, forecast)
        print(message)

    def getForecast(self):
        if self._isExpired():
            if self._makeRequest():
                print("Completed observation!")
                self._readWeather()
    
    
if __name__ == '__main__':
    wf = WeatherForecaster()
    wf.getForecast()
    