import idaapi
import idc
from idautils import *

res = []
# -----------------------------------------------------------------------
# Using raw IDAAPI
def raw_main(p=True):
    global res
    # find .text section startEA first
    #text_startEA = None
    #for s in Segments():
    #    if SegName(s) == '.text':
    #        text_startEA = s
    #        break
    #if text_startEA is None:
    #    text_startEA = 0
    #f = idaapi.get_func(text_startEA)
    f = idaapi.get_next_func(0)
    fc = idaapi.FlowChart(f)

    while f:
        funcea = f.startEA
        fn = GetFunctionName(funcea)
        # if "Pl" in fn:
        #     funcaddr = f.startEA
        #     f = idaapi.get_next_func(funcaddr)
        #     continue

        q = idaapi.qflow_chart_t("The title", f, 0, 0, idaapi.FC_PREDS)
        res.append("##############################\n")
        for n in xrange(0, q.size()):
            b = q[n]
            if p:
                res.append("%x - %x [%d]:\n" % (b.startEA, b.endEA, n))

            for ns in xrange(0, q.nsucc(n)):
                res.append("SUCC:  %d->%d\n" % (n, q.succ(n, ns)))
            pred_set = set()
            for ns in xrange(0, q.npred(n)):
                res.append("PRED:  %d->%d\n" % (n, q.pred(n, ns)))
                pred_set.add(q.pred(n, ns))

            if q.nsucc(n) == 0:
                # this is a block with no successors
                last_insn = None
                for h in Heads(b.startEA, b.endEA):
                    last_insn = h
                if last_insn is None:
                    continue
                insn = DecodeInstruction(last_insn)
                if idaapi.is_ret_insn(insn):
                    continue
                disasm_str = GetDisasm(last_insn)
                if 'abort' in disasm_str or 'exit' in disasm_str or 'hlt' in disasm_str or '___stack_chk_fail' in disasm_str or '___assert_fail' in disasm_str:
                    continue
                if idaapi.is_indirect_jump_insn(insn):
                    # if this function ends with an indirect jump, it means ida failed to
                    # determine the successors. We treat all blocks in this function as possible successors
                    #with open('wierd_jump.txt', 'a') as tmp_f:
                    #    tmp_f.write(disasm_str + '\n')
                    for tn in xrange(0, q.size()):
                        res.append("SUCC:  %d->%d\n" % (n, tn))
                        if tn not in pred_set:
                            res.append("PRED:  %d->%d\n" % (tn, n))
                elif idaapi.is_call_insn(insn):
                    # if this function ends with a call (not something like abort), it is somewhat wierd.
                    # do not solve this temporarily
                    #with open('wierd_call.txt', 'a') as tmp_f:
                    #    tmp_f.write(disasm_str + '\n')
                    for tn in xrange(0, q.size()):
                        res.append("SUCC:  %d->%d\n" % (n, tn))
                        if tn not in pred_set:
                            res.append("PRED:  %d->%d\n" % (tn, n))

        funcaddr = f.startEA
        f = idaapi.get_next_func(funcaddr)

if __name__ == '__main__':
    raw_main(True)
    output_path = idc.ARGV[1]
    with open(output_path, "w") as f:
        f.writelines(res)
    qexit()

