from graph_generator import generate_substrate_network
from graph_generator import generate_virtual_network
from global_resource_capacity_algorithm import greedy_node_mapping

sn = generate_substrate_network(100, 100, 0.11, 0, 
                                'Substrate_Network', 
                                [50, 100], [50, 100])

vn = generate_virtual_network(10, 0.5, 0, 
                              'Virtual_Network', 
                              [1,50], [1,50])

(blocked, vn_sn_map) = greedy_node_mapping(sn,vn,0.00001,0.85)

if blocked:
  print 'suc'
else:
  print 'fail'
