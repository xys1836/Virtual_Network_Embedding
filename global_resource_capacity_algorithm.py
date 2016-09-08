import numpy as np
import logging
import copy
import networkx as nx
"""
logging.basicConfig(format ='%(asctime)s %(message)s', \
                    datefmt='%m/%d/%Y%I:%M:%S%p', \
                    filename = 'grc.log', \
                    level=logging.DEBUG)
"""

def grc_resources(G, d):
  r = []
  c = []
  sum_c = global_computing_resources(G) 
  for node in G.nodes():
    u = G.node[node]['cpu_capacity'] 
    c.append(normalized_computing_resource(sum_c, u))
  r = copy.deepcopy(c)
  
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
  #logging.debug('global_computing_resources')
  sum_c = 0
  for node in G.nodes():
    #print 'node capacity',G.node[node]['cpu_capacity']
    sum_c = sum_c + G.node[node]['cpu_capacity'] 
  #logging.debug('global_computing_resources: %s', sum_c)a
  #print 'sum_c: ', sum_c
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
  #logging.debug(normalized_computing_resource)
  return u*1.0 / sum_c

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
  #logging.debug('adjacent_bandwidth_resources')
  sum_b = 0
  for n in G.neighbors(u):
    sum_b = sum_b + bandwidth_resource(G, u, n)
    #logging.debug(sum_b)
  #logging.debug('adjacent_bandwidth_resources: %s', sum_b)
  if sum_b is 0:
    logging.error('adjacent_bandwidth_resources is ZERO')
  return sum_b

def bandwidth_resources_transition(G, u, r):
  """Bandwidth resource transition in numberal form

    *** Warning ***
    This function should multiple r(v) in order to 
    calculate r(u) in numberal form. This is only used in numberal case, 
    not in matrix case
    
    Calculate and sum each path adjacent node u 's weight 
    among u's neighbour's adjacent paths
    
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
    sum_bt = sum_bt + bandwidth_resource(G, u, v)*1.00 \
             / adjacent_bandwidth_resources(G, v)* r[v] 
  return sum_bt
    
def transition_matrix(G):
  """Transition matrix
    
    Calculate transtion matrix. 
    This function return a numpy matrix data structure

    Input:
      G: the graph
    Output:
      A matrix in numpy natrix form of bandwidth transition
  """
  num_v = G.number_of_nodes()
  m = np.zeros((num_v,num_v)) 
  for node in G.nodes():
    for neighbor in G.neighbors(node):
      m[node][neighbor] = bandwidth_resource(G, node, neighbor) * 1.00 \
                          / adjacent_bandwidth_resources(G, neighbor)
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
  
  delta = 2**10 * 1.00 ## should be a very large float number, larger than th
  while delta >= th:
    r_c = (1-d)*c + d*(m*r_p)
    delta = np.linalg.norm(r_c - r_p, 1)
    r_p = r_c.copy()
  return r_c

def add_grc_to_network(G, th, d):
  """Add grc to network

    Add grc rank score to network topology G

    Input:
       G: the network topology
      th: pre-set small positive threshold
       d: a constant damping factor
    Output:
      The network topology with grc rank score
  """
  num_of_nodes = len(G.nodes())
  g_grc_vector = grc_vector(G, th, d)
  
  for i in range(0, num_of_nodes):
    G.node[i]['grc'] = g_grc_vector[i,0]
  return G

def greedy_node_mapping(sn, vn, th, d):
  """Greedy node mapping

    Greedy node mapping algorithm, descripted in algorithm 2 in paper.
        
    *** WARNING ***
    The function will always return vn_sn_map although the mapping may fail
    In this case, vn_sn_map may be None or a partial mapping
 
    Input:
      sn: the substrate network topology 
      vn: the virtual network topology
      th: pre-set small positive threshold
       d: a constant damping factor
    Output:
      Boolean: True, if all node in virtual network mapped sucessfully, 
               or return False
      vn_sn_node_map: node mapping dictionary
                 {node in virtual network : node in substrate network}    
  """
  sn_grc_node_map = {}
  vn_grc_node_map = {}
  vn_sn_node_map = {}
  sn_grc_list = []
  vn_grc_list = []
  sn_grc = grc_vector(sn, th, d)
  vn_grc = grc_vector(vn, th, d)
  number_of_virtual_network_nodes = len(vn.nodes())
  number_of_mapped_nodes = 0

  for i in range(0, len(sn.nodes())):
    ## map grc to nodes
    sn_grc_node_map[sn_grc[i,0]] = i
  
  for grc, n in sorted(sn_grc_node_map.items()):
    ## sort grc list, node with highest grc come to last
    sn_grc_list.append(n)
  
  for i in range(0, len(vn.nodes())):
    ## map grc to nodes
    vn_grc_node_map[vn_grc[i,0]] = i
  
  for grc, n in sorted(vn_grc_node_map.items()):
    ## sort grc list, node with highest grc come to last
    vn_grc_list.append(n)
  while sn_grc_list and vn_grc_list:
    vn_node = vn_grc_list.pop()
    sn_node = sn_grc_list.pop()
    vn_cpu_capacity = vn.node[vn_node]['cpu_capacity']
    sn_cpu_capacity = sn.node[sn_node]['cpu_capacity']
    if sn_cpu_capacity >= vn_cpu_capacity:
      ## the CPU capacity is sufficient for this virtual node
      ## map this vn node to this sn node
      vn_sn_node_map[vn_node] = sn_node
      ## set sn node's cpu capacity equal new capacity
      sn.node[sn_node]['cpu_capacity'] = sn.node[sn_node]['cpu_capacity'] \
                                         - vn.node[vn_node]['cpu_capacity']
      number_of_mapped_nodes = number_of_mapped_nodes + 1
    else:
      ## the CPU capacity is not sufficient for this virtual node
      ## put the vn node back to vn_grc_list, waiting for next map
      vn_grc_list.append(vn_node)
  return number_of_mapped_nodes == number_of_virtual_network_nodes, \
         vn_sn_node_map, sn

def shortest_path_based_link_mapping(sn, vn, vn_sn_node_map):
  """Shortest path based link mapping
  
    Mapping link based on shortest path
    In mapping each edge in virtual network round, first cut off all edges
    in substrate network whose bandwidth capacity is smaller than that in this 
    virtual network edge. Then find shortest path on the new substrate network
    According to Algorithm 3 in paper
   
    *** WARNING ***
    The function will always return vn_sn_map although the mapping may fail
    In this case, vn_sn_map may be None or a partial mapping
 
    Input:
      sn: substrate network topology
      vn: virtual network topology
      vn_sn_node_map: node mapping dictionary
                      {node in virtual network : node in substrate network} 
    Ouput: 
      Boolean: True, if all links in virtual network mapped sucessfully, 
               or return False
      vn_sn_link_map: links mapping dictionary
                      {link in virtual network : 
                       nodes in substrate network along the shortest path} 
                      {(node_u, node_v) : [node_u, node_v, node_x,...]}
  """
  vn_sn_link_map = {}
  sn_tmp = copy.deepcopy(sn)
  for vn_edge in vn.edges():
    ## Mapping edge in virtual network
    vn_node_u = vn_edge[0]
    vn_node_v = vn_edge[1]
    sn_tmp = copy.deepcopy(sn)
    vn_bw_cap = vn.edge[vn_node_u][vn_node_v]['bandwidth_capacity']
    for sn_edge in sn_tmp.edges():
      ## Remove the link whose bw is smaller than the vn's request bw
      sn_node_u = sn_edge[0]
      sn_node_v = sn_edge[1]
      sn_bw_cap = sn.edge[sn_node_u][sn_node_v]['bandwidth_capacity']
      if vn_bw_cap > sn_bw_cap:
        sn_tmp.remove_edge(sn_node_u, sn_node_v)
    try:
      shortest_path = nx.shortest_path(sn_tmp,
                                    vn_sn_node_map[vn_node_u],
                                    vn_sn_node_map[vn_node_v])  
    except nx.NetworkXNoPath:
      ## If there is no path between nodes, throw this exception
      ## and return False
      return False, vn_sn_link_map, sn
    if shortest_path:
      ## If there is a shortest path between nodes,
      ## Update the bandwidth along the path in substrate network
      vn_sn_link_map[(vn_node_u, vn_node_v)] = shortest_path
      for i in range(0, len(shortest_path)-1):
      ## Update the bandwidth along the path in substrate network
        node_u = shortest_path[i]
        node_v = shortest_path[i+1]
        sn.edge[node_u][node_v]['bandwidth_capacity'] \
          = sn.edge[node_u][node_v]['bandwidth_capacity'] - vn_bw_cap    
    else:
      ##  If there is not a shortest path between nodes
      return False, vn_sn_link_map, sn
  return True, vn_sn_link_map, sn


def grc_mapping(sn, vn, th, d):
  """GRC Mapping

    This is a overall function which realized the grc algorithm.
    
    Input:
      sn: substrate network topology
      vn: virtual network tolplogy
      th: pre-set small positive threshold
       d: a constant damping factor
    Output:
      (Boolean, vn_sn_node_map, vn_sn_link_map)
      Boolean: True if both node and link mapping sucessed
               False if any one of node or link mapping failed
      vn_sn_node_map: node mapping dictionary
                 {node in virtual network : node in substrate network}    

      vn_sn_link_map: links mapping dictionary
                      {link in virtual network : 
                       nodes in substrate network along the shortest path} 
                      {(node_u, node_v) : [node_u, node_v, node_x,...]}

  """
  #logging.info('GRC mapping \n GRC_th: %s \n GRC_d: %s', th, d)
  vn_sn_node_map = {}
  vn_sn_link_map = {}
  sn_tmp = copy.deepcopy(sn)
  suc_node = False
  suc_link = False
  sn = sn_tmp 
  #logging.info('GRC node mapping: %s', suc)
  if suc_node:
    (suc_link, vn_sn_link_map, sn_tmp) = shortest_path_based_link_mapping(sn_tmp, vn, 
                                                            vn_sn_node_map)
    # logging.info('GRC link mapping: %s', suc_node)
    if suc_link:
      #logging.info(vn_sn_node_map)
      #logging.info(vn_sn_link_map)
      sn = copy.deepcopy(sn_tmp)
      #sn = sn_tmp
      return True, vn_sn_node_map, vn_sn_link_map, sn_tmp
    else:
      return False, vn_sn_node_map, vn_sn_link_map, sn_tmp
  else:
    return False, vn_sn_node_map, vn_sn_link_map, sn_tmp


class GRC:
  def __init__(self, th, d):
    self.thred = th
    self.delt = d
  def mapping(self, sn, vn):
    return grc_mapping(sn, vn, self.thred, self.delt)

