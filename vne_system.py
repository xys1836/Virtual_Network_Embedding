from poisson_process import next_time
from graph_generator import generate_substrate_network
from graph_generator import generate_virtual_network
from graph_generator import generate_virtual_network_with_lifetime
#from global_resource_capacity_algorithm import grc_mapping
from global_resource_capacity_algorithm_obj import GRC
from global_resource_capacity_algorithm_obj import RTK
import logging
import random
import copy
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
  def __init__(self, algorithm, algorithm_c):
    self.mapping_algorithm = algorithm
    self.mapping_algorithm_c = algorithm_c

    self.time_length = 50000
    self.current_time = 0
    self.next_time = 0
    self.virtual_network_arrival_time_interval = 20.0
    self.virtual_network_lifetime = 500.0

    self.number_of_vn = 0 
    self.substrate_network = None
    self.substrate_network_c = None
    self.virtual_network_node_mapping = {} ## virtual network name : nodemapping
    self.virtual_network_link_mapping = {}
    self.virtual_network_node_mapping_c = {} ## virtual network name : nodemapping
    self.virtual_network_link_mapping_c = {}
    self.mapped_virtual_network_list = []
    self.mapped_virtual_network_list_c = []

    ## For draw figure and some statistic
    self.suc_count = 0
    self.suc_count_c = 0
    self.reject_count = 0
    self.reject_count_c = 0
    self.reject_list = []
    self.reject_list_c = []
    self.cpu_utility_rate_list = []
    self.cpu_utility_rate_list_c = []
    self.cpu_utility_rate_rejected_list = [] ## the cpu utility rate when a vnr
                                             ## is rejected
    self.cpu_utility_rate_rejected_list_c = []
    self.bw_utility_rate_rejected_list = []
    self.bw_utility_rate_rejected_list_c = []

    self.bw_utility_rate_list = []
    self.bw_utility_rate_list_c = []
    self.suc_list = []
    self.suc_list_c = []
    self.x_axis = []
    #self.x_axis = []
    self.length_of_links = 0 #for test
    self.test_count = 0
  def init_all():
    self.number_of_vn = 0
  def start(self):
    self.current_time = 0
    next_t = next_time(1 / self.virtual_network_arrival_time_interval)
    ##
    ## TEST START ##
    total_cpu_resource = 0
    for node in self.substrate_network.nodes():
      total_cpu_resource = total_cpu_resource + \
      self.substrate_network.node[node]['cpu_capacity']
    print 'total cpu resource: ', total_cpu_resource
    print 'total cpu resource: ', \
           self.get_total_cpu_resources(self.substrate_network)
    total_bw_resource = 0
    for edge in self.substrate_network.edges():
      total_bw_resource = total_bw_resource + \
          self.substrate_network.edge[edge[0]][edge[1]]['bandwidth_capacity']
    print 'total_bw_resource: ', total_bw_resource
    print 'total_bw_resource: ', \
          self.get_total_bandwidth_resources(self.substrate_network)
    ## TEST END ##
    for t in range(0, self.time_length):
      self.current_time = t
      self.virtual_network_depart(self.mapped_virtual_network_list) 
      self.virtual_network_depart_c(self.mapped_virtual_network_list_c)
      if self.current_time >= next_t:
        ## A virtual network arrived
        self.number_of_vn = self.number_of_vn + 1
        next_t = self.current_time + \
                 next_time(1/self.virtual_network_arrival_time_interval)

        ## ******* Create a new virtual network ******* ##
        vm_name = 'VN' + str(self.number_of_vn)
        numer_of_virtual_network_nodes = random.randint(2, 20)
        virtual_network =  \
        self.generate_virtual_network_with_lifetime(numer_of_virtual_network_nodes, 
                                                    0.5, 
                                                    0, 
                                                    vm_name, 
                                                    [1, 50], 
                                                    [1, 50], 
                                                    self.virtual_network_lifetime)
        virtual_network.depart_time = virtual_network.lifetime + self.current_time
        ## ******* Create a new virtual network END **** ##

        ## ******* Mapping VN to SN ************************ ##
        (vn_sn_node_map, vn_sn_link_map, sn_tmp) = \
        self.mapping(self.substrate_network, virtual_network)

        (vn_sn_node_map_c, vn_sn_link_map_c, sn_tmp_c) = \
        self.mapping_c(self.substrate_network_c, virtual_network)
        ## ******* Mapping VN to SN END ******************** ##
        
        if sn_tmp is not None:
          ## Mapped success
          self.substrate_network = copy.deepcopy(sn_tmp)       ## Update substrate network
          self.suc_count = self.suc_count + 1
          self.mapped_virtual_network_list.append(virtual_network)
          self.virtual_network_node_mapping[virtual_network.graph['name']] = vn_sn_node_map
          self.virtual_network_link_mapping[virtual_network.graph['name']] = vn_sn_link_map
          print self.suc_count

        else:
          self.reject_count = self.reject_count + 1
          self.cpu_utility_rate_rejected_list.append(self.get_total_cpu_resources(self.substrate_network) * 1.00 / \
              total_cpu_resource)
          self.bw_utility_rate_rejected_list.append(self.get_total_cpu_resources(self.substrate_network) * 1.00 / \
              total_cpu_resource)

        if sn_tmp_c is not None:
          ## Mapped success
          self.substrate_network_c = copy.deepcopy(sn_tmp_c)       ## Update substrate network
          self.suc_count_c = self.suc_count_c + 1
          self.mapped_virtual_network_list_c.append(virtual_network)
          self.virtual_network_node_mapping_c[virtual_network.graph['name']] = \
                                                                  vn_sn_node_map_c
          self.virtual_network_link_mapping_c[virtual_network.graph['name']] = \
                                                                  vn_sn_link_map_c

        else:
          self.reject_count_c = self.reject_count_c + 1
          self.cpu_utility_rate_rejected_list_c.append(self.get_total_cpu_resources(self.substrate_network_c) * 1.00 / \
              total_cpu_resource)
          self.bw_utility_rate_rejected_list_c.append(self.get_total_cpu_resources(self.substrate_network_c) * 1.00 / \
              total_cpu_resource)



       
        rr = self.reject_count * 1.0 / self.number_of_vn
        sr = self.suc_count * 1.0 / self.number_of_vn
        self.suc_list.append(sr)
        self.reject_list.append(rr)
        self.cpu_utility_rate_list.append(self.get_total_cpu_resources(self.substrate_network) * 1.00 / \
              total_cpu_resource)
        self.bw_utility_rate_list.append(self.get_total_bandwidth_resources(self.substrate_network) * \
              1.00 / total_bw_resource)

        rr_c = self.reject_count_c * 1.0 / self.number_of_vn
        sr_c = self.suc_count_c * 1.0 / self.number_of_vn
        self.suc_list_c.append(sr_c)
        self.reject_list_c.append(rr_c)
        self.cpu_utility_rate_list_c.append(self.get_total_cpu_resources(self.substrate_network_c) * 1.00 / \
              total_cpu_resource)
        self.bw_utility_rate_list_c.append(self.get_total_bandwidth_resources(self.substrate_network_c) * \
              1.00 / total_bw_resource)



        self.x_axis.append(self.current_time)
        # print sr 
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
    self.substrate_network_c = copy.deepcopy(self.substrate_network)
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
  def get_total_cpu_resources(self, g):
    total_cpu_resource = 0
    for node in g.nodes():
      total_cpu_resource = total_cpu_resource + \
          g.node[node]['cpu_capacity']
    return total_cpu_resource
  def get_total_bandwidth_resources(self, g):
    total_bw_resource = 0
    for edge in g.edges():
      total_bw_resource = total_bw_resource + \
          g.edge[edge[0]][edge[1]]['bandwidth_capacity']
    return total_bw_resource
  def virtual_network_depart(self, vn_list):
    for vn in vn_list:
      if self.current_time > vn.depart_time:
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
            self.substrate_network.edge[sn_edges[i]][sn_edges[i + 1]]['bandwidth_capacity'] = \
            self.substrate_network.edge[sn_edges[i]][sn_edges[i + 1]]['bandwidth_capacity'] + bw
  def virtual_network_depart_c(self, vn_list):
    for vn in vn_list:
      if self.current_time > vn.depart_time:
        vn_list.remove(vn)
        node_mapping = self.virtual_network_node_mapping_c[vn.graph['name']]
        link_mapping = self.virtual_network_link_mapping_c[vn.graph['name']]
        for node in vn.nodes():
          self.substrate_network_c.node[node_mapping[node]]['cpu_capacity'] = \
          self.substrate_network_c.node[node_mapping[node]]['cpu_capacity'] + \
                                            vn.node[node]['cpu_capacity']
        for edge in vn.edges():
          bw = vn.edge[edge[0]][edge[1]]['bandwidth_capacity']
          sn_edges = link_mapping[edge]
          for i in range(0, len(sn_edges) - 1):
            self.substrate_network_c.edge[sn_edges[i]][sn_edges[i + 1]]['bandwidth_capacity'] = \
            self.substrate_network_c.edge[sn_edges[i]][sn_edges[i + 1]]['bandwidth_capacity'] + bw
  def mapping_c(self, sn, vn):
    return self.mapping_algorithm_c.mapping(sn, vn)


if __name__ == '__main__':
  grc = GRC(0.00001, 0.85)
  rtk = RTK()
  #vne = VNE(grc)
  vne = VNE(grc,rtk)
  print vne.generate_substrate_network(100, 100, 0.11, 1, 'Substrate_Network',
                                      [50, 100], [50, 100])

  vne.start()
  rr = vne.reject_list
  sr = vne.suc_list
  cr = vne.cpu_utility_rate_list
  br = vne.bw_utility_rate_list
  crr = vne.cpu_utility_rate_rejected_list
  brr = vne.bw_utility_rate_rejected_list

  rr_c = vne.reject_list_c
  sr_c = vne.suc_list_c
  cr_c = vne.cpu_utility_rate_list_c
  br_c = vne.bw_utility_rate_list_c
  crr_c = vne.cpu_utility_rate_list_c
  brr_c = vne.bw_utility_rate_list_c

  """
  plt.plot(vne.x_axis,rr)
  plt.plot(vne.x_axis,rr_c, 'r--')
  plt.show()
 
 
  plt.plot(vne.x_axis,sr)
  plt.plot(vne.x_axis,sr_c, 'r--')
  plt.show()
 
  plt.plot(vne.x_axis,cr)
  plt.plot(vne.x_axis,cr_c, 'r--')
  plt.show()

  plt.plot(vne.x_axis,br)
  plt.plot(vne.x_axis,br_c, 'r--')
  plt.show()
  """

  f = open('grc_rejected_rate.txt','w')
  for i in rr:
    f.write(str(i) + '\n')
  f.close()

  f = open('grc_accepted_rate.txt','w')
  for i in sr:
    f.write(str(i) + '\n')
  f.close()
 
  f = open('rtk_rejected_rate.txt', 'w')
  for i in rr_c:
    f.write(str(i) + '\n')
  f.close()

  f = open('rtk_accepted_rate.txt', 'w')
  for i in sr_c:
    f.write(str(i) + '\n')
  f.close()

  f = open('grc_cpu_utility_rate.txt','w') 
  for i in cr:
    f.write(str(i) + '\n')
  f.close()

  f = open('rtk_cpu_utility_rate.txt','w')
  for i in cr_c:
    f.write(str(i) + '\n')
  f.close()

  f = open('grc_bw_utility_rate.txt','w') 
  for i in br:
    f.write(str(i) + '\n')
  f.close()

  f = open('rtk_cpu_utility_rate.txt','w')
  for i in br_c:
    f.write(str(i) + '\n')
  f.close()

  f = open('grc_cpu_utility_rate_rejected.txt', 'w')
  for i in crr:
    f.write(str(i) + '\n')
  f.close()

  f = open('grc_bw_utility_rate_rejected.txt', 'w')
  for i in brr:
    f.write(str(i) + '\n')
  f.close()

  f = open('rtk_cpu_utility_rate_rejected.txt', 'w')
  for i in crr_c:
    f.write(str(i) + '\n')
  f.close()

  f = open('rtk_bw_utility_rate_rejected.txt', 'w')
  for i in brr_c:
    f.write(str(i) + '\n')
  f.close()

  import os, datetime
  import subprocess
  path = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
  path = './result/' + path
  subprocess.call(['mkdir', path])
  subprocess.call("mv ./*.txt " + path, shell=True)



