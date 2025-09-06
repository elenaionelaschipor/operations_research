# created by Elena --- COPY

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import collections as mc   
import gurobipy as grb


# -----------------------------------------------------------------

def sim1(pixel1, pixel2):  # misura di somiglianza esponenziale
    # pixel1 and pixel2 are both grayscale pixel values
    sigma = 10
    return np.exp(-abs(pixel1 - pixel2)/sigma)

def sim2(pixel1, pixel2):
    return 1/(1 + (abs(pixel1 - pixel2))**2)
# -----------------------------------------------------------------
def flip_y(i, j, h, w):
    return i, h-1-j
def costruisci_grafo_base(image):
    G = nx.Graph()
    w, h = image.shape
    for i in range(w):
        for j in range(h):
            # i,j are the coordinates of the pixel with origin at the top left corner
            # G.add_node((i, j), intensity=image[i, j])   
            G.add_node((i, j), intensity=image[flip_y(i, j, h, w)])  
            if i > 0:
                G.add_edge((i, j), (i-1, j), 
                    weight1=sim1(image[flip_y(i, j, h, w)], image[flip_y(i-1, j, h, w)]),
                    weight2=sim2(image[flip_y(i, j, h, w)], image[flip_y(i-1, j, h, w)])
                )
            if j > 0:
                G.add_edge((i, j), (i, j-1),
                    weight1=sim1(image[flip_y(i, j, h, w)], image[flip_y(i, j-1, h, w)]), 
                    weight2=sim2(image[flip_y(i, j, h, w)], image[flip_y(i, j-1, h, w)])
                )
    return G


# ------------------------------------------------------------------------------
import matplotlib.pyplot as plt
import matplotlib.collections as mc
import networkx as nx

def Plot_graph(G, image_shape=None, stop=False, values=None, scattercolor="grey", fig=None, ax=None):
    Ps = list(G.nodes())
    Ls = list(G.edges())

    if image_shape is None:
        h = max(i for i, j in Ps) + 1
        w = max(j for i, j in Ps) + 1
    else:
        h, w = image_shape

    Ps_plot = [(i, j) for i, j in Ps]
    lines = [[(i, j), (k, l)] for (i, j), (k, l) in Ls]

    if fig is None and ax is None:
        fig, ax = plt.subplots(figsize=(w / 50, h / 50))

    if values is None:
        values = [1 for _ in range(len(Ls))]
        norm = plt.Normalize(1, 1)
    else:
        norm = plt.Normalize(min(values), max(values))

    from matplotlib.colors import LinearSegmentedColormap
    rainbow_to_white = LinearSegmentedColormap.from_list(
        'rainbow_to_white',
        ['black', 'purple', 'red', 'orange', 'yellow', 'green', 'blue', 'cyan', 'white']
    )

    lc = mc.LineCollection(lines, colors=[rainbow_to_white(norm(x)) for x in values])
    ax.add_collection(lc)

    # for ((i, j), (k, l)), val in zip(Ls, values):
    #     x1, y1 = flip_y(i, j, h, w)
    #     x2, y2 = flip_y(k, l, h, w)
    #     x_mid = (x1 + x2) / 2
    #     y_mid = (y1 + y2) / 2
    #     ax.text(x_mid, y_mid, f"{val:.2f}", fontsize=6, color='black', alpha=0.5, ha='center', va='center')

    ax.scatter([x for x, y in Ps_plot], [y for x, y in Ps_plot],
               s=20, alpha=0.8, color=scattercolor)

    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.set_aspect('equal')
    ax.margins(0.1)

    if not stop:
        plt.show()
        return fig, ax
    return fig, ax

#-----------------------------------------------------------------------------------
def get_cutted_edges(S, S_bar, G): # qua voglio S e S_bar come grafi  
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
    # print(G.nodes())
    h = max([a[1] for a in G.nodes()]) + 1
    w = max([a[0] for a in G.nodes()]) + 1

    im = np.zeros((w, h ,1))
    for n in G.nodes():
        # print(flip_y(n[0], n[1], h, w)[0], flip_y(n[0], n[1], h, w)[1], 0)
        # print(G.nodes[n]['intensity'])
        im[flip_y(n[0], n[1], h, w)[0], flip_y(n[0], n[1], h, w)[1], 0] = G.nodes[n]['intensity']/255
    # plt.imshow(im, cmap='gray', vmin=0, vmax=1)
    # plt.show()
    image = np.repeat( im, 3, axis = -1) # np.array([G.nodes()[n]['intensity']/255 for n in G.nodes()])
                        #        .reshape(w,h,1), 3, axis=-1)
    from matplotlib.colors import ListedColormap

    import matplotlib.cm as cm
    import matplotlib.colors as mcolors
    from matplotlib import colormaps

    def get_distinct_colors(n):
        # base = colormaps.get_cmap('Set1', n)
        base = cm.get_cmap('prism', n)  # oppure 'gist_rainbow', 'Set3', ecc.
        return [base(i)[:3] for i in range(n)]
    colors = get_distinct_colors(len(sets))

    # cmap =  ListedColormap(["red", "green", "orange", "blue"])
    # print(cmap)

    for idx, V in enumerate(sets):
        color = colors[idx]
        for node in G.subgraph(V).nodes():
            n = flip_y(node[0], node[1], h, w)   # da pixel a np
            image[n[0], n[1], :] = 0.9 * image[n[0], n[1], :] + 0.1 * np.array(color)
    plt.imshow(image)  # verrà plottata come i pixel


    if source_pixels != None and len(source_pixels) == 2:
        for sp in source_pixels:
            # mantengo notazione dei pixel
            plt.scatter(sp[0], sp[1], color='black', s=100, marker='*', label='Source Pixel' if sp == source_pixels[0] else "")
        plt.legend(loc='upper right')
    if source_pixels != None and len(source_pixels) > 2:
        for sp in source_pixels:
            for pix in sp:
                plt.scatter(pix[0], pix[1], color='black', s=100, marker='*', label='Source Pixel' if pix == source_pixels[0][0] else "")
        plt.legend(loc='upper right')
    if sink_pixels != None:
        for tp in sink_pixels:
            plt.scatter(tp[0], tp[1], color='black', s=100, marker='4', label='Sink Pixel' if tp == sink_pixels[0] else "")
        plt.legend(loc='upper right')
    plt.axis('off')
    if image_name == None:
        plt.show()
    else:
        plt.savefig(image_name[:-4] + "_segmented.png")
        plt.show()

# ---------------------------------------------------------------------------------------------------

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

def MinCut(image, source_pixels, sink_pixels, lambda_, G=None):
    if G == None:
        G = costruisci_grafo_base(image)
    # source_pixels devono essere una lista [(x1,y1), (x2,y2)] e sink_pixels [(x3,y3), (x4,y4)]
    # HANNO LA FORMA DELLE COORD DEI PIXEL
    if (source_pixels[1], source_pixels[0]) in G.edges():
        source = (source_pixels[1], source_pixels[0]) # come edge del grafo
    if (source_pixels[0], source_pixels[1]) in G.edges():
        source = (source_pixels[0], source_pixels[1])
    if (sink_pixels[1], sink_pixels[0]) in G.edges():
        sink = (sink_pixels[1], sink_pixels[0])
    if (sink_pixels[0], sink_pixels[1]) in G.edges():
        sink = (sink_pixels[0], sink_pixels[1])
    
    # print(source, sink)
    # G_st = costruisci_grafo_st(G, lambda_, source, sink) # ora ho il grafo con s e t come nodi
    
    
    from gurobipy import Model, GRB, quicksum
    model = Model()
    model.setParam("OutputFlag", 0)
    # print("##########   MODEL CREATED")

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
        z[(edge[1], edge[0])] = z[edge]  # perchè il grafo è undirected
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
        model.addConstr(z[(edge[1], edge[0])] >= x[edge[1]] - x[edge[0]])
        model.addConstr(y[edge] >= x[edge[0]] + x[edge[1]] - 1)
        model.addConstr(1+z[edge] >= y[edge])
        model.addConstr(1+y[edge] >= z[edge])

    print("OPTIMIZING....")
    model.modelSense = grb.GRB.MINIMIZE
    model.update()
    
    model.write("mincut_lambda.lp") 

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

def parametric_min_cut(image,source_pixels, sink_pixels, time_limit = 300, max_iter = 100, max_stall = 20, G = None):
    from time import time
    start_time = time()
    if G == None:
        G = costruisci_grafo_base(image)
    # source_pixels devono essere una lista [(x1,y1), (x2,y2)] e sink_pixels [(x3,y3), (x4,y4)] 
    if (source_pixels[1], source_pixels[0]) in G.edges():
        source = (source_pixels[1], source_pixels[0]) # come edge del grafo
    if (source_pixels[0], source_pixels[1]) in G.edges():
        source = (source_pixels[0], source_pixels[1])
    if (sink_pixels[1], sink_pixels[0]) in G.edges():
        sink = (sink_pixels[1], sink_pixels[0])
    if (sink_pixels[0], sink_pixels[1]) in G.edges():
        sink = (sink_pixels[0], sink_pixels[1])

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
        print("t = ", t, "------------------------")
        source_set, sink_set, cut, sol_x, sol_y, sol_z = MinCut(image, source_pixels, sink_pixels, t, G) 
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

def k_partition(image, k, source_pixels, time_limit = 300, max_iter = 100, max_stall = 20, G = None, plotting = False):
    import math
    print("Computing k-partition for k =", k, "----------------------------------------------***")
    if k == 0 or source_pixels == []:
        return []
    if G == None:
        G = costruisci_grafo_base(image)
    if k == 1:
        return [G.nodes()]
    if k == 2:
        source_set, sink_set, cut, sol_x, sol_y, sol_z, t, flag = parametric_min_cut(image, source_pixels[0], source_pixels[1], time_limit, max_iter, max_stall)
        return [source_set, sink_set]
    if k > 0 and (k & (k - 1)) == 0: # se k è una potenza di 2
        n = int(math.log2(k))
        s = source_pixels[0]
        t = source_pixels[1]
        print("source pixels:", source_pixels)

        print("k is a power of 2, log2(k) =", n)
        print("Computing 2-partition for source pixel", s, "and sink pixel", t)
        S, T, c, x, y, z, lambda_, flag = parametric_min_cut(image, s,t)

        if plotting:
            Plot_image_cuts([G.subgraph(S), G.subgraph(T)], G, source_pixels = source_pixels)
        
        print("checking which sources are in which set")
        print("Set S has", len(S), "nodes, Set T has", len(T), "nodes")

        # print(T)
        for pixel in source_pixels:
            
            if pixel[0] in S and pixel[1] in S:
                print("this edge is in S:")
                print(pixel)
            elif pixel[0] in T and pixel[1] in T:
                print("this edge is in T:")
                print(pixel)
            else:
                print("warning, this edge is cutted:", pixel)

        source_s = [pixel for pixel in source_pixels if pixel[0] in S and pixel[1] in S]
        source_t = [pixel for pixel in source_pixels if pixel[0] in T and pixel[1] in T]


        print("Partition found with cut value:", c)
        print("Source pixels in S:", source_s)
        print("Source pixels in T:", source_t)
        print("Now computing recursively the partitions of S and T")
        if len(source_s) == 1:
            partition_S = [S]
        else:
            print("--------Computing", len(source_s), "-partition for source pixels", source_s)
            partition_S =  k_partition(image, len(source_s), source_s, time_limit, max_iter, max_stall, G.subgraph(S))
            print("len partition S:", len(partition_S))

        print("--------------------------------------------------- ARE YOU STILL THERE? ---------------------------------------------------")    
        if len(source_t) == 1:
            partition_T = [T]
        else:
            print("--------Computing", len(source_t), "-partition for source pixels", source_t)
            partition_T =  k_partition(image, len(source_t), source_t, time_limit, max_iter, max_stall, G.subgraph(T))
        
        return partition_S + partition_T
    else:
        print("HELLO!!!!!!! NOT EXPECTING ME")
        lower_power = 2 ** int(math.log2(k))
        extra = k - lower_power
        base_pixels = source_pixels[:lower_power]
        extra_pixels = source_pixels[lower_power:]

        base_partitions = k_partition(image, lower_power, base_pixels, time_limit, max_iter, max_stall, G)

        for i in range(extra):            
            good_sets = [sets for sets in base_partitions if len([pixel for pixel in extra_pixels if pixel in sets])>=2]
            if good_sets == []:
                break
            good_sets = sorted(good_sets, key = len, reverse = True)
            largest_set = good_sets[0]
            l_pixels = [pixel for pixel in extra_pixels if pixel in largest_set]
            part_largest = k_partition(image, 2, [l_pixels[0], l_pixels[1]], time_limit, max_iter, max_stall, G.subgraph(largest_set))
            base_partitions.remove(largest_set)
            base_partitions.extend(part_largest)
        

        return base_partitions









if __name__ == "__main__":
    
    # image = plt.imread('C:/Users/elena/Documents/GitHub/operations_research/project_2025/images/cane_piccolissimo.jpg')

    # h, w = image.shape[0], image.shape[1]
    # source_pixels = [[(5,5),(5,6)], [(30, 30), (30,31)], [(15,30), (16,30)], [(45,30), (45,31)]]
    # # source_pixels = [[(5,5),(5,6)], [(30, 30), (30,31)], [(15,30), (16,30)], [(45,10), (45,11)]]
    
    
    # # plt.imshow(image)
    # # plt.axis('off')
    # # plt.show()

    # image_bn = np.mean(image, axis=2)
    # plt.imshow(image_bn,cmap='gray')
    # plt.show()
    # sets = k_partition(image_bn, 4, source_pixels, time_limit=600, max_iter=50, max_stall = 10, plotting=True)
    # print(len(sets), "partitions found")
    # G = costruisci_grafo_base(image_bn)
    # Plot_image_cuts(sets, G, source_pixels)



    # image = plt.imread('C:/Users/elena/Documents/GitHub/operations_research/project_2025/images/nerojpg.jpg')
    # image_bn = np.mean(image, axis=2)
    # G = costruisci_grafo_base(image_bn)
    # Plot_graph(G, values = [k[2]['weight1'] for k in G.edges(data=True)])   # giustamente in una immagine ad alta risoluzione non si vede il reticolo
    
    # print(G.nodes())       

    """
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
    images["cane_piccolissimo.jpg"] =  [(30,20),(31,20)]
    images["cane_piccolo.jpg"] = [(55,50), (55, 51)]
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
        image_bn = np.mean(image, axis=2)
        sink_pixels = [(5,5), (5,6)]
        source_pixels = images[image_name]
        

        source_set, sink_set, cut, sol_x, sol_y, sol_z, t, flag = parametric_min_cut(image_bn, source_pixels, sink_pixels, time_limit=600, max_iter=50, max_stall = 10)


        G = costruisci_grafo_base(image_bn)
        
        print("Source set size:", len(source_set))
        print("Sink set size:", len(sink_set))
        
        Plot_image_cuts([G.subgraph(source_set), G.subgraph(sink_set)], G, source_pixels, sink_pixels, image_name)
        

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
            file.write(flag)
            # --------------------------------------------------------