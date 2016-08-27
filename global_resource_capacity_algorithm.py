#import networkx as nx
import numpy as np
import logging
def grc_resource(G, u):
  pass
  #return r

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

def bandwidth_resources_transition(G, u):
  """Bandwidth resource transition in numberal form

    *** Warning ***
    This function should multiple r(v) in order to calculate r(u) in numberal form 
    
    Calculate and sum each path adjacent node u 's weight among u's neighbour's 
    adjacent paths
    
    Input:
      G: the graph
      u: the node

    Output:
      Sum of each path adjacent node u 's weight among u's neighbour's 
    adjacent paths
  """
  sum_bt = 0
  for v in G.neighbors(u):
    sum_bt = sum_bt + bandwidth_resource(G, u, v)*1.00 / adjacent_bandwidth_resources(G, v)
  return sum_bt
    
def transition_matrix(G):
  """Transition matrix
  
     Calculate transtion matrix. This function return a numpy matrix data structure

     Input:
       G: the graph

     Output:
       A matrix in numpy natrix form 
  """
  num_v = G.number_of_nodes()
  m = np.zeros((num_v,num_v)) 
  for node in G.nodes():
    for neighbor in G.neighbors(node):
      m[node][neighbor] = bandwidth_resource(G, node, neighbor) * 1.00 / adjacent_bandwidth_resources(G, neighbor)
  m = np.matrix(m)
  return m
