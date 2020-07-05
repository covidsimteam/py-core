import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy.special import erf
from itertools import count
import shapefile as shp
import seaborn as sns
import matplotlib
import datetime

from pyspark import *
from pyspark.sql import *
from graphframes import *

from dataloader.dataloader import sessionManager, Nodes, Weights
from dataloader.parameters import get_parameters

class Network():
    def __init__(self, session, nodes, edges):

        sqlContext = SQLContext(sc)
        nodes_df = sqlContext.createDataFrame(nodes)
        edges_df = sqlContext.createDataFrame(edges) 
        self.graph = GraphFrame(nodes_df, edges_df)

class diseasespread():
    """parameters for the model"""
    def __init__(self, graph, parameters): #one needs to find a good paramter such that ODEs become solvable, and yield physically reliable solutions
        data = 0

    def tau(self, node):
        return(self.nc_tau*14*self.healthcare[node])

    def sigmoid(self, x):
        """two different functions for the disturbances the neighboring nodes creates towards node i"""
        if 1:
            return erf((x)/(self.sigma)) #newly discovered (inspired by a quantum computing research). sigma could be different for every node
        else:
            return (1-np.exp(-self.alpha*x))/(1+np.exp(-self.alpha*(x-self.theta))) #DOI: 10.1103/PhysRevE.75.056107

    def neighbors(self, node):
        """returns the neighboring nodes"""
        return list(self.graph.neighbors(node))

    def M(self,node):
        """link strengths"""
        neighbors = self.neighbors(node)
        Mij=np.zeros_like(np.array(neighbors),dtype=float)
        for nbrid, nbr in enumerate(neighbors):
            # print(nbrid, nbr)
            Mij[nbrid]=self.nc_M*self.weights[self.label[node]][self.label[nbr]]
        return Mij
        # return 

    def Delay(self,node):
        """gives time-delay for disease to spread"""
        neighbors = self.neighbors(node)
        tij = np.zeros_like(neighbors,dtype=float)
        for nbrid, nbr in enumerate(neighbors):
            tij[nbrid] = 1.0
        return tij

    def nodeDegree(self,node):
        """returns node degree"""
        return len(list(self.graph.neighbors(node)))

    def f(self,node):
        """weighs the influence of neighboring nodes on node i"""
        return (self.a*self.nodeDegree(node))/(1+self.b*self.nodeDegree(node))

    def evolve(self,x,t):
        """time-dynamics of all the nodes. time-delay is set to 0 for simplicity"""
        dxdt=np.zeros_like(x,dtype=float)
        fp = np.zeros_like(x,dtype=float)
        sp = np.zeros_like(x,dtype=float)
        for i in range(len(x)):
            if len(np.array(self.neighbors(i+1))-1)==0:
                fp[i] = -x[i] / self.tau(i+1)
                sp[i] = 0
            else:
                xj=x[np.array(self.neighbors(i+1))-1]
                fp[i] = -x[i] / self.tau(i+1)
                sp[i] = self.sigmoid(np.sum(xj * np.array(self.M(i+1)) * np.exp(-self.beta * np.array(self.Delay(i + 1)),dtype=float) / np.array((self.f(i + 1)),dtype=float)))
            dxdt[i] = fp[i] + sp[i]
        # self.firstpart.append(fp)
        # self.secondpart.append(sp)
        return dxdt

if __name__ == "__main__":

    sc = SparkContext("local", "intercity model")

    AuthToken = sessionManager()
    
    #create an object of Nodes
    nodeobject = Nodes(AuthToken.get_token())
    nodes_df = nodeobject.nodes()
    N = len(nodes_df)
    x0 = np.zeros(N)
    x0[0] = 0.1
    nodes_df["x0"] = x0


    weights = Weights(AuthToken.get_token(), nodeobject.get_index())
    weights_df = weights.weights()
    
    space = [1]
    assert N == len(nodes_df)

    network = Network(sc, nodes_df, weights_df)
    graph_rdd = network.graph
    print(graph_rdd.vertices.show())

    parameters_rdd = sc.parallelize(get_parameters())


    # # taulist=np.ones(N)*5 #keep identical healing rates for all the nodes
    # x0=np.ones(N)*0 #at t=0, all other cities are normal
    # x0[24]=0.1 #at t=0, Kathmandu is diseased
    
    # samples=100
    # simuwindow=100 #the evolution is distinctly observed at longer times, so keep the simulation window large
    
    # for i in space:
        
    #     print("normalization tau = "+str(10)+", M = "+str(i))
    #     spread=diseasespread(nodes_df,weights_df,nc_tau=i,nc_M=i)
    #     t=np.linspace(0,simuwindow,samples)
    #     xt=odeint(spread.evolve,x0,t)