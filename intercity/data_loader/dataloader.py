import requests
import numpy as np
import pandas as pd
import json

from data_loader.credintials import URL, UserName, Password
# from credintials import URL, UserName, Password

class sessionManager():
    def __init__(self):

        url = URL+"_session"

        payload = 'name='+UserName+'&password='+Password
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data = payload)

        self.AuthToken = response.headers['Set-Cookie'].split(";")[0][12:]

    def get_token(self):
        return self.AuthToken

class Nodes(object):
    def __init__(self, AuthToken):
        url = URL+"covidsimteam/districts"

        cookie = dict(AuthSession=AuthToken)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CouchDB-WWW-Authenticate': 'Cookie'
        }

        response = requests.request("GET", url, headers=headers, cookies=cookie)
        # print(response.text.encode('utf8'))

        response_json = json.loads(response.text.encode('utf8'))

        self.nodes_df = pd.json_normalize(response_json["districts"])
        self.health_data(AuthToken)
        self.nodes_df.rename({"index":"id"}, axis=1, inplace=True)

    def health_data(self, AuthToken):
        url = URL+"covidsimteam/provinces"
        cookie = dict(AuthSession=AuthToken)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CouchDB-WWW-Authenticate': 'Cookie'
        }
        response = requests.request("GET", url, headers=headers, cookies=cookie)
        
        response_json = json.loads(response.text.encode('utf8'))
        health_df = pd.json_normalize(response_json["provinces"])
    
        health_data = []
        for _,v in self.nodes_df.iterrows():
            province = str(v["province"])
            health_data.append(float(health_df.loc[(health_df["Name of Government Unit"]=="Province "+province)]["Index"]))
        self.nodes_df["health_index"] = health_data

    def nodes(self):
        return self.nodes_df

    def get_index(self):
        indexdict = {}
        index = 0
        for _,v in self.nodes_df.iterrows():
            indexdict[index] = v["Districts"]
            index += 1
        return indexdict
        

class Weights():
    def __init__(self, AuthToken, indexlabeldict):
        url = URL+"covidsimteam/district_distances"

        cookie = dict(AuthSession=AuthToken)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CouchDB-WWW-Authenticate': 'Cookie'
        }

        response = requests.request("GET", url, headers=headers, cookies=cookie)
        weights_json = json.loads(response.text.encode('utf8'))["district_distances"]
        weights_json = pd.json_normalize(weights_json).set_index("Districts")

        N = len(weights_json)
        weightdict = {}
        index = 0
        for i in range(N):
            for j in range(N):
                if not i == j:
                    weightdict[index] = [i,j,weights_json[indexlabeldict[i]][indexlabeldict[j]]]
                    index += 1

        self.weights_df = pd.DataFrame.from_dict(weightdict, orient="index", columns=["src","dst","Weight"])
        self.weights_df["Weight"] /= self.weights_df["Weight"].max()

    def weights(self):
        return self.weights_df

if __name__=="__main__":
    session = sessionManager().get_token()

    n = Nodes(session)
    e = Weights(session, n.get_index())
    print(n.nodes(), e.weights())

