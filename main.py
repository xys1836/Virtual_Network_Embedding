from Graph_Generator import generate_graph
import networkx as nx
import matplotlib.pyplot as plt
G = generate_graph(100, 100, 0.2, 0, 'sb')
#nx.draw(G)
#nx.draw_random(G)
#nx.draw_circular(G)
nx.draw_spectral(G)
plt.show()
