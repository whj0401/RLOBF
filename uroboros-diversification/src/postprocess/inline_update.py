
def find_symbol (l, symbols):
    return filter(lambda s: s in l, symbols)


def main():
    with open('final.s') as f:
        lines = f.readlines()

    # all the symbols found in inlined function, provided by
    # func_inline_diversify.ml
    with open('inline_symbols.txt') as f:
        symbols = f.readlines()

    # get rid of space; newline and ":"
    symbols = map(lambda s : s.replace(":",""), symbols)
    symbols = map(lambda s : s.strip(), symbols)
    symbols = filter(lambda s : s.strip(), symbols)

    symbols = set(symbols)

    #print symbols

    inline_region = False
    cur_fun_index = 0
    cur_fun_name = ""

    # the ret instruction is substituted as:
    #   ret/retn  ==> pop ecx; jmp ecx
    #   EAX, ECX and EDX are caller save registers.
    #   EBP, EBX, EDI and ESI are callee save registers.

    for i in range(len(lines)):
        l = lines[i]
        l = l.strip()
        if "_next_inline" in l and "push" in l :
            #begin of function
            cur_fun_name =  "inline_"+str(cur_fun_index)
            if inline_region == True:
                # possibly inline function nested; abort
                print "inline function nested"
                assert(False)
            else:
                #print "find inline function : " + l
                inline_region = True
        elif "_next_inline:" in l:
            if inline_region == False:
                # possibly inline function lost; abort
                print "inline function lost"
                assert(False)
            else:
                inline_region = False
                cur_fun_index += 1
        elif inline_region == True:
            items = l.split()  # @UnusedVariable
            found_symbols = find_symbol(l, symbols)
            # if "ret" == l:
            #     l = "pop %ecx\njmp *%ecx"
            #elif len(items) == 2 and find_symbol(l) != "":
            if len(found_symbols) != 0:
                for r in found_symbols:
                    r1 = r + "_" + cur_fun_name
                    l = l.replace(r, r1)
            else:
                l = l

        lines[i] = l + "\n"

    with open('final.s', 'w') as f:
        f.writelines(lines)
