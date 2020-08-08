import pycouchdb
# from credintials import URL_LOCAL, UserName_LOCAL, Password_LOCAL
from data_loader.credintials import URL_LOCAL, UserName_LOCAL, Password_LOCAL

def get_parameters():
    parameters = {}
    parameters["nc_tau"] = 1
    parameters["nc_M"] = 1
    parameters["sigma"] = 25
    parameters["alpha"] = 0.1 
    parameters["beta"] = 0.01 
    parameters["theta"] = 10
    parameters["a"] = 4.0
    parameters["b"] = 3.0
    parameters["function"] = "errf"
    parameters["samples"] = 100
    parameters["simwindow"] = 100

    return {"parameters": parameters, "_id":"data['_id']"}

class couchServer():
    def __init__(self):
        server = pycouchdb.Server("http://"+UserName_LOCAL+":"+Password_LOCAL+"@"+URL_LOCAL)
        self.db_results = server.database("intercity_results")
        self.db_dashboard = server.database("intercity_dashboard")
        try:
            seq_file = open(".seq","r")
            self.last_seq = seq_file.read()
            seq_file.close()
        except:
            self.last_seq = None
        
    def write(self, last_seq):
        seq_file = open(".seq","w")
        seq_file.write(last_seq)
        seq_file.close()

    def save(self,data,db="results"):
        if db=="results":
            return self.db_results.save(data)
        elif db=="dashboard":
            return self.db_dashboard.save(data)

    def changes_feed(self, callback, **kwargs):
        self.db_dashboard.changes_feed(callback,**kwargs)

if __name__ == "__main__":
    couchserver = couchServer()
    print(couchserver.save({"name":"Password"}))