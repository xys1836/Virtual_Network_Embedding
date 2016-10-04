import numpy as np
import logging
import copy
import networkx as nx

class RankBasedMapping:
  """The based class for rank based mapping method
  """

  def __init__(self):
    pass

  def cpu_capacity(self, G, node):
    return G.node[node]['cpu_capacity']

  def bandwidth_capacity(self, G, node_U, node_v):
    return G.edge[node_u][node_v]['bandwidth_capacity']

  def rank_based_node_mapping(self, sn, vn, sn_rank, vn_rank):
    """Rank based node mapping
      
      Greedy node mapping algorithm, descripted in algorithm 2 in paper.
      This is a large to large mapping method
       
      Input:
        sn: the substrate network topology 
        vn: the virtual network topology
        sn_rank: the node rank list of substrate network 
        vn_rank: the node rank list of virtual network
      Output:
        if all nodes in virtual network mapped sccessfully,
          return the map dictionary
          {node in virtual network : node in substrate network}    
        else
          return None
    """
    number_of_virtual_network_nodes = len(vn.nodes())
    if (len(vn.nodes()) is not len(vn_rank)) and \
       (len(sn.nodes()) is not len(sn_rank)):
      ## 
      return None
    vn_sn_node_map = {}     ## {vn_node : sn_node}

    sn_rank_node_map = {}    ## {rank_value : node_number}
    vn_rank_node_map = {} 

    sn_rank_list = []        ## node with highest rank value come to last
    vn_rank_list = []

    #sn_grc = grc_vector(sn, th, d)
    #vn_grc = grc_vector(vn, th, d)

    number_of_mapped_nodes = 0 ## the number of mapped nodes in vn
     
    for i in range(0, len(sn.nodes())):
      ## map rank value to nodes
      sn_rank_node_map[sn_rank[i]] = i
     
    for rank, n in sorted(sn_rank_node_map.items()):
      ## sort rank value list, node with highest value come to last
      sn_rank_list.append(n)
     
    for i in range(0, len(vn.nodes())):
      ## map rank value to nodes
      vn_rank_node_map[vn_rank[i]] = i
    
    for rank, n in sorted(vn_rank_node_map.items()):
      ## sort rank value list, node with highest rank value come to last
      vn_rank_list.append(n)

    while sn_rank_list and vn_rank_list:
      """The loop stops when any of sn_rank_list and vn_rank_list is NULL
      """
      ## Get the node with highest rank value in this iteration
      vn_node = vn_rank_list.pop()
      sn_node = sn_rank_list.pop()

      ## Cet the cpu capacity of node
      vn_cpu_capacity = vn.node[vn_node]['cpu_capacity']
      sn_cpu_capacity = sn.node[sn_node]['cpu_capacity']

      if sn_cpu_capacity >= vn_cpu_capacity:
        ## the CPU capacity is sufficient for this virtual node
        ## map this vn node to this sn node
        vn_sn_node_map[vn_node] = sn_node
        
        ## Commented all the following 3 line code
        ## we update the node CPU capacity after both node and link map
        ## successfully
        ## set sn node's cpu capacity equal new capacity
        ## sn.node[sn_node]['cpu_capacity'] = sn.node[sn_node]['cpu_capacity'] \
        ##                                   - vn.node[vn_node]['cpu_capacity']
        number_of_mapped_nodes = number_of_mapped_nodes + 1
      else:
        ## the CPU capacity is not sufficient for this virtual node
        ## put the vn node back to vn_rank_list, waiting for next map
        vn_rank_list.append(vn_node)
    if number_of_mapped_nodes == number_of_virtual_network_nodes:
      ## All node in vn has been mapped successfully
      ## todo something
      return vn_sn_node_map
    else:
      return None

  def shortest_path_based_link_mapping(self, sn, vn, vn_sn_node_map):
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
        if all links in virtual network mapped sucessfully, 
        return
        vn_sn_link_map: links mapping dictionary
                        {link in virtual network : 
                         nodes in substrate network along the shortest path} 
                        {(node_u, node_v) : [node_u, node_v, node_x,...]}
        sn_tmp_main: the graph after mapping link  
        else
        return None, None
    """
    vn_sn_link_map = {}
    sn_tmp = copy.deepcopy(sn) ## make a copy of sn for cutting link
    sn_tmp_main = copy.deepcopy(sn) ## make a copy for mapping
    for vn_edge in vn.edges():
      ## Mapping edge in virtual network
      vn_node_u = vn_edge[0]
      vn_node_v = vn_edge[1]
      sn_tmp = copy.deepcopy(sn_tmp_main)
      vn_bw_cap = vn.edge[vn_node_u][vn_node_v]['bandwidth_capacity']
      for sn_edge in sn_tmp.edges():
        ## Remove the link whose bw is smaller than the vn's request bw
        sn_node_u = sn_edge[0]
        sn_node_v = sn_edge[1]
        sn_bw_cap = sn_tmp.edge[sn_node_u][sn_node_v]['bandwidth_capacity']
        if vn_bw_cap > sn_bw_cap:
          ## Cut the link 
          sn_tmp.remove_edge(sn_node_u, sn_node_v)
      
      ## Try to find a shortest path
      try:
        shortest_path = nx.shortest_path(sn_tmp,
                                      vn_sn_node_map[vn_node_u],
                                      vn_sn_node_map[vn_node_v])  
      except nx.NetworkXNoPath:
        ## If there is no path between nodes, throw this exception
        ## and return False
        return None, None
      if shortest_path:
        ## If a shortest path exists between nodes,
        ## Update the bandwidth along the path in substrate network tmp 
        ## We do not acutually modify the substrate network
        vn_sn_link_map[(vn_node_u, vn_node_v)] = shortest_path
        for i in range(0, len(shortest_path)-1):
          ## Update the bandwidth along the path in substrate network tmp
          node_u = shortest_path[i]
          node_v = shortest_path[i+1]
          sn_tmp_main.edge[node_u][node_v]['bandwidth_capacity'] \
            = sn_tmp_main.edge[node_u][node_v]['bandwidth_capacity'] - vn_bw_cap    
      else:
        ##  If there is not a shortest path between nodes
        return None, None
    return vn_sn_link_map, sn_tmp_main

class GRC(RankBasedMapping):
  """Global reosources capacity algorithm
  """
  def __init__(self, grc_thread, grc_delta):
    RankBasedMapping.__init__(self)
    self.thread = grc_thread
    self.delta = grc_delta
    #self.substrate_network = grc_substrate_network
  def grc_global_computing_resources(self, G):
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

  def grc_normalized_computing_resource(self, sum_c, u):
    """Normalized computing resource in GRC
      
      Calculate normalized computing resource
        computing_resources/sum_of_computing_resources
      Input:
        sum_c: Sum of computing resouces
            u: Computing resource of node u
      Output:
        normalized computing resource of u   
    """
    return u*1.0 / sum_c

  def grc_computing_resources_matrix(self, G):
    """Computing resources matrix
      
      Input: 
        G: the graph
      Output:
        A matrix in numpy matrix structure of computing resource 
    """
    c = []
    sum_c = self.grc_global_computing_resources(G)
    for node in G.nodes():
      u = G.node[node]['cpu_capacity'] 
      c.append(u*1.0/sum_c)
    return np.matrix(c).T

  def grc_adjacent_bandwidth_resources(self, G, u):
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
      sum_b = sum_b + G.edge[n][u]['bandwidth_capacity']
    if sum_b is 0:
      logging.error('adjacent_bandwidth_resources is ZERO')
    return sum_b
  
  def grc_transition_matrix(self, G):
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
        m[node][neighbor] = G.edge[node][neighbor]['bandwidth_capacity'] \
                   * 1.00 / self.grc_adjacent_bandwidth_resources(G, neighbor)
    m = np.matrix(m)
    return m

  def grc_vector(self, G, th, d):
    """GRC Vector
       
      Calculate GRC Vector according to Algorithm 1 
       
      Input:
        G: the graph 
        th: pre-set small positive threshold 
        d: a constant damping factor 
      Output:
        GRC vector r in list structure
    """
    m = self.grc_transition_matrix(G)
    c = self.grc_computing_resources_matrix(G)
    r_p = c
    r_c = c.copy()  ## todo: check r_p r_c address
    r_c_list = [] 
    delta = 2**10 * 1.00 ## should be a very large float number, larger than th
    while delta >= th:
      r_c = (1-d)*c + d*(m*r_p)
      #print 'r_c', r_c
      #print 'r_p', r_p
      delta = np.linalg.norm(r_c - r_p, 1)
      r_p = r_c.copy()
    ## Convert vector to python list structure
    r_c = r_c.tolist()
    for value in r_c:
      r_c_list.append(value[0])
    return r_c_list
  
  def grc_node_mapping(self, sn, vn, th, d):
    sn_grc_list = self.grc_vector(sn, th, d)
    vn_grc_list = self.grc_vector(vn, th, d)
    return self.rank_based_node_mapping(sn, vn, sn_grc_list, vn_grc_list)

  def grc_link_mapping(self, sn, vn, vn_sn_node_map):
    return self.shortest_path_based_link_mapping(sn, vn, vn_sn_node_map)

  def grc_mapping(self, sn, vn):
    """Mapping virtual network on substrate network
        
      Input:
        sn: substrate network
        vn: vitural network
      Output:
        <vn_sn_node_map, vn_sn_link_map, mapped substrate network>
        if failed, return <None, None, None>
    """
    th = self.thread
    d = self.delta
    #sn = self.substrate_network
    sn_tmp = copy.deepcopy(sn)
    vn_sn_node_map = {}
    vn_sn_link_map = {}
    vn_sn_node_map = self.grc_node_mapping(sn, vn, th, d)
    if vn_sn_node_map is not None:
      (vn_sn_link_map, sn_tmp) = self.grc_link_mapping(sn, vn, vn_sn_node_map)
    else:
      print "GRC Node Mapping Failed"
      return None, None, None
    if vn_sn_link_map is not None:
      ## Update node capacity in sn
      for node in vn.nodes():
        vn_cpu_capacity = vn.node[node]['cpu_capacity']
        sn_node = vn_sn_node_map[node]
        sn_tmp.node[sn_node]['cpu_capacity'] = sn.node[sn_node]['cpu_capacity'] \
                                           - vn.node[node]['cpu_capacity']
      return vn_sn_node_map, vn_sn_link_map, sn_tmp
    else:
      print 'GRC Link Mapping Failed'
      return None, None, None

  def mapping(self, sn, vn):
    return self.grc_mapping(sn, vn)

class RTK(RankBasedMapping):
  """This is the algorithm in rethinking ... paper"""
  def __init__(self):
    RankBasedMapping.__init__(self)

  def rtk_node_resources(self, G):
    """Calculate the node resources
      
      to do 
      write down the detail of the cacluation 
      Input:
        G: the network topology
      Output:
        available_resources_list: the list of available node resouces
    """
    available_resources_list = []
    for node in G.nodes():
      bw = 0
      for n in G.neighbors(node):
        bw = bw + G.edge[node][n]['bandwidth_capacity']
      cpu = G.node[node]['cpu_capacity']
      available_resources_list.append(cpu * bw)
    return available_resources_list

  def rtk_node_mapping(self, sn, vn):
    sn_rank_list = self.rtk_node_resources(sn)
    vn_rank_list = self.rtk_node_resources(vn)
    return self.rank_based_node_mapping(sn, vn, sn_rank_list, vn_rank_list)

  def rtk_link_mapping(self, sn, vn, vn_sn_node_map):
    return self.shortest_path_based_link_mapping(sn, vn, vn_sn_node_map)

  def rtk_mapping(self, sn, vn):
    """Mapping virtual network on substrate network
        
      Input:
        sn: substrate network
        vn: vitural network
      Output:
        <vn_sn_node_map, vn_sn_link_map, mapped substrate network>
        if failed, return <None, None, None>
    """
    sn_tmp = copy.deepcopy(sn)
    vn_sn_node_map = {}
    vn_sn_link_map = {}
    vn_sn_node_map = self.rtk_node_mapping(sn, vn)
    if vn_sn_node_map is not None:
      (vn_sn_link_map, sn_tmp) = self.rtk_link_mapping(sn, vn, vn_sn_node_map)
    else:
      print "RTK Node Mapping Failed"
      return None, None, None
    if vn_sn_link_map is not None:
      ## Update node capacity in sn
      for node in vn.nodes():
        vn_cpu_capacity = vn.node[node]['cpu_capacity']
        sn_node = vn_sn_node_map[node]
        sn_tmp.node[sn_node]['cpu_capacity'] = sn.node[sn_node]['cpu_capacity'] \
                                           - vn.node[node]['cpu_capacity']
      return vn_sn_node_map, vn_sn_link_map, sn_tmp
    else:
      print 'RTK Link Mapping Failed'
      return None, None, None

  def mapping(self, sn, vn):
    return self.rtk_mapping(sn, vn)
