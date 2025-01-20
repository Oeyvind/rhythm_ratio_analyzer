
import os
os.chdir('C:\\Projects\efx_experiments\\rhythm_ratio_analyzer\\rhythm_ratio_analyzer')
print(os.getcwd())
f = open('weights_run1.txt', 'r')
d = {}
for line in f:
  l = line.split(', avg:')
  avg, m = l[1].split(', min:')
  d.setdefault(eval(l[0]), [eval(avg), eval(m)])
print(len(list(d.keys())))

d_purged = {}
avgs = []
mins = []
for k,v in d.items():
  avgs.append(v[0])
  mins.append(v[1])
  #if v[0] > 0.3:
  #if v[1] > 0.12:
  if (v[0] > 0.35) and (v[1] > 0.15):
    d_purged[k] = v
print(len(list(d_purged.keys())))
print(f'avgs min max: {min(avgs), max(avgs)}')
print(f'mins min max: {min(mins), max(mins)}')
for k,v in d_purged.items():
  print(k,v)

# compare weights where only one of the values differ
# find the avg and min confidence for these
# expect the highest value to give better confidence
def differ_by_two(l1, l2):
    return sum(1 for i,j in zip(l1, l2) if i!=j) == 2