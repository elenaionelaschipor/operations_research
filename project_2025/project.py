# created by Elena
# 30/08/25



import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import collections as mc   



# -----------------------------------------------------------------

def sim(pixel1, pixel2):  # misura di somiglianza
    # pixel1 and pixel2 are both grayscale pixel values
    return abs(pixel1 - pixel2)/255
# -----------------------------------------------------------------
def costruisci_grafo(image):
    G = nx.Graph()
    h, w = image.shape
    for i in range(h):
        for j in range(w):
            G.add_node((i, j), intensity=image[i, j])
            if i > 0:
                G.add_edge((i, j), (i-1, j), weight=sim(image[i, j], image[i-1, j]))
            if j > 0:
                G.add_edge((i, j), (i, j-1), weight=sim(image[i, j], image[i, j-1]))
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


    # ...existing code...
    # Normalizza i valori tra 0 e 1
    if values == None:
        values = [1 for _ in range(len(G.nodes()))]  
        norm = plt.Normalize(1, 1)

    else: 
        norm = plt.Normalize(min(values), max(values))
    from matplotlib.colors import LinearSegmentedColormap
    white_to_rainbow = LinearSegmentedColormap.from_list('white_to_rainbow', ['white', "cyan", "blue", "green", "yellow", "orange", "red", "purple", 'black'])
    cmap = white_to_rainbow
        
    lc = mc.LineCollection(
        lines,
        colors=[cmap(norm(x)) for x in values]
    )
    # ...existing code...
    # lc = mc.LineCollection(lines,
    #                        colors = ['white' if x < 0.1 else "blue" if x<0.2 else "red" if x <0.3 else 'orange' if x<0.4 else "pink" if x<0.5 else "purple" if x <0.7 else "darkgreen" if x <0.8 else "green" if x <0.9 else "black" for x in values])


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
def capacity(sets, G, cutted_edges = None):
    if len(sets) == 1:
        S = sets[0]
        # S_bar = nx.difference(G, S)
        S_bar = G.copy()
        S_bar.remove_nodes_from(n for n in G if n in S)
        print(S_bar)
        if cutted_edges == None:
            cutted_edges = get_cutted_edges(S, S_bar, G)
            print(cutted_edges)
        return sum([G[u][v]['weight'] for u, v in cutted_edges])
        
    else:
        if nx.union_all(sets).nodes() == G.nodes():
            tot = 0
            for k in range(len(sets)):
                V_k = sets[k]
                V_k_bar = G.copy()
                V_k_bar.remove_nodes_from(n for n in G if n in V_k)
                if cutted_edges == None:
                    cutted_edges = get_cutted_edges(V_k, V_k_bar, G)
                tot += 0.5 * sum([G[u][v]['weight'] for u, v in cutted_edges])
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

#--------------------------------------------------------------------------------

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


if __name__ == "__main__":
    cane = plt.imread('C:/Users/elena/Documents/GitHub/operations_research/project_2025/images/cane.jpg')

    plt.imshow(cane)
    plt.axis('off')
    plt.show()

    cane_bn = np.mean(cane, axis=2)

    plt.imshow(cane_bn, cmap='gray')
    plt.axis('off')
    plt.show()

    # print(cane_bn)
    G = costruisci_grafo(cane_bn)
    # print(G.edges(data=True))
    Plot_graph(G, values = [k[2]['weight'] for k in G.edges(data=True)])   # giustamente in una immagine ad alta risoluzione non si vede il reticolo

    print("prova del 9 con la capacità")
    print("capacità di G con taglio G = ",  capacity([G], G)) 

    print("tentativo di dividere")

    print("nodi totali ", len(G.nodes))
    
    sets = []
    for i in range(11):
        sub_nodes = list(G.nodes)[i*6750: 6750*(i+1)]  # primi 100 nodi
        V= G.subgraph(sub_nodes)
        sets.append(V)

    print("cut cost:", capacity(sets, G))

    print("plotting cuts")
    Plot_graph_cuts(sets, G)

    Plot_image_cuts(sets, G)