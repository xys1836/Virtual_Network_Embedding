import numpy as np
import logging
import copy

def grc_resources(G, d):
  r = []
  c = []
  sum_c = global_computing_resources(G) 
  for node in G.nodes():
    u = G.node[node]['cpu_capacity'] 
    c.append(normalized_computing_resource(sum_c, u))
  r = copy.deepcopy(c)
  #print r
  for node in G.nodes():
    r[node] = (1 - d) * c[node] + d * bandwidth_resources_transition(G, node, r) 

  return r

def global_computing_resources(G):
  """Calculate global computing resources

    Sum of computing resource of nodes
     
    Input:
      G: the graph with node and computing attributes
    Output:
      The global computing resources
  """
  sum_c = 0
  for node in G.nodes():
    sum_c = sum_c + G.node[node]['cpu_capacity'] 
  return sum_c

def normalized_computing_resource(sum_c, u):
  """Normalized computing resource in GRC

    Calculate normalized computing resource
      computing_resources/sum_of_computing_resources
    Input:
      sum_c: Sum of computing resouces
      u: Computing resource of node u
    Output:
      normalized computing resource of u   
  """
  c = u*1.0 / sum_c
  
  return c

def computing_resources_matrix(G):
  """Computing resources matrix

    Input: 
      G: the graph
    Output:
      A matrix in numpy matrix form of computing resource 
  """
  c = []
  sum_c = global_computing_resources(G)
  for node in G.nodes():
    u = G.node[node]['cpu_capacity'] 
    c.append(normalized_computing_resource(sum_c, u))
  return np.matrix(c).T

def bandwidth_resource(G, u, v):
  """Bandwidth resource between node u and node v
  """
  return G.edge[u][v]['bandwidth_capacity']

def adjacent_bandwidth_resources(G, u):
  """Adjacent bandwidth resources of node u

    Sum of the bandwidth capacities of node u's adjacent paths
    Input:
      G: the graph
      u: the node
    Output:
      The sum of bandwidth capacities of node u's adjacent paths
  """
  sum_b = 0
  for n in G.neighbors(u):
    sum_b = sum_b + bandwidth_resource(G, u, n)
  return sum_b

def bandwidth_resources_transition(G, u, r):
  """Bandwidth resource transition in numberal form

    *** Warning ***
    This function should multiple r(v) in order to calculate r(u) in numberal form 
    This is only used in numberal case, not in matrix case
    
    Calculate and sum each path adjacent node u 's weight among u's neighbour's 
    adjacent paths
    
    Input:
      G: the graph
      u: the node
      r: list of node grc vector  ## here is not very well maybe there is a bug
    Output:
      Sum of each path adjacent node u 's weight among u's neighbour's 
    adjacent paths
  """
  sum_bt = 0
  for v in G.neighbors(u):
    sum_bt = sum_bt + bandwidth_resource(G, u, v)*1.00 / adjacent_bandwidth_resources(G, v)* r[v] 
  return sum_bt
    
def transition_matrix(G):
  """Transition matrix
    
    Calculate transtion matrix. This function return a numpy matrix data structure

    Input:
      G: the graph
    Output:
      A matrix in numpy natrix form of bandwidth transition
  """
  num_v = G.number_of_nodes()
  m = np.zeros((num_v,num_v)) 
  for node in G.nodes():
    for neighbor in G.neighbors(node):
      m[node][neighbor] = bandwidth_resource(G, node, neighbor) * 1.00 / adjacent_bandwidth_resources(G, neighbor)
  m = np.matrix(m)
  return m

def grc_vector(G, th, d):
  """GRC Vector

    Calculate GRC Vector according to Algorithm 1 
   
    Input:
      G: the grpah 
      th: pre-set small positive threshold 
      d: a constan damping factor 
    Output:
      GRC vector r
  """

  m = transition_matrix(G)
  c = computing_resources_matrix(G)
  r_p = c
  r_c = c.copy()
  #print c
  delta = 2**10 * 1.00 ## should be a very large float number, larger than th
  while delta >= th:
    r_c = (1-d)*c + d*(m*r_p)
    delta = np.linalg.norm(r_c - r_p, 1)
    r_p = r_c.copy()
  return r_c


