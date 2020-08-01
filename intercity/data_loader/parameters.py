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

    return parameters

def get_unique_id():
    return "this-is-unique-id"