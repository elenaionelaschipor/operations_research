# created by Elena
# 30/08/25

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import collections as mc   
import gurobipy as grb


# -----------------------------------------------------------------

def sim1(pixel1, pixel2):  # misura di somiglianza
    # pixel1 and pixel2 are both grayscale pixel values
    return 1/(0.001 + abs(pixel1 - pixel2)/255)

def sim2(pixel1, pixel2):
    return 1/(0.001 + abs(pixel1 - pixel2)/255)**2
# -----------------------------------------------------------------

def costruisci_grafo_base(image):
    G = nx.Graph()
    h, w = image.shape
    for i in range(h):
        for j in range(w):
            G.add_node((i, j), intensity=image[i, j])
            if i > 0:
                G.add_edge((i, j), (i-1, j), 
                weight1=sim1(image[i, j], image[i-1, j]),
                weight2=sim2(image[i, j], image[i-1, j])
                )
            if j > 0:
                G.add_edge((i, j), (i, j-1),
                weight1=sim1(image[i, j], image[i, j-1]), 
                weight2=sim2(image[i, j], image[i, j-1])
                )
    return G


# ------------------------------------------------------------------------------

def Plot_graph(G,stop = False, values = None, scattercolor = "grey", fig = None, ax = None):
    # adattato dal Plot_tour fatto a lezione
    # G = grafo
    # values = vettore dei pesi associati ai nodi, consigliati tra 0 e 1
    
    # Ps = positions, list of points in R^2 (coordinates!)
    # Ls = lists of successive points that i visit (indices!)
        # values are for color plotting, used in the LP relax
    Ps = G.nodes()

    Ls = G.edges()
    lines = [[(l, k), (j, i)] for (i,j), (k,l) in Ls]
    if fig == None and ax == None:
        fig, ax = plt.subplots()

    # Normalizza i valori tra 0 e 1
    if values == None:
        values = [1 for _ in range(len(G.nodes()))]  
        norm = plt.Normalize(1, 1)

    else: 
        norm = plt.Normalize(min(values), max(values))
    from matplotlib.colors import LinearSegmentedColormap
    
    rainbow_to_white = LinearSegmentedColormap.from_list(
    'rainbow_to_white',
    ['black', 'purple', 'red', 'orange', 'yellow', 'green', 'blue', 'cyan', 'white']
    )
    cmap = rainbow_to_white
    lc = mc.LineCollection(
        lines,
        colors=[cmap(norm(x)) for x in values]
    )
   
    ax.add_collection(lc)
    ax.scatter([j for i,j in Ps], [i for i,j in Ps], 
                s=20, alpha=0.8, color=scattercolor)           # plot the points
    ax.set_ylim(ax.get_ylim()[::-1])
    
    ax.margins(0.1)
    ax.axis('equal')
    if not stop:
        plt.show()
        return fig, ax
    return fig, ax


# ------------------------------------------------------
def two_cut(G, edges, node_in):
    G.remove_edges_from(edges)
    S, S_bar = nx.connected_components(G)        
    if node_in != None:
        if node_in in S:
            return S, S_bar
        else:
            return S_bar, S

#-----------------------------------------------------------------------------------
def get_cutted_edges(S, S_bar, G):
    return [edge for edge in G.edges() if edge[0] in S and edge[1] in S_bar]


# ------------------------------------------------------------------------------------
def capacity1(sets, G, cutted_edges = None):
    if len(sets) == 1:
        S = sets[0]
        # S_bar = nx.difference(G, S)
        S_bar = G.copy()
        S_bar.remove_nodes_from(n for n in G if n in S)
        print(S_bar)
        if cutted_edges == None:
            cutted_edges = get_cutted_edges(S, S_bar, G)
            print(cutted_edges)
        return sum([G[u][v]['weight1'] for u, v in cutted_edges])
        
    else:
        if nx.union_all(sets).nodes() == G.nodes():
            tot = 0
            for k in range(len(sets)):
                V_k = sets[k]
                V_k_bar = G.copy()
                V_k_bar.remove_nodes_from(n for n in G if n in V_k)
                if cutted_edges == None:
                    cutted_edges = get_cutted_edges(V_k, V_k_bar, G)
                tot += 0.5 * sum([G[u][v]['weight1'] for u, v in cutted_edges])
            return tot
        else:
            raise ValueError("Invalid sets, the union is not G")

#-------------------------------------------------------------------------------

def Plot_graph_cuts(sets, G):
    fig, ax = Plot_graph(G, stop = True, values = None)

    cmap = plt.get_cmap('tab20')  # puoi cambiare colormap se vuoi
    n = len(sets)
    colors = [cmap(i % cmap.N) for i in range(n)]

    for idx, V in enumerate(sets):
        fig, ax = Plot_graph(V, stop = True, values = None, scattercolor = colors[idx], fig = fig, ax = ax)
    plt.show()

# --------------------------------------------------------------------------------

def Plot_image_cuts(sets, G):
    h = max([a[1] for a in G.nodes()]) + 1
    w = max([a[0] for a in G.nodes()]) + 1

    image = np.repeat(np.array([G.nodes()[n]['intensity']/255 for n in G.nodes()])
                                .reshape(w,h,1), 3, axis=-1)

    cmap = plt.get_cmap('tab20')
    # print(cmap)
    for idx, V in enumerate(sets):
        # color = np.array(cmap(idx % cmap.N)[:])
        for node in V.nodes():
            image[node[0], node[1], :] = 0.7 * image[node[0], node[1], :] + 0.3*np.array([cmap(idx % cmap.N)[:3]])
    plt.imshow(image)
    plt.axis('off')
    plt.show()

# --------------------------------------------------------------------------------

def volume(S, G):
    return sum([ sum([G.edges[node, k]["weight1"] if (node,k) in G.edges() else 0 for k in G.nodes()] ) for node in S])

def Laplacian(G):
    return np.diag([volume([singoletto], G) for singoletto in G.nodes()]) - nx.adjacency_matrix(G)


# -----------------------------------------------------------------------

def costruisci_grafo_st(G, lambda_, source, sink):
    G_primo = nx.DiGraph()

    for n in G.nodes():
        G_primo.add_node(x := 'x' + str(n)) # aggiungo nodo per ogni nodo di G
    for n1, n2 in G.edges():
        G_primo.add_edge(n1, n2, weight = G.edges[n1, n2]['weight1'])
        G_primo.add_edge(n2, n1, weight = G.edges[n1, n2]['weight1'])
    G_primo.add_node('s')
    G_primo.add_node('t')
    for e in G.edges():
        # creo le y_ij per ogni collegamento tra xi e xj che chiamo e di edges
        G_primo.add_node(y := 'e' + str(e))  # aggiungo nodo per ogni arco
        G_primo.add_edge(y, e[0], weight = float("inf"))  # collego il nodo e ai due estremi
        G_primo.add_edge(y, e[1], weight= float("inf"))
    
    for e in G.edges():
        # collego le y al source s
        if e != source:
            G_primo.add_edge('s', 'e' + str(e), weight = lambda_ * G.edges[e]['weight2'])  # collego s a ogni nodo y_ij
        if e == source:
            G_primo.add_edge('s', 'e' + str(e),  weight = float("inf")) 
    # collego t ai due estremi del sink

    G_primo.add_edge(sink[0], 't', weight = float("inf"))  
    G_primo.add_edge(sink[1], 't', weight = float("inf"))

    return G_primo

# --------------------------------------------------------

def MinCut(image, source_pixels, sink_pixels, lambda_):
    G = costruisci_grafo_base(image)
    # source_pixels devono essere una lista [(x1,y1), (x2,y2)] e sink_pixels [(x3,y3), (x4,y4)] 
    source = (source_pixels[0], source_pixels[1]) # come edge del grafo
    sink = (sink_pixels[0], sink_pixels[1]) # come edge del grafo

    # G_st = costruisci_grafo_st(G, lambda_, source, sink) # ora ho il grafo con s e t come nodi
    
    
    from gurobipy import Model, GRB, quicksum
    model = Model()
    

    # ora dato il grafo dobbiamo scrivere il problema di min cut
    
    x = {}      # x[node] = 1 se node è nel source set
    for index, node in enumerate(G.nodes()): 
        x[node] = model.addVar(lb=0, ub=1,  vtype=GRB.CONTINUOUS, name=f"x_{node}")

    y = {}      # y[edge] = 1 se edge è nel source set
    for index, edge in enumerate(G.edges()): 
        # print(edge)
        y[edge] = model.addVar(lb=0, ub=1, obj = - lambda_*G.edges[edge]['weight2'],  vtype=GRB.CONTINUOUS, name=f"y_{edge}")
    z = {}      # z[edge] = 1 se edge è nel cut
    for index, edge in enumerate(G.edges()): 
        z[edge] = model.addVar(lb=0, ub=1, obj = G.edges[edge]['weight1'], vtype=GRB.CONTINUOUS, name=f"z_{edge}")


    # constraints su source e sink
    model.addConstr(y[source] == 1)
    model.addConstr(y[sink] == 0) 

    for edge in G.edges():
        # se y_ij = 1 allora x_i = 1 e x_j = 1
        model.addConstr(y[edge] <= x[edge[0]])
        model.addConstr(y[edge] <= x[edge[1]])
        # se x_i = x_j = 1 allora z_ij = 0 (sono nello stesso set) (idem se tutto 0)
        # se x_i != x_j allora z_ij = 1 (sono in set diversi)
        model.addConstr(z[edge] >= x[edge[0]] - x[edge[1]])
        model.addConstr(z[edge] >= x[edge[1]] - x[edge[0]])


    model.modelSense = grb.GRB.MINIMIZE
    model.update()

    model.optimize()

    if model.status == GRB.OPTIMAL:
        print('Optimal objective: %g' % model.objVal)
        sol_x = model.getAttr('x', x)
        sol_y = model.getAttr('x', y)
        sol_z = model.getAttr('x', z)
        # print("solution x:", sol_x)
        # print("solution y:", sol_y)
        # print("solution z:", sol_z)

        source_set = [node for node in G.nodes() if sol_x[node] > 0.5]
        sink_set = [node for node in G.nodes() if sol_x[node] <= 0.5]

        return source_set, sink_set, model.objVal, sol_x, sol_y, sol_z  
    else:
        print("No optimal solution found, model.status =", model.status)
        return None, None, None

# --------------------------------------------------------

def parametric_min_cut(image, source_pixels, sink_pixels, time_limit = 300, max_iter = 100):
    from time import time
    start_time = time()
    G = costruisci_grafo_base(image)
    # source_pixels devono essere una lista [(x1,y1), (x2,y2)] e sink_pixels [(x3,y3), (x4,y4)] 
    source = (source_pixels[0], source_pixels[1]) # come edge del grafo
    sink = (sink_pixels[0], sink_pixels[1]) # come edge del grafo
 
    best_lambda = None
    best_cut_value = float('inf')
    best_source_set = None
    best_sink_set = None

    lambda_1 = -1.0
    lambda_3 = 1.0
    iter = 0
    while lambda_3 - lambda_1 > 0.01:  # precisione di 0.01
        source_1, sink_1, cut_value_1, sol_x1, sol_y1, sol_z1 = MinCut(image, source_pixels, sink_pixels, lambda_1)
        source_3, sink_3, cut_value_3, sol_x3, sol_y3, sol_z3 = MinCut(image, source_pixels, sink_pixels, lambda_3)
        
        print("########################## Iteration {}, lambda_1 = {}, cut_value_1 = {}, lambda_3 = {}, cut_value_3 = {}".format(iter, lambda_1, cut_value_1, lambda_3, cut_value_3))
        
        if source_1 == None or source_3 == None:
            raise ValueError("MinCut did not return a valid solution for given lambda values.")
        if source_1 == source_3 and sink_1 == sink_3:
            print("Same cut found for both lambda values.")
        if source_1 != source_3 or sink_1 != sink_3:
            print("Different cuts found for lambda_1 = {} and lambda_3 = {}".format(lambda_1, lambda_3))
            

        beta_1 = sum([G.edges[e]['weight2'] for e in G.edges() if sol_y1[e] < 0.5]) - 0 # qua ci sarebbero degli infiniti ma tanto quelli sicuro stanno in T quindi non li conto
        beta_3 = sum([G.edges[e]['weight2'] for e in G.edges() if sol_y3[e] < 0.5]) - 0


        alpha_1 = cut_value_1 - lambda_1*beta_1
        alpha_3 = cut_value_3 - lambda_3*beta_3
        print("###########################alpha_1 = {}, beta_1 = {}, alpha_3 = {}, beta_3 = {}".format(alpha_1, beta_1, alpha_3, beta_3))
        lambda_2 = (alpha_3 - alpha_1) / (beta_1 - beta_3)
        print("########################## Iteration {}, lambda_1 = {}, lambda_3 = {}, lambda_2 = {}".format(iter, lambda_1, lambda_3, lambda_2))
        source_2, sink_2, cut_value_2, sol_x2, sol_y2, sol_z2 = MinCut(image, source_pixels, sink_pixels, lambda_2)
        beta_2 = sum([G.edges[e]['weight2'] for e in G.edges() if sol_y2[e] < 0.5]) - 0

        alpha_2 = cut_value_2 - lambda_2*beta_2

        if abs(beta_2) <= 0.0000000000001:
            best_lambda = lambda_2
            best_source_set = source_2
            best_sink_set = sink_2
            best_cut_value = cut_value_2
            break

        if beta_2 > 0:
            print(" ------------------ Updating lower bound.")
            lambda_1 = lambda_2
            sink_1 = sink_2
            source_1 = source_2
            cut_value_1 = cut_value_2
            alpha_1 = alpha_2
            beta_1 = beta_2
            sol_x1 = sol_x2
            sol_y1 = sol_y2
            sol_z1 = sol_z2
        else:
            print(" ------------------ Updating upper bound.")
            lambda_3 = lambda_2
            sink_3 = sink_2
            source_3 = source_2
            cut_value_3 = cut_value_2
            alpha_3 = alpha_2
            beta_3 = beta_2
            sol_x3 = sol_x2
            sol_y3 = sol_y2
            sol_z3 = sol_z2

        iter += 1
        print("Current lambda range: [{}, {}] --------------------------------- ".format(lambda_1, lambda_3))
        if time() - start_time > time_limit:
            print("Time limit reached.")
            break
        if iter > max_iter:
            print("Maximum iterations reached.")
            break

    return best_source_set, best_sink_set, best_lambda, best_cut_value



if __name__ == "__main__":
    image = plt.imread('C:/Users/elena/Documents/GitHub/operations_research/project_2025/images/cane_piccolo.jpg')

    plt.imshow(image)
    plt.axis('off')
    plt.show()

    image_bn = np.mean(image, axis=2)

    plt.imshow(image_bn, cmap='gray')
    plt.axis('off')
    plt.show()

    # print(image_bn)
    G = costruisci_grafo_base(image_bn)
    # print(G.edges(data=True))
    Plot_graph(G, values = [k[2]['weight1'] for k in G.edges(data=True)])   # giustamente in una immagine ad alta risoluzione non si vede il reticolo

    print("prova del 9 con la capacità")
    print("capacità di G con taglio G = ",  capacity1([G], G)) 

    print("tentativo di dividere")

    print("nodi totali ", len(G.nodes))
    
    sets = []
    for i in range(11):
        sub_nodes = list(G.nodes)[i*6750: 6750*(i+1)]  # primi 100 nodi
        V= G.subgraph(sub_nodes)
        sets.append(V)

    print("cut cost:", capacity1(sets, G))

    # print("plotting cuts")
    # Plot_graph_cuts(sets, G)

    # Plot_image_cuts(sets, G)
    # print(Laplacian(G))


    source_set, sink_set, best_lambda, best_cut_value = parametric_min_cut(image_bn, [(5,5), (5, 6)], [(40, 20), (40,21)])

    print("Best lambda:", best_lambda)
    print("Best cut value:", best_cut_value)



    if source_set != None and sink_set != None:
        print("Source set size:", len(source_set))
        print("Sink set size:", len(sink_set))
        Plot_image_cuts([G.subgraph(source_set), G.subgraph(sink_set)], G)
        