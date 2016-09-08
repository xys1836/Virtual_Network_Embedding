from poisson_process import next_time
from graph_generator import generate_substrate_network
from graph_generator import generate_virtual_network
from graph_generator import generate_virtual_network_with_lifetime
from global_resource_capacity_algorithm import grc_mapping
from global_resource_capacity_algorithm import GRC
import logging
import random
import matplotlib.pyplot as plt
logging.basicConfig(format ='%(asctime)s %(message)s', \
                    datefmt='%m/%d/%Y%I:%M:%S %p', \
                    filename = 'vne.log', level=logging.INFO)

class Virtual_Network_Queue:
  def __init__(self):
    self.virtual_network_list = []
    self.window_size = 1
  def isEmpty(self):
    return self.virtual_network_list == []
  
  def enqueue(self, item):
    self.virtual_network_list.insert(0, vn)

  def dequeue(self):
    if not isEmpty:
      return self.virtual_network_list.pop()
    else:
      return None
  def dequeue_window_size(self):
    if isEmpty():
      return None
    if self.size() > self.window_size:
      _w = self.virtual_network_list[0:self.window_size]
      return _w.reverse()
    else:
      _w = self.virtual_network_list[:]
      return _w.reverse()

  def size(self):
    return len(self.virtual_network_list)

class VNE:
  def __init__(self, algorithm):
    self.time_length = 50000
    self.current_time = 0
    self.next_time = 0
    self.virtual_network_arrival_time_interval = 20.0
    self.virtual_network_lifetime = 500.0
    self.number_of_vn = 0 
    self.window_size = 1
    self.virtual_network_queue = Virtual_Network_Queue()
    self.mapping_algorithm = algorithm
    self.substrate_network = None
    self.virtual_network_node_mapping = {} ## virtual network name : nodemapping
    self.virtual_network_link_mapping = {}
    self.mapped_virtual_network = []
    self.suc_count = 0
    self.reject_count = 0
    self.reject_list = []
    self.x_axis = []
  def init_all():
    self.number_of_vn = 0

  def start(self):
    self.current_time = 0
    next_t = next_time(1 / self.virtual_network_arrival_time_interval)
    for t in range(0, self.time_length):
      self.current_time = t
      #logging.debug('Current Time: %s', self.current_time )
      self.virtual_network_depart(self.mapped_virtual_network) 
      if self.current_time >= next_t:
        ## An virtual network arrived
        #print 'Virtual Network Arrived'
        #logging.info('Time Seq: %s  New Virtual Network arrived', \
        #              self.current_time)
        #logging.debug('Current time: %s', self.current_time)
        
        self.number_of_vn = self.number_of_vn + 1
        next_t = self.current_time + \
                 next_time(1/self.virtual_network_arrival_time_interval)
        print 'number of virtual network: ', self.number_of_vn 
        ## ******* Create a new virtual network ******* ##
        vm_name = 'VN' + str(self.number_of_vn)
        numer_of_virtual_network_nodes = random.randint(2, 20)
        #logging.debug('Number of Virtual Network Nodes: %s',numer_of_virtual_network_nodes)
        virtual_network =  \
        self.generate_virtual_network_with_lifetime(numer_of_virtual_network_nodes, 0.5, 0, 
                                                         vm_name, 
                                                         [1, 50], [1, 50], 
                                              self.virtual_network_lifetime)
        virtual_network.depart_time = virtual_network.lifetime + self.current_time
        #logging.debug('virtual network depart time: %s', virtual_network.depart_time)


        ## ******* MAP VN to SN *********************##
        (suc, vn_sn_node_map, vn_sn_link_map, sn_tmp) = \
        self.mapping(self.substrate_network, virtual_network)
        #logging.info('Mapping: %s', suc)
        #logging.debug('Mapping: %s', vn_sn_node_map)
        ## ******* MAP END ***********************##

        if suc:
          self.substrate_network = sn_tmp
          self.suc_count = self.suc_count + 1
          self.mapped_virtual_network.append(virtual_network)
          self.virtual_network_node_mapping[virtual_network.graph['name']] = vn_sn_node_map
          self.virtual_network_link_mapping[virtual_network.graph['name']] =vn_sn_link_map
        else:
          self.reject_count = self.reject_count + 1

        rr = self.reject_count * 1.0 / self.number_of_vn
        self.reject_list.append(rr)
        self.x_axis.append(self.current_time)
        #logging.info('reject rate: %s', rr)
        print 'reject rate: ', rr
  def _enqueue(self, vn, queue):
    queue.append(vn)
    return queue
  def _dequeue(self, queue):
    if vn_queue:
      return queue.pop(0)
    else: 
      return False
  def _dequeue_num(self, num, queue):
    length = len(queue)
    if num > length:
      return queue[0:length]
    else:
      return queue[0:num]
  def generate_substrate_network(self, n, g, p, s, nm, cpu_c, bw_c):
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
    self.substrate_network = generate_substrate_network(n, g, p, s, nm, cpu_c, bw_c) 
    return self.substrate_network
  def generate_virtual_network(self, n, p ,s, nm, cpu_d, bw_d):
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
    vn = generate_virtual_network(n, p, s, nm, cpu_d, bw_d)
    return vn
  def generate_virtual_network_with_lifetime(self, n, p, s, nm, cpu_d, bw_d,lf_t):
    vn = generate_virtual_network_with_lifetime(n, p, s, nm, cpu_d, bw_d, lf_t)
    return vn
  def mapping(self, sn, vn):
    return self.mapping_algorithm.mapping(sn, vn)
  def virtual_network_depart(self, vn_list):
    for vn in vn_list:
      if self.current_time > vn.depart_time:
        ## add CPU and BW Capacity
        #print 'Virtual Network depart:', vn.graph['name']
        vn_list.remove(vn)
        node_mapping = self.virtual_network_node_mapping[vn.graph['name']]
        link_mapping = self.virtual_network_link_mapping[vn.graph['name']]
        for node in vn.nodes():
          self.substrate_network.node[node_mapping[node]]['cpu_capacity'] = \
          self.substrate_network.node[node_mapping[node]]['cpu_capacity'] + \
                                            vn.node[node]['cpu_capacity']
        for edge in vn.edges():
          bw = vn.edge[edge[0]][edge[1]]['bandwidth_capacity']
          sn_edges = link_mapping[edge]
          for i in range(0, len(sn_edges) - 1):
            self.substrate_network.edge[sn_edges[i]][sn_edges[i+1]]['bandwidth_capacity'] = \
            self.substrate_network.edge[sn_edges[i]][sn_edges[i + 1]]['bandwidth_capacity'] + bw

if __name__ == '__main__':
  grc = GRC(0.00001, 0.85)
  vne = VNE(grc)
  print vne.generate_substrate_network(100, 100, 0.11, 0, 'Substrate_Network',
                                      [50, 100], [50, 100])

  vne.start()
  rr = vne.reject_list
  plt.plot(vne.x_axis,rr)
  plt.show()
