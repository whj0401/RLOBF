import sys, os

lines = []

path = sys.argv[1]

print path

with open(path) as f:
	lines = f.readlines()




knot_count = 0

is_first_func = True

label_addr = {}
jmp_addr = {}

def knot():
	global label_addr
	global jmp_addr
	global knot_count
	print "label addr dic: "
	print label_addr
	print "jmp addr dic: "
	print jmp_addr

	jmp_addr_num = {}

	for k, v in jmp_addr.items():
		v1 = v+":"
		if v1 in label_addr:
			addr = label_addr[v1] # let it crash if inter-procedure jmp occurs
			jmp_addr_num[k] = addr
		else:
			print v1

	print jmp_addr_num

	for k1, v1 in jmp_addr_num.items():
		for k2, v2 in jmp_addr_num.items():
			if k1 < k2 and k2 < v1 and v1 < v2: # situation 1
				knot_count = knot_count + 1
				print "knot : " + str(knot_count)
				print str(k1) + " " + str(v1) + " " + str(k2) + " " + str(v2)
			if k2 < k1 and k1 < v2 and v2 < v1: # situation 2
				knot_count = knot_count + 1
				print "knot : " + str(knot_count)
				print str(k1) + " " + str(v1) + " " + str(k2) + " " + str(v2)

for i in xrange(0, len(lines)):
	l = lines[i]
	items = l.split()
	if len(items) > 0:
		if "global" in items[0]:
			if is_first_func:
				#take record
				is_first_func = False
			else:
				knot()
				label_addr = {}
				jmp_addr = {}
		if len(items) == 1 and "loc_" in items[0]:
			# identify a new label
			nl = lines[i+1]
			addr = nl.split()[0] #let it crash if wrong
			label_addr[items[0]] = addr
		if len(items) == 3 and items[1].startswith('j'):
			des = items[2]
			source = items[0]
			jmp_addr[source] = des

print "############"
print "knot : " + str(knot_count/2)
