# created by Elena
# same functions of project_copy but no tests 

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import collections as mc   
import gurobipy as grb


# -----------------------------------------------------------------


def sim1(pixel1, pixel2,sigma, medical = False):  # misura di somiglianza esponenziale
    
    if medical: # nelle immagini "mediche" il nero è lo sfondo che non ci interessa, per evitare che faccia il cut tra tutto il soggetto e lo sfondo invece del tumore
        # pixel1 and pixel2 are both grayscale pixel values
        if pixel1 == 0 or pixel2 == 0:
            return 1000
        return np.exp(-abs(pixel1 - pixel2)/sigma)
    else:
        return np.exp(-abs(pixel1 - pixel2)/sigma)


def sim2(pixel1, pixel2,sigma, medical = False):
    
    if medical:
        if pixel1 == 0 or pixel2== 0:
            return 1000
        return 1/(1 + (abs(pixel1 - pixel2)/sigma)**2)
    else:
        return 1/(1 + (abs(pixel1 - pixel2)/sigma)**2)
# -----------------------------------------------------------------

def costruisci_grafo_base(image, medical = False):
    G = nx.Graph()
    w,h = image.shape
    if np.max(image) > 1:
        image = image/255
    
    sigma = 1# np.std(image) + 1e-5
    print(sigma)
    for i in range(w):
        for j in range(h):
            G.add_node((i, j), intensity=image[i, h-1-j])
            if i > 0:
                G.add_edge((i, j), (i-1, j), 
                weight1=sim1(image[i, j], image[i-1, h-1-j], sigma,medical),
                weight2=sim2(image[i, j], image[i-1, h-1-j],sigma, medical)
                )
            if j > 0:
                G.add_edge((i, j), (i, j-1),
                weight1=sim1(image[i, j], image[i, h-j], sigma, medical), 
                weight2=sim2(image[i, j], image[i, h-j], sigma, medical)
                )
    return G


# ------------------------------------------------------------------------------

def Plot_graph(G,stop = False, values = None, scattercolor = "grey", fig = None, ax = None):
    # adattato dal Plot_tour fatto a lezione
    # G = grafo
    # values = vettore dei pesi associati ai edges, consigliati tra 0 e 1
    h = max([a[1] for a in G.nodes()]) + 1
    w = max([a[0] for a in G.nodes()]) + 1

    # Ps = positions, list of points in R^2 (coordinates!)
    # Ls = lists of successive points that i visit (indices!)
        # values are for color plotting, used in the LP relax
    Ps = G.nodes()

    Ls = G.edges()
    lines = [[(i,j), (k,l)] for (i,j), (k,l) in Ls]
    # lines = [[((l, k), (j, i))] for (i,j), (k,l) in Ls]
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


    for ((i, j), (k, l)), val in zip(G.edges(), values):
        y_mid = (j + l) / 2
        x_mid = (i + k) / 2
        ax.text(x_mid, y_mid, f"{val:.2f}", fontsize=6, color='black', alpha=0.5, ha='center', va='center')

   
    ax.scatter([i for i,j in Ps], [j for i,j in Ps], 
                s=20, alpha=0.8, color=scattercolor) # plot the points
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
        # print(S_bar)
        if cutted_edges == None:
            cutted_edges = get_cutted_edges(S, S_bar, G)
            # print(cutted_edges)
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

def Plot_image_cuts(sets, G, source_pixels = None, sink_pixels = None, image_name =None):
    h = max([a[1] for a in G.nodes()]) + 1
    w = max([a[0] for a in G.nodes()]) + 1

    image = np.zeros((w, h, 1))
    for i,j in G.nodes():
        image[i, h-1-j] = G.nodes()[i,j]['intensity']
    
    image = np.repeat(image, 3, axis=-1)
    from matplotlib.colors import ListedColormap
    cmap =  ListedColormap(["red", "blue"])
    # print(cmap)
    for idx, V in enumerate(sets):
        # color = np.array(cmap(idx % cmap.N)[:])
        for node in V.nodes():
            n = (node[0],  h-1-node[1])
            image[n[0], n[1], :] = 0.7 * image[n[0], n[1], :] + 0.3*np.array([cmap(idx % cmap.N)[:3]])
    plt.imshow(image)
    if source_pixels != None and sink_pixels != None:
        for sp in source_pixels:
            plt.scatter(sp[0], sp[1], color='black', s=100, marker='*', label='Source Pixel' if sp == source_pixels[0] else "")
        for tp in sink_pixels:
            plt.scatter(tp[0], tp[1], color='black', s=100, marker='4', label='Sink Pixel' if tp == sink_pixels[0] else "")
        plt.legend(loc='upper right')
    plt.axis('off')
    if image_name == None:
        plt.show()
    else:
        plt.savefig(image_name[:-4] + "_segmented.png")
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
    source = (source_pixels[1], source_pixels[0]) # come edge del grafo
    sink = (sink_pixels[1], sink_pixels[0]) # come edge del grafo

    # print(source, sink)
    # G_st = costruisci_grafo_st(G, lambda_, source, sink) # ora ho il grafo con s e t come nodi
    
    
    from gurobipy import Model, GRB, quicksum
    model = Model()
    model.setParam("OutputFlag", 0)
    # ora dato il grafo dobbiamo scrivere il problema di min cut
    
    x = {}      # x[node] = 1 se node è nel source set
    for index, node in enumerate(G.nodes()): 
        x[node] = model.addVar(lb=0, ub=1,  vtype=GRB.CONTINUOUS, name=f"x_{node}") 

    y = {}      # y[edge] = 1 se edge è nel source set<
    z = {}      # z[edge] = 1 se edge è nel cut
    for index, edge in enumerate(G.edges()): 
        # print(edge)
        y[edge] = model.addVar(lb=0, ub=1, obj = - lambda_*G.edges[edge]['weight2'],  vtype=GRB.CONTINUOUS, name=f"y_{edge}")
    
        z[edge] = model.addVar(lb=0, ub=1, obj = G.edges[edge]['weight1'], vtype=GRB.CONTINUOUS, name=f"z_{edge}")
        z[(edge[1], edge[0])] = z[edge]  # perchè il grafo è undirected
    
    # constraints su source e sink (devo fare questo if perchè il grafo è undirected ma il dizionario è directed)
    if source in y:
        model.addConstr(y[source] == 1)
        print("weights around the source")
        print(G.edges[source]["weight1"])

    elif (source[1], source[0]) in y:
        model.addConstr(y[(source[1], source[0])] == 1)

    if sink in y:
        model.addConstr(y[sink] == 0)
    elif (sink[1], sink[0]) in y:
        model.addConstr(y[(sink[1], sink[0])] == 0)

    for edge in G.edges():
        # se y_ij = 1 allora x_i = 1 e x_j = 1
        model.addConstr(y[edge] <= x[edge[0]])
        model.addConstr(y[edge] <= x[edge[1]])
        # se x_i = x_j = 1 allora z_ij = 0 (sono nello stesso set) (idem se tutto 0)
        # se x_i != x_j allora z_ij = 1 (sono in set diversi)
        model.addConstr(z[edge] >= x[edge[0]] - x[edge[1]])
        model.addConstr(z[(edge[1], edge[0])] >= x[edge[1]] - x[edge[0]])
        model.addConstr(y[edge] >= x[edge[0]] + x[edge[1]] - 1)
        model.addConstr(1+z[edge] >= y[edge])
        model.addConstr(1+y[edge] >= z[edge])

    print("MODEL CREATED, ADDED CONSTRAINTS, OPTIMIZING....")
    model.modelSense = grb.GRB.MINIMIZE
    model.update()
    
    # model.write("mincut_lambda.lp") 

    model.optimize()
    if model.status == GRB.OPTIMAL:
        print("MODEL OPTIMAL")
        print('Optimal objective: %g' % model.objVal)
        sol_x = model.getAttr('x', x)
        sol_y = model.getAttr('x', y)
        sol_z = model.getAttr('x', z)
        # print("solution x:", sol_x)
        # print("solution y:", [(y, sol_y[y]) for y in sol_y if sol_y[y] < 0.5])
        # print("solution z:", [(z, sol_z[z]) for z in sol_z if sol_z[z]> 0.5])

        source_set = [node for node in G.nodes() if sol_x[node] > 0.5]
        sink_set = [node for node in G.nodes() if sol_x[node] <= 0.5]

        return source_set, sink_set, model.objVal, sol_x, sol_y, sol_z  
    else:
        print("No optimal solution found, model.status =", model.status)
        return None, None, None

# --------------------------------------------------------

def parametric_min_cut(image, source_pixels, sink_pixels, time_limit = 300, max_iter = 100, max_stall = 20):
    from time import time
    start_time = time()
    G = costruisci_grafo_base(image)
    # source_pixels devono essere una lista [(x1,y1), (x2,y2)] e sink_pixels [(x3,y3), (x4,y4)] 
    source = (source_pixels[1], source_pixels[0]) # come edge del grafo
    sink = (sink_pixels[1], sink_pixels[0]) # come edge del grafo

    # best_lambda = None
    # best_cut_value = float('inf')
    # best_source_set = None
    # best_sink_set = None
    iter_ = 0
    stall = 0
    t = 1
    t_his = 1
    source_set, sink_set, cut, sol_x, sol_y, sol_z = MinCut(image, source_pixels, sink_pixels, t) 
    source_his = source_set
    sink_his = sink_set
    cut_his = cut
    x_his = sol_x
    y_his = sol_y
    z_his = sol_z
    while abs(cut) >=  0.00001:
        t = sum([G.edges[e]['weight1'] for e in G.edges() if sol_z[e] > 0.5]) / sum([G.edges[e]['weight2'] for e in G.edges() if sol_y[e] > 0.5])
        print("t = ", t, "------------------------------------------------")
        source_set, sink_set, cut, sol_x, sol_y, sol_z = MinCut(image, source_pixels, sink_pixels, t) 
        iter_ += 1
        flag = ""
        if t == t_his:
            stall += 1
            print("warning, same value of t")
            if source_his == source_set and sink_his == sink_set and x_his == sol_x and y_his == sol_y and z_his == sol_z:
                print("Generating the same partition and the same solutions. Stopping to avoid looping")
                flag = "looping"
                break
        if time() - start_time > time_limit:   
            print("Time limit reached.")
            flag = "time limit reached"
            break
        if iter_ >= max_iter:
            print("max iterations reached.")
            flag = "max iterations reached."
            break
        t_his = t
        source_his = source_set
        sink_his = sink_set
        x_his = sol_x 
        y_his = sol_y
        z_his = sol_z

    return source_set, sink_set, cut, sol_x, sol_y, sol_z, t, flag
