import sys, os

lines = []

path = sys.argv[1]

print(path)

with open(path) as f:
#with open(path+'func.txt') as f:
	lines = f.readlines()

#	we have to process three kinds of string exp
#		new function:   global FUNC_NAME
#		call instr:		   call    XXX
#		jump instr:		[jmp; jnz...] XXX
#
#JMP | JNE | JE | JB | JNAE | JNP
#              | JC | JNB | JAE | JNC | JBE | JNA
#              | JA | JNBE | JL | JNGE | JGE | JNL | JLE
#              | JNG | JG | JNLE | JS | JNS | JP
#

jump_list = ('jmp', 'jne', 'je', 'jb', 'jnae', 'jnp', 'jc', 'jnb', 'jae', 'jnc', 'jbe', 'jna',
			'ja', 'jnbe', 'jl', 'jnge', 'jge', 'jnl', 'jle', 'jng', 'jg', 'jnle', 'js', 'jns', 'jp')

func_c = 0
call_c = 0
jump_c = 0

#c_func = ""
res = []

for l in lines:
    items = l.split()
    if len(items) > 1:
        if "global" in items[0]:
            #c_func = items[1]
            func_c = func_c + 1
            res = []
        elif "call" in items[1]:
            print(l)
            d = items[2]
            if d in res:
                continue
                #call_c = call_c + 1
            else:
                res.append(d)
                call_c = call_c + 1

func_num = func_c
cg_edge = call_c

print("func_num : " + str(func_num))
print("cg_edge : " + str(cg_edge))
