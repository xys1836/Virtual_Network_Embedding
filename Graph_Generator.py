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

def generate_graph(n, g, p, s, name = None):
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


if __name__ == '__main__':
  G = generate_graph(100,100,0.11,0,'Substrate')
  print G.number_of_nodes()
  print G.number_of_edges()
  print G.nodes()
  print G.edges()
#for i in range(0,100):
#  print generate_uniform_distribution(1,100)
