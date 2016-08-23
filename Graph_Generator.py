import os
import subprocess

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
    file_path = './graph_set/' + name + '.gb'
  else:
    file_path = './graph_set/' + 'tmp.gb'
  f = open(file_path, 'wb')
  f.write(l1 + '\n')
  f.write(l2 + '\n')
  f.close()
  return file_path



#if '__name__' == '__main__':
create_script_file(10,10,0.5,0,'Substrate')
