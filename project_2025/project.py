# created by Elena
# 30/08/25



import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# -----------------------------------------------------------------

cane = plt.imread('C:/Users/elena/Documents/GitHub/operations_research/project_2025/images/cane_piccolo.jpg')
plt.imshow(cane)
plt.axis('off')
plt.show()

cane_bn = np.mean(cane, axis=2)

plt.imshow(cane_bn, cmap='gray')
plt.axis('off')
plt.show()

print(cane_bn)

def sim(pixel1, pixel2):
    # pixel1 and pixel2 are both grayscale pixel values
    return abs(pixel1 - pixel2)

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


G = costruisci_grafo(cane_bn)

# ...existing code...
sub_nodes = list(G.nodes)[:100]  # primi 100 nodi
subG = G.subgraph(sub_nodes)
nx.draw(subG, with_labels=True)
plt.show()
# ...existing code...


print(G)
# nx.draw(G, with_labels=True)