from __future__ import division, print_function
"""
Author: Manish Jung Thapa, ETH Zurich
please leave the line above if you want to use or modify this code!
Performs simulations of COVID19 spread between cities in Nepal
Checkout 10.1103/PhysRevE.75.056107 for more details on the model
"""
__author__ = 'Manish J. Thapa'


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

from data_loader.dataloader import Nodes, Weights, sessionManager
from data_loader.parameters import get_parameters
# from data_loader.plot_map import plot_map
# from data_loader.make_folium import make_folium

import myargparse as argparse

parser = argparse.MyArgumentParser(description='infects node')
parser.add_argument('-nodeinfect',default=6,type=int,help='nodeinfect')
args = parser.parse_args()

class diseasespread():
    """parameters for the model"""
    def __init__(self, nodes, weights, parameters): #one needs to find a good paramter such that ODEs become solvable, and yield physically reliable solutions
        self.nlist = nodes["id"].values
        self.elist = list(zip(weights["src"].values,weights["dst"]))
        self.health_index = nodes["health_index"].values
        self.weights = {}
        for _,v in weights.iterrows():
            self.weights["("+str(int(v["src"]))+","+str(int(v["dst"]))+")"] = v["Weight"]

        # print(self.weights)
        
        self.graph = nx.Graph()
        self.graph.add_edges_from(self.elist)
        self.graph.add_nodes_from(self.nlist)
        
        self.nc_tau = parameters["nc_tau"]
        self.nc_M = parameters["nc_M"]
        self.theta = parameters["theta"]
        self.beta = parameters["beta"]
        self.alpha = parameters["alpha"]
        self.sigma = parameters["sigma"]
        self.a = parameters["a"]
        self.b = parameters["b"]

    def tau(self, node):
        return(self.nc_tau*14*self.health_index[node])

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
            wt = float(self.weights["("+str(node)+","+str(nbr)+")"])
            Mij[nbrid]=self.nc_M * wt
        return Mij
         
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
        for i in range(len(x)):
            if len(np.array(self.neighbors(i))-1)==0:
                dxdt[i] = -x[i] / self.tau(i)
            else:
                xj=x[np.array(self.neighbors(i))-1]
                dxdt[i] = -x[i] / self.tau(i) + self.sigmoid(np.sum(xj * np.array(self.M(i)) * np.exp(-self.beta * np.array(self.Delay(i)),dtype=float) / np.array((self.f(i)),dtype=float)))
        return dxdt

if __name__ == "__main__":

    plot = False
    #create an object of Links
    AuthToken = sessionManager()

    nodeobject = Nodes(AuthToken.get_token())
    nodes_df = nodeobject.nodes()
    N = len(nodes_df)
    x0 = np.zeros(N)

    assert args.nodeinfect < N+1
    x0[args.nodeinfect]=0.1 #at t=0 some city is diseased
    print("For node: ", args.nodeinfect)
    nodes_df["x0"] = x0


    weights = Weights(AuthToken.get_token(), nodeobject.get_index())
    weights_df = weights.weights()

    parameters = get_parameters()
    
    assert N == len(nodes_df)

    samples = parameters["samples"]
    simuwindow = parameters["simwindow"] #the evolution is distinctly observed at longer times, so keep the simulation window large
    cnt = 0
        
    spread=diseasespread(nodes_df, weights_df, parameters)
    t=np.linspace(0,simuwindow,samples)
    xt=odeint(spread.evolve,x0,t)

    print(xt, xt.shape)

    results = nodes_df
    for day in range(simuwindow):
        results["x"+str(day)] = xt[day]
    # print(results.head(10))

    #submit code here
    
    if plot:
        plt.plot(t,np.sum(xt, axis=1)/N,color="black", label="total")
        # print(np.sum(xt,axis=1).shape)
        # plt.plot(t,np.sum(np.array(spread.firstpart), axis=1),color="green", label="recovered")
        # plt.plot(t,np.sum(np.array(spread.secondpart), axis=1),color="red", label="new")
        # plt.title("Using erf and sigma = 25, normalization tau = "+str(10)+", M = "+str(i))
        # plt.title("Using sigmoid, normalization tau = "+10+", M = "+str(j))
        plt.title("Infection Plot")
        plt.ylabel("Total Infections (in percent)")
        plt.xlabel("Time (Days)")
        plt.savefig("results/totalplot_"+str(cnt)+".png")

        plt.show()
        plt.clf()
        cnt+=1
        for day in range(int(simuwindow)):
            intensity = xt[day]*100/N
            geofile = "shapefiles/nepal-map-governance/NEPAL_DISTRICTS_WGS.shp"
            save_image = "results/districts_road/map/covid000"+str(int(int(day)))+".png"
            title = 'Day-'+str(int(int(day)))
            plot_map(geofile, intensity, save_image, title)
    
        coordinates = coord.values()
        data = xt*100/N
        make_folium(coordinates, data, datetime.date(year=2020, month=5, day=6), save_file="results/results.html")

        for day in range(int(simuwindow)):
            xt[day] /= N
            nodelist=[]
            for i in range(N):
                dictBook = dict()
                dictBook.setdefault('health', xt[:,i][int(day)])
                nodelist.append((i+1,dictBook.copy()))
            linklist=elist

            plt.figure(figsize=(22, 12))
            G = nx.Graph()
            G.add_nodes_from(nodelist)
            G.add_edges_from(linklist)
            groups = set(nx.get_node_attributes(G,'health').values())
            mapping = dict(zip(sorted(groups),count()))
            nodes = G.nodes()
            colors = [mapping[G.node[nid]['health']] for nid in nodes]
            # neplinks = nx.draw_networkx_edges(G, coord, edge_colors='k', style='dashed', edge_size=1, alpha=0.6)
            nepnodes = nx.draw_networkx_nodes(G, coord, nodelist=nodes, node_color=colors, alpha=0.5,with_labels=True, node_size=700, cmap=plt.cm.jet)
            # nx.draw_networkx_labels(G, coord, labels, font_size=12)
            maxval = np.max(np.array(list(groups),dtype="float"))
            cbar = plt.colorbar(nepnodes,label='Intensity of Infection (in %)')
            cbar.ax.set_yticklabels(np.around(np.linspace(0,maxval,8)*100,decimals=4),size=22)

            text = cbar.ax.yaxis.label
            font = matplotlib.font_manager.FontProperties(size=22)
            text.set_font_properties(font)

            plt.axis('off')

            #draw map of Nepal, need the .shp file
            sns.set(style="whitegrid", color_codes=True)
            sns.mpl.rc("figure", figsize=(10,6))
            pathshp = "shapefiles/nepal_data/npl_admbnda_districts_nd_20190430.shp"
            # pathshp = "npl_admbnda_adm0_nd_20190430.shp"
            shapef = shp.Reader(pathshp)

            def country_map(shapef):
                for shape in shapef.shapeRecords():
                    xcoord = [xpt[0] for xpt in shape.shape.points[:]]
                    ycoord = [ypt[1] for ypt in shape.shape.points[:]]
                    plt.plot(xcoord, ycoord, 'k')
            country_map(shapef)
            print('Time - ',day)
            plt.title('Day-'+str(int(int(day))),fontsize=30)
            plt.savefig('results/districts_road/map1/covid000'+str(int(int(day)))+'.png')

#ffmpeg -r 0.5 -f image2 -s 1920x1080 -i covid%04d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p covidlatest.mp4 #run from the terminal