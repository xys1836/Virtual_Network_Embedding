import os
import subprocess
import random
import networkx as nx

def create_script_file(n,g,p,s,name = None):
  """Create Script for itm

    Input:
      n: number of nodes
      g: grid scale
      p: probility of two edge connected
      s: seed for rand
      name: name for the graph
    Output:
      the file path of the graph
  """
  file_path = ''
  l1 = 'geo' + ' ' + '1' + ' ' + str(s)
  l2 = str(n) + ' ' + str(g) + ' ' + '3' + ' ' + str(p)
  if name:
    file_path = './graph_set/' + name 
  else:
    file_path = './graph_set/' + 'no_name_graph'
  with open(file_path, 'wb') as f:
    f.write(l1 + '\n')
    f.write(l2 + '\n')
  return file_path

def execute_itm(file_path):
  subprocess.call(['itm', file_path])
  subprocess.call(['sgb2alt', file_path + '-0.gb', file_path + '.alt'])
  return 0

def generate_basic_graph(n, g, p, s, name = None):
  G = nx.Graph()
  for i in range(0, n):
    G.add_node(i)
  isEdge = False
  file_path = create_script_file(n,g,p,s,name)
  execute_itm(file_path)
  with open(file_path + '.alt', 'r') as f:
    for line in f:
      if isEdge:
        edge = line.split(' ') 
        a = int(edge[0])
        b = int(edge[1])
        G.add_edge(a,b)
        continue

      if line[0:5] == 'EDGES':# (from-node to-node length a b):':
        isEdge = True

  return G
 
def generate_uniform_distribution(a, b):
  return random.randint(a,b)  

def generate_substrate_network(n, g, p, s, nm, cpu_c, bw_c):
  """Generate a substrate network
    
    Input: 
      n: Number of nodes in substrate network
      g: Grid scale
      p: Probability of two edges connected
      s: Seed for random generating
      nm: Name of the substarte network
      cpu_c: Computing resources, uniform distribution variables, a two element list [min CPU, max CPU]
      bw_c: Bandwidth resources, uniform distribution varibales, a two element list [min BW, max BW]
      
    Ouput:
      A graph of n nodes with edges connectivity p in a scale of g
  """

  G = generate_basic_graph(n, g, p, s, nm)
  G.graph['name'] = nm

  #Add CPU capacity to substarte network
  a = cpu_c[0]
  b = cpu_c[1]
  for node in G.nodes_iter():
    G[node]['cpu_capacity'] = generate_uniform_distribution(a, b)
  
  #Add Bandwidth capacity to substrate network
  a = bw_c[0]
  b = bw_c[1]
  for edge in G.edges_iter():
    G[edge[0]][edge[1]]['bandwidth_capacity'] = generate_uniform_distribution(a, b)

  return G

def generate_virtual_network(n, p, s, nm, cpu_d, bw_d):
  """Generate a virtual network
     
    Scale is default to 100

    Input:
      n: number of nodes in virtual network
      p: probablity of two edges connected 
      s: seed for random generating
      nm: name of the virtual network
      cpu_d: CPU demand, uniform distribution variables, a two element list [min CPU, max CPU]
      bw_d: Bandwidth demand, uniform distribution varibales, a two element list [min BW, max BW]
    
    Output:
      A graph of n nodes with edges connectivity p 
      
  """
  G = generate_basic_graph(n, 100, p, s, nm)
  G.graph['name'] = nm

  #Add CPU capacity to substarte network
  a = cpu_d[0]
  b = cpu_d[1]
  for node in G.nodes_iter():
    G[node]['cpu_demand'] = generate_uniform_distribution(a, b)
  
  #Add Bandwidth capacity to substrate network
  a = bw_d[0]
  b = bw_d[1]
  for edge in G.edges_iter():
    G[edge[0]][edge[1]]['bandwidth_demand'] = generate_uniform_distribution(a, b)

  return G


if __name__ == '__main__':
  substrate_network = generate_substrate_network(100, 100, 0.11, 0, 'Substrate_Network', [50, 100], [50, 100])
  virtual_network = generate_virtual_network(6, 0.5, 0, 'Virtual_Network', [0, 50], [0, 50])
  print 'Substrate_Network'
  print substarte_network.graph
  print 'Virtual_Network'
  print virtual_network.graph