import sys, os

fn = sys.argv[1]    # binary file name
c = sys.argv[2]     # iteration count
path = '.'  # binary file directory
bin_dir = sys.argv[3]

os.system("ROPgadget --binary %s > %s/rop_%d.data" % (bin_dir + '/' + fn, path, 0))
for i in range(1, int(c)+1):
    os.system("ROPgadget --binary %s > %s/rop_%d.data" % (bin_dir + '/obfs_' + str(i), path, i))

res = []

res_f0 = path + '/rop_0.data'

lines0 = []
with open(res_f0) as f:
    lines0 = f.readlines()

lines0 = lines0[2:]

total0 = lines0[-1].split(':')[1] # get the total number of rop gadgets
total0 = int(total0.strip())

lines0 = lines0[:-2]

addrs0 = []
for l in lines0:
    addrs0.append(l.split(':')[0])


res = []

for i in range(1, int(c)+1):
    res_f1 = path + '/rop_' + str(i) + '.data'

    lines1 = []
    with open(res_f1) as f:
        lines1 = f.readlines()

    lines1 = lines1[2:]

    total1 = lines1[-1].split(':')[1] # get the total number of rop gadgets
    total1 = int(total1.strip())

    lines1 = lines1[:-2]

    addrs1 = []
    for l in lines1:
        addrs1.append(l.split(':')[0])

    count = 0
    for addr in addrs0:
        if addr in addrs1:
            continue
        else:
            count += 1

    res.append(str((count/float(total0))*100) + "\n")

with open(path + "/rop_base.res", "w") as f:
    f.writelines(res)
