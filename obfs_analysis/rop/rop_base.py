import sys, os

fn = sys.argv[1]    # binary file name
c = sys.argv[2]     # iteration count
path = sys.argv[3]  # binary file directory
bin_dir = sys.argv[4]


os.system("python ROPgadget --binary %s > %s/rop_%d.data" % (bin_dir + '/' + fn, path, 0))
for i in range(1, int(c)+1):
    os.system("python ROPgadget --binary %s > %s/rop_%d.data" % (bin_dir + '/obfs_' + str(i), path, i))

res = []

res_f0 = path + '/rop_0.data'


def read_rop_data(data_path):
    with open(data_path, 'r') as data_f:
        lines = data_f.readlines()
        lines = lines[2:]
        num_gadgets = int(lines[-1].split(':')[-1])
        # get the gadgets and opcodes sequence map
        lines = lines[:-2]
        addr_opcodes_map = dict()
        for l in lines:
            tmp = l.split(' : ')
            rop_addr = int(tmp[0], 16)
            rop_instrs = tmp[1].split(';')
            opcodes = []
            for instr in rop_instrs:
                opcodes.append(instr.split()[0])
            addr_opcodes_map[rop_addr] = opcodes
        return num_gadgets, addr_opcodes_map


total0, addrs0 = read_rop_data(res_f0)

res = []

for i in range(1, int(c)+1):
    res_f1 = path + '/rop_' + str(i) + '.data'
    total1, addrs1 = read_rop_data(res_f1)
    count = 0
    for addr in addrs0.keys():
        if addr in addrs1.keys() and len(addrs0[addr]) == len(addrs1[addr]):
            # compare the opcode sequence
            same_seq = True
            for idx in range(len(addrs0[addr])):
                if addrs0[addr][idx] != addrs1[addr][idx]:
                    same_seq = False
                    break
            if not same_seq:
                count += 1
        else:
            count += 1

    res.append(str((count/float(total0))*100) + "\n")

with open(path + "/rop_base.res", "w") as f:
    f.writelines(res)

