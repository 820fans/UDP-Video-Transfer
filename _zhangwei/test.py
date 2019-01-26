from queue import Queue, PriorityQueue

class Pack(object):
	def __init__(self, idx, ctime):
		self.idx = idx
		self.ctime = ctime

	def __lt__(self, other):
		return self.ctime > other.ctime 

Q = PriorityQueue(128)
Q.put(Pack(2, 1548397750814))
Q.put(Pack(1, 1548397750871))

print(Q.get().ctime)
print(Q.get().ctime)

arr = []
for i in range(10):
	arr.append(None)
print(arr[3])