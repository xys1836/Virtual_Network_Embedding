import math
import random

def next_time(rateParameter):
  return -math.log(1.0 - random.random()) / rateParameter
"""
p = nextTime(1/10.0)
cT = 0
nT = cT + p
sumT = 0
c = 0
for i in range(0,100000):
  ct = i
  if ct >= nT:
    c = c + 1
    p = nextTime(1/10.0)
    print p
    nT = ct + p 
    sumT = sumT + p
print sumT/c
"""
