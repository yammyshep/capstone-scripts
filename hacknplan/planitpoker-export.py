import requests
from iniconfig import IniConfig
import math

class ApiKeyAuth(requests.auth.AuthBase):
    def __init__(self, apiKey):
        self.apiKey = apiKey

    def __call__(self, r):
        r.headers["Authorization"] = "ApiKey " + self.apiKey
        return r

# Get API Key
ini = IniConfig("hacknplan.ini")
apiKey = ini["Credentials"]["ApiKey"]
auth = ApiKeyAuth(apiKey)

projectId = int(ini["Project"]["ProjectID"])
boardId = int(ini["Project"]["BoardID"])
tagId = int(ini["Project"]["PokerTagID"])

totalCount = math.inf
workItems = []

while (len(workItems) < totalCount):
    params = {"boardId": boardId, "offset": len(workItems), "limit": 100}
    print(f"Requesting items {params["offset"]} to {params["offset"] + params["limit"]}")
    r = requests.get(f"https://api.hacknplan.com/v0/projects/{projectId}/workitems", auth=auth, params=params)

    res = r.json()
    if res["totalCount"] < totalCount:
        totalCount = res["totalCount"]

    for item in res["items"]:
        workItems.append(item)


filtered = filter(lambda item: any(tag["tagId"]==tagId for tag in item["tags"]), workItems)

for item in filtered:
    print(f"#{item["workItemId"]}: {"USER STORY: " if item["isStory"] else ""}{item["title"]}")
