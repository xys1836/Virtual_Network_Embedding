from Graph_Generator import generate_graph
import networkx as nx
import matplotlib.pyplot as plt
G = generate_graph(10, 100, 0.5, 0, 'sb')
#nx.draw(G)
nx.draw_random(G)
#nx.draw_circular(G)
#nx.draw_spectral(G)
#plt.show()
#plt.savefig('node_10.png')
def generate_substrate_network(n, g, p, s, nm):
  """Generate a substrate network
    
    Input: 
      n: number of nodes in substrate network
      g: grid
      p: probability of two edges connected
      s: seed for random generating
      nm: name of the substarte network

    Ouput:
      A graph 
  """
  pass

def generate_virtual_network(n, p, s, nm):
  """Generate a virtual network

    Input:
      n: number of nodes in virtual network
      p: probablity of two edges connected 
      s: seed for random generating
      nm: name of the virtual network
  """
  pass


