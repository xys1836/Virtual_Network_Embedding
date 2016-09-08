from graph_generator import generate_substrate_network
from graph_generator import generate_virtual_network
from global_resource_capacity_algorithm import greedy_node_mapping
from global_resource_capacity_algorithm import shortest_path_based_link_mapping
from global_resource_capacity_algorithm import grc_mapping
from poisson_process import next_time
sn = generate_substrate_network(100, 100, 0.11, 0, 
                                'Substrate_Network', 
                                [50, 100], [50, 100])

vn = generate_virtual_network(10, 0.5, 0, 
                              'Virtual_Network', 
                              [1,50], [10,80])
"""
(suc, vn_sn_map) = greedy_node_mapping(sn,vn,0.00001,0.85)
a = []
b = []
c = {}
d = 0
if suc:
  print 'suc'
  print vn_sn_map
else:
  print 'fail'
for e in sn.edges():
  a.append(sn.edge[e[0]][e[1]]['bandwidth_capacity'])
shortest_path_based_link_mapping(sn, vn, vn_sn_map)
print '**********'
for e in sn.edges():
  b.append(sn.edge[e[0]][e[1]]['bandwidth_capacity'])
for i in range(0, len(a)):
  if a[i] is not b[i]:
    c[i] = [a[i], b[i]]
    d = d + 1
print 'diff'
print c
print d
"""
(suc, vn_sn_node_map, vn_sn_link_map) = grc_mapping(sn, vn, 0.00001, 0.85)
print "mapping sucessful"
print suc
print 'virtual node mapping'
print vn_sn_node_map
print 'virtual link mapping'
print vn_sn_link_map





