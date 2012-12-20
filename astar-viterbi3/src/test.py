import sys
import subprocess

line = sys.stdin.readlines()
print reduce(lambda x,y:x+y,map(lambda y:filter(lambda x:x!='' and x or None,y.strip().split(" ")),line))

#cmd = ["java", "AStar", "3.91866175645", "1.60445652255", "1.68243006494"]
cmd = ['java', 'AStar', '3.91866175645', '1.60445652255', '1.68243006494']
result = subprocess.check_output(cmd)
print result
