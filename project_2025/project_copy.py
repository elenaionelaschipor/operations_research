# created by Elena 


import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import collections as mc   
import gurobipy as grb


import matplotlib 
matplotlib.use('Agg') 
# -----------------------------------------------------------------

import numpy as np

def compute_weight_bounds(image, a):
    # Calcola tutte le differenze tra pixel adiacenti
    diff_h = np.abs(image[:, :-1] - image[:, 1:])
    diff_v = np.abs(image[:-1, :] - image[1:, :])
    all_diffs = np.concatenate([diff_h.flatten(), diff_v.flatten()])
    
    # Calcola i pesi grezzi
    raw_weights = np.exp(-a * all_diffs)
    
    # Trova min e max effettivi (escludendo outlier estremi)
    min_w = np.percentile(raw_weights, 5)
    max_w = np.percentile(raw_weights, 95)
    
    if min_w <= 1e-8:
        min_w = 1e-8
    return min_w, max_w

def sim1(pixel1, pixel2, h, w, a, medical=False, min_w=0.1, max_w=0.9):  # misura di somiglianza esponenziale
    # pixel1 and pixel2 are both grayscale pixel values between 0 and 1
    raw = np.exp(-a * abs(pixel1 - pixel2))
    normalized = (raw - min_w) / (max_w - min_w + 1e-8)  # evita divisione per zero
    normalized = normalized * (max_w - min_w) + min_w  # riscalamento nel range desiderato

    if medical:
        if pixel1 == 0 or pixel2 == 0:
            return 0
        else:
            # return 1/(1 + a*(abs(pixel1 - pixel2)))
            # return np.exp(-a*abs(pixel1 - pixel2))
            return normalized
    else:
        # return np.exp(-a*abs(pixel1 - pixel2))
        # return 1/(1 + a*(abs(pixel1 - pixel2)))
        return normalized

def sim2(pixel1, pixel2, h, w, a, medical, min_w=0.1, max_w=0.9):
    # return np.exp(-a*abs(pixel1 - pixel2))
    # return 1/(h*w)
    # return 1/(1 + a*(abs(pixel1 - pixel2)))
    raw = np.exp(-a * abs(pixel1 - pixel2))
    normalized = (raw - min_w) / (max_w - min_w + 1e-8)
    return normalized * (max_w - min_w) + min_w
# -----------------
def compute_a_global_variance(image, epsilon=1e-5):
        # Calcola le differenze tra pixel adiacenti (orizzontali e verticali)
        diff_h = np.abs(image[:, :-1] - image[:, 1:])
        diff_v = np.abs(image[:-1, :] - image[1:, :])
        all_diffs = np.concatenate([diff_h.flatten(), diff_v.flatten()])
        
        variance = np.var(all_diffs)
        # print("variance of the image", variance)
        # if np.unique(image).size <= 2:
        #     a = 1  # oppure 5, oppure 1, da testare
        # else:
        #     a = 1 / (variance + epsilon)
        # return a
        a = 1 / (variance + epsilon)
        return a

def enhance_contrast(image):
    return (image - np.min(image)) / (np.max(image) - np.min(image) + 1e-8)


def add_noise(image, sigma=0.01):
    """
    Aggiunge rumore gaussiano all'immagine.
    image: array numpy con valori tra 0 e 1
    sigma: deviazione standard del rumore (molto piccolo)
    """
    noise = np.random.normal(loc=0.0, scale=sigma, size=image.shape)
    noisy_image = image + noise 
    return np.clip(noisy_image, 0, 1)  # assicura che i valori restino tra 0 e 1

# ------------------------
def costruisci_grafo_base(image, medical=False):
    G = nx.Graph()
    w,h = image.shape
    # print(h,w)
    # print(np.max(image))
    if np.max(image) > 1:
        image = image/255
    # print(np.max(image))
    eps = 0.001
    

    a = compute_a_global_variance(image, eps)
    min_w, max_w = compute_weight_bounds(image, a)

    for i in range(w):

        for j in range(h):
            # indici dei nodi = coordinate come su numpy
            G.add_node((i, j), intensity=image[i, j])
            if i > 0:
                G.add_edge((i, j), (i-1, j), 
                weight1=sim1(image[i, j], image[i-1, j],h,w,a, medical, min_w, max_w),
                weight2=sim2(image[i, j], image[i-1, j],h,w,a, medical, min_w, max_w)
                )
            if j > 0:
                G.add_edge((i, j), (i, j-1),
                weight1=sim1(image[i, j], image[i, j-1],h,w, a, medical, min_w, max_w), 
                weight2=sim2(image[i, j], image[i, j-1],h,w, a, medical, min_w, max_w)
                )
    return G


# ------------------------------------------------------------------------------

def Plot_graph(G,stop = False, values = None, scattercolor = "grey", fig = None, ax = None):
    # adattato dal Plot_tour fatto a lezione
    # G = grafo
    # values = vettore dei pesi associati ai edges, consigliati tra 0 e 1
    
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
    for ((i, j), (k, l)), val in zip(G.edges(), values):
        x_mid = (j + l) / 2
        y_mid = (i + k) / 2
        ax.text(x_mid+ 0.00001,  y_mid, f"{val:.2f}", fontsize=6, color='black', alpha=0.5, ha='center', va='center')

   
    ax.scatter([j for i,j in Ps], [i for i,j in Ps], 
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
    A = [edge for edge in G.edges() if edge[0] in S and edge[1] in S_bar ]
    A.extend([edge for edge in G.edges() if edge[0] in S_bar and edge[1] in S ])
    return A

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

    image = np.repeat(np.array([G.nodes()[n]['intensity'] for n in G.nodes()])
                                .reshape(w,h,1), 3, axis=-1)
    from matplotlib.colors import ListedColormap
    cmap =  ListedColormap(["red", "blue"])
    # print(cmap)
    for idx, V in enumerate(sets):
        # print(V.nodes())
        # color = np.array(cmap(idx % cmap.N)[:])
        for node in V.nodes():
            image[node[0], node[1], :] = 0.5 * image[node[0], node[1], :] + 0.5*np.array([cmap(idx % cmap.N)[:3]])
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
        # plt.show()
        plt.close()

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
    print("##########   MODEL CREATED")

    # ora dato il grafo dobbiamo scrivere il problema di min cut
    
    x = {}      # x[node] = 1 se node è nel source set
    for index, node in enumerate(G.nodes()): 
        x[node] = model.addVar(lb=0, ub=1,  vtype=GRB.INTEGER, name=f"x_{node}") 

    y = {}      # y[edge] = 1 se edge è nel source set
    k = {}
    for index, edge in enumerate(G.edges()): 
        # print(edge)
        y[edge] = model.addVar(lb=0, ub=1, obj = - lambda_*G.edges[edge]['weight2'],  vtype=GRB.INTEGER, name=f"y_{edge}")
        k[edge] = model.addVar(lb = 0, ub=1, vtype=GRB.INTEGER, name=f"k_{edge}")


    z = {}      # z[edge] = 1 se edge è nel cut
    for index, edge in enumerate(G.edges()): 
        z[edge] = model.addVar(lb=0, ub=1, obj = G.edges[edge]['weight1'], vtype=GRB.INTEGER, name=f"z_{edge}")
        # z[(edge[1], edge[0])] = z[edge]  # perchè il grafo è undirected
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
        model.addConstr(z[edge] >= x[edge[1]] - x[edge[0]])
        ###  model.addConstr(z[(edge[1], edge[0])] >= x[edge[1]] - x[edge[0]])
        model.addConstr(k[edge] >= x[edge[0]] + x[edge[1]] - 1)
        model.addConstr(1-z[edge] >= y[edge])
        ### model.addConstr(1-y[edge] >= z[edge])
        model.addConstr(y[edge] >= k[edge])
        model.addConstr(k[edge] <= x[edge[0]])
        model.addConstr(k[edge] <= x[edge[1]])
    print("######## ADDED CONSTRAINTS, OPTIMIZING....")
    model.modelSense = grb.GRB.MINIMIZE
    model.update()
    
    # model.write("mincut_lambda___.lp") 

    model.optimize()
    if model.status == GRB.OPTIMAL:
        print("##########   MODEL OPTIMAL")
        print('Optimal objective: %g' % model.objVal)
        sol_x = model.getAttr('x', x)
        sol_y = model.getAttr('x', y)
        sol_z = model.getAttr('x', z)
        # print("solution x:", sol_x)
        # print("solution y:", [(y, sol_y[y]) for y in sol_y if sol_y[y] < 0.5])
        # print("solution z:", [(z, sol_z[z]) for z in sol_z if sol_z[z]> 0.5])
    
        source_set = [node for node in G.nodes() if sol_x[node] == 1.0]
        sink_set = [node for node in G.nodes() if sol_x[node] == 0.0 ]
        # print(sol_x.values(), sol_y.values(), sol_z.values())
        
        print("unique elements of x:", set([x for x in sol_x.values()]))
        print("Zeros x: ", len([x for x in sol_x.values() if x == 0.0]))
        print("Ones x: ", len([x for x in sol_x.values() if x == 1]))
        print("Len x: ", len(sol_x.values()))

        print("unique elements of y:", set([y for y in sol_y.values()]))
        print("Zeros y: ", len([y for y in sol_y.values() if y == 0.0]))
        print("Ones y: ", len([y for y in sol_y.values() if y == 1]))
        print("Len y: ", len(sol_y.values()))

        
        print("unique elements of z:", set([z for z in sol_z.values()]))
        print("Zeros z: ", len([z for z in sol_z.values() if z == 0.0]))
        print("Ones z: ", len([z for z in sol_z.values() if z == 1]))
        print("Len z: ", len( sol_z.values()))
        cut = capacity1([G.subgraph(source_set), G.subgraph(sink_set)], G)
        print("Actual cut value: ", cut, "------------------------")
        return source_set, sink_set, model.objVal, sol_x, sol_y, sol_z 
    else:
        print("No optimal solution found, model.status =", model.status)
        return None, None, None

# --------------------------------------------------------

def parametric_min_cut(image, source_pixels, sink_pixels, time_limit = 300, max_iter = 100, max_stall = 20):
    from time import time
    start_time = time()
    # print("building graph")
    G = costruisci_grafo_base(image)
    # print("graph built")
    # source_pixels devono essere una lista [(x1,y1), (x2,y2)] e sink_pixels [(x3,y3), (x4,y4)] 
    source = (source_pixels[0], source_pixels[1]) # come edge del grafo
    sink = (sink_pixels[0], sink_pixels[1]) # come edge del grafo

    iter_ = 0
    stall = 0
    # t = np.median([G.edges[e]['weight1'] for e in G.edges()]) / (np.median([G.edges[e]['weight2'] for e in G.edges()]) + 1e-5)

    source_0 = [n for n in G.nodes() if G.nodes[n]["intensity"]>0.5]
    sink_0 = [n for n in G.nodes() if G.nodes[n]["intensity"]<=0.5]

    # print("calculating t")
    # s1 = sum([G.edges[e]['weight1'] for e in G.edges() if e[0] in source_0 and e[1] in sink_0])
    # s2 = sum([ G.edges[e]["weight1"] for e in G.edges() if e[1] in source_0 and e[0] in sink_0 ])
    # s3 = sum([G.edges[e]['weight2'] for e in G.edges() if e[0] in source_0 and e[1] in source_0])
        
    # t0 = (s1+s2)/s3
    # print("calculated t")
    t = 1
    t_his = t
    source_set, sink_set, cut, sol_x, sol_y, sol_z = MinCut(image, source_pixels, sink_pixels, t) 
    source_his = source_set
    sink_his = sink_set
    cut_his = cut
    x_his = sol_x
    y_his = sol_y
    z_his = sol_z
    while abs(cut) >=  0.1e-8:


        t = sum([G.edges[e]['weight1'] for e in G.edges() if sol_z[e] > 0.5]) / sum([G.edges[e]['weight2'] for e in G.edges() if sol_y[e] > 0.5])
        print("t = ", t, "------- nonzeros x = ", len([x for x in sol_x if sol_x[x]>0.5]) ,  "-----------------------------------------")
        print("t = ", t, "------- nonzeros z = ", len([z for z in sol_z if sol_z[z]>0.5]) ,  "-----------------------------------------")
        print("t = ", t, "------- numeratore = ",sum([G.edges[e]['weight1'] for e in G.edges() if sol_z[e] > 0.5])  ,  "-----------------------------------------")
        print("t = ", t, "------- denominatore = ",sum([G.edges[e]['weight2'] for e in G.edges() if sol_y[e] > 0.5]) ,  "-----------------------------------------")
        
        if t == 0:
            print("t = 0, you're not solving normalized cut anymore")
            flag = "found value t = 0"
            break
        
        if abs(t - t_his) <= 1e-8:
            stall += 1
            print("warning, same value of t")
            source_set, sink_set, cut, sol_x, sol_y, sol_z = MinCut(image, source_pixels, sink_pixels, t) 
            iter_ += 1
        
            if source_his == source_set and sink_his == sink_set and x_his == sol_x and y_his == sol_y and z_his == sol_z:
                flag = "looping"
                break

        if stall >= max_stall:
            print("Stall limit reached.")
            flag = "stall limit"
            break
        source_set, sink_set, cut, sol_x, sol_y, sol_z = MinCut(image, source_pixels, sink_pixels, t) 
        iter_ += 1
        flag = ""
        # Plot_image_cuts([G.subgraph(source_set), G.subgraph(sink_set)], G, source_pixels, sink_pixels)


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


    flag ="ALL WELL"
    print("ALL WELL")
    return source_set, sink_set, cut, sol_x, sol_y, sol_z, t, flag

def from_pixel_to_np(pixel, image_shape):
    w,h = image_shape
    return (pixel[0], h-1-pixel[1])


if __name__ == "__main__":
    """
    # image = plt.imread('C:/Users/elena/Documents/GitHub/operations_research/project_2025/images/cane.jpg')

    # plt.imshow(image)
    # plt.axis('off')
    # plt.show()

    # image_bn = np.mean(image, axis=2)

    # plt.imshow(image_bn, cmap='gray')
    # plt.axis('off')
    # plt.show()

    # # print(image_bn)
    # G = costruisci_grafo_base(image_bn)
    # print(G.edges(data=True))
    # Plot_graph(G, values = [k[2]['weight1'] for k in G.edges(data=True)])   # giustamente in una immagine ad alta risoluzione non si vede il reticolo

    # print("prova del 9 con la capacità")
    # print("capacità di G con taglio G = ",  capacity1([G], G)) 

    # print("tentativo di dividere")

    # print("nodi totali ", len(G.nodes))
    
    # sets = []
    # for i in range(11):
    #     sub_nodes = list(G.nodes)[i*6750: 6750*(i+1)]  # primi 100 nodi
    #     V= G.subgraph(sub_nodes)
    #     sets.append(V)

    # print("cut cost:", capacity1(sets, G))

    # print("plotting cuts")
    # Plot_graph_cuts(sets, G)

    # Plot_image_cuts(sets, G)
    # print(Laplacian(G))


    # sink_pixels = [(5,5), (5,6)]
    # source_pixels = [(160, 115), (160, 116)] # per cane
    # source_pixels = [(55,50), (55, 51)] # per cane piccolo
    # source_pixels = [(30,20),(31,20)] # per cane piccolissimo
    # source_pixels = [(95, 70), (95, 71)] # per luna
    # source_pixels = [(25, 25), (25, 26)] # per blob nero


    # lambda_  = 1
    # source_set, sink_set, cut_value, sol_x, sol_y, sol_z = MinCut(image_bn, source_pixels, sink_pixels, lambda_)

    # source_set, sink_set, cut, sol_x, sol_y, sol_z, t, flag = parametric_min_cut(image_bn, source_pixels, sink_pixels, time_limit=300, max_iter=50)

    # print("Best lambda:", t)
    # print("Best cut value:", cut)

    # if source_set != None and sink_set != None:
    #     print("Source set size:", len(source_set))
    #     print("Sink set size:", len(sink_set))
    #     Plot_image_cuts([G.subgraph(source_set), G.subgraph(sink_set)], G, source_pixels, sink_pixels)
    """

    images = {}
    # images["nerojpg.jpg"] = [(20,30), (20,31)]
    # images["cane_piccolissimo.jpg"] =  [(30,20),(31,20)]
    # images["gatto_piccolissimo.jpg"] =  [(30,15),(31,15)]
    # images["cane_piccolo.jpg"] = [(55,50), (55, 51)]
    
    images["brain.png"] = [(222,170), (222,171)]
    images["brain2.png"] = [(180,170), (180,171)]
    images["cane.jpg"] = [(160, 115), (160, 116)]
    images["luna.jpg"] = [(95, 70), (95, 71)]
    images["gatto.jpg"] = [(150, 113), (150, 114)]
    images["fiori_rossi.jpg"] = [(170, 118), (170, 119)]
    images["fiori_rosa.jpg"]= [(100, 70), (100, 71)]
    images["fiori_bianchi.jpg"] = [(190, 120), (190, 121)]
    images["fiore_giallo.jpg"] = [(80,80), (80,81)]
    
    import json 

    for image_name in images:  
        print("######################"+image_name + "#####################") 
        image = plt.imread('C:/Users/elena/Documents/GitHub/operations_research/project_2025/images/'+ image_name)
        
        if image_name == "brain.png":
            medical = True
            image_bn = image
            image_bn = enhance_contrast(image_bn)
            sink_pixels = [(333,115), (333,116)]

        elif image_name == "brain2.png":
            medical = True
            image_bn = image
            
            image_bn = enhance_contrast(image_bn)
            sink_pixels = [(200,90), (200,91)]
        
        else:
            medical = False
            image_bn = np.mean(image, axis=2)
            
            image_bn = enhance_contrast(image_bn)
            sink_pixels = [(5,5), (5,6)]

        # if image_name == "nerojpg.jpg":

        #     image_bn = add_noise(image_bn, 5)

        source_pixels = images[image_name]
        
        # print("hello??????")

        source_set, sink_set, cut, sol_x, sol_y, sol_z, t, flag = parametric_min_cut(image_bn, source_pixels, sink_pixels, time_limit=1200, max_iter=50, max_stall = 10)
        # print(source_set)


        G = costruisci_grafo_base(image_bn, medical)
        
        print("Source set size:", len(source_set))
        print("Sink set size:", len(sink_set))
        
        Plot_image_cuts([G.subgraph(source_set), G.subgraph(sink_set)], G, source_pixels, sink_pixels, image_name)
        # Plot_graph(G, values = [k[2]['weight1'] for k in G.edges(data=True)])   # giustamente in una immagine ad alta risoluzione non si vede il reticolo
        # Plot_graph(G, values = [k[2]['weight2'] for k in G.edges(data=True)])   # giustamente in una immagine ad alta risoluzione non si vede il reticolo

        import json
        with open("C:/Users/elena/Documents/GitHub/operations_research/project_2025/"+ image_name[:-4] + "_x.json", "w") as file: 
            json.dump(str(sol_x), file)
        with open("C:/Users/elena/Documents/GitHub/operations_research/project_2025/"+ image_name[:-4] + "_y.json", "w") as file: 
            json.dump(str(sol_y), file)
        with open("C:/Users/elena/Documents/GitHub/operations_research/project_2025/"+ image_name[:-4] + "_z.json", "w") as file: 
            json.dump(str(sol_z), file)
        with open("C:/Users/elena/Documents/GitHub/operations_research/project_2025/"+ image_name[:-4] + "_info.txt", "w") as file:
            file.write("Source set size:" + str(len(source_set))+ "\n")
            file.write("Sink set size:"+ str(len(sink_set))+"\n")
            file.write("best lambda:" + str(t) +"\n")
            file.write("best cut value:" + str(cut) + "\n")
            file.write("sigma: " + str(np.std(image_bn/255) + 0.001) + "\n")
            
            file.write(flag)
            # --------------------------------------------------------