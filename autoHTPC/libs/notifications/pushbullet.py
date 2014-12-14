import json
import requests
from requests.auth import HTTPBasicAuth

HOST = "https://api.pushbullet.com/v2"

class PushBullet():
    def __init__(self, apiKey):
        self.apiKey = apiKey

    def _request(self, method, url, postdata=None, params=None, files=None):
        headers = {"Accept": "application/json",
                   "Content-Type": "application/json",
                   "User-Agent": "pyPushBullet"}

        if postdata:
            postdata = json.dumps(postdata)

        r = requests.request(method,
                             url,
                             data=postdata,
                             params=params,
                             headers=headers,
                             files=files,
                             auth=HTTPBasicAuth(self.apiKey, ""))

        r.raise_for_status()
        return r.json()

    def getDevices(self):
        return self._request("GET", HOST + "/devices")["devices"]
		
    def pushNote(self, recipient, title, body):
        data = {"type": "note",
                "title": title,
                "body": body}
				
        data['device_iden'] = recipient

        return self._request("POST", HOST + "/pushes", data)
