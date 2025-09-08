# created by Elena


from normalized_cut import * 

medical = False
# medical = True
# image_path = "C:/UsFrs/elena/Documents/GitHub/operations_research/project_2025/images/PKG_Brain_Mets_Lung_MRI_Path_Segs_radiology_images/output/YG_8C4Q7MZ67UAA/YG_LSMF1KDV6GFL_flair_img/channel_20.png"
image_path = 'C:/Users/elena/Documents/GitHub/operations_research/project_2025/images/nerojpg.jpg'

image = plt.imread(image_path)
print(np.max(image))
image = np.mean(image, axis=2)

# sink_pixels = [(300, 225), (300,226)]
# source_pixels = [(238, 163), (238, 164)] 
 
sink_pixels = [(5,5),(5,6)]
source_pixels = [(20, 30),(20,31)]

source_set, sink_set, cut, sol_x, sol_y, sol_z, t, flag = parametric_min_cut(image, source_pixels, sink_pixels, time_limit = 300, max_iter = 100, max_stall = 20)

G = costruisci_grafo_base(image, medical)
print("Source set size:", len(source_set))
print("Sink set size:", len(sink_set))
Plot_image_cuts([G.subgraph(source_set), G.subgraph(sink_set)], G, source_pixels, sink_pixels)
Plot_graph(G, values = [k[2]['weight1'] for k in G.edges(data=True)])   # giustamente in una immagine ad alta risoluzione non si vede il reticolo
