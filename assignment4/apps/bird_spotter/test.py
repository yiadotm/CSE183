import requests
import json

url = "http://localhost:8000/bird_spotter/api/birds/2"  # replace with your actual URL
headers = {'Content-Type': 'application/json'}  # specify JSON content type
data = {"habitat": "south pole", "weight": 21.0}  # the data to update

response = requests.put(url, headers=headers, data=json.dumps(data))

print(response.status_code)
print(response.json())

# res = fetch(
#     "PUT", self.url + "api/birds/2", {"habitat": "south pole", "weight": 20.0}
# )
# assert res["updated"] and not res["errors"], "Invalid response"
