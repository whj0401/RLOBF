"""
Main module
"""

import glob
import os
import shutil
import sys
from argparse import ArgumentParser, RawTextHelpFormatter

from termcolor import colored

import config


def process(filepath, instrument=False, fexclude=''):
    """
    Start file processing
    :param filepath: path to executable
    :param instrument: True to apply instrumentation
    :param fexclude: path to file of symbol exclusions
    :return: True if everything ok
    """
    import init
    import traceback
    from postprocess import compile_process
    from disasm import main_discover, func_addr

    print "Starting to process binary '" + filepath + "'"
    try:

        func_addr.func_addr(filepath, 0, fexclude)

        os.system(config.strip + ' ' + filepath)
        main_discover.main_discover(filepath)

        init.main(filepath, instrument)
        if not os.path.isfile("final.s"): return False

        with open('final_data.s', 'a') as f:
            f.write('\n.section .eh_frame\n')
            with open('eh_frame_split.info') as eh: f.write(eh.read())
            f.write('\n.section .eh_frame_hdr\n')
            with open('eh_frame_hdr_split.info') as eh: f.write(eh.read())
        with open('final.s', 'a') as f:
            with open('final_data.s', 'r') as fd: f.write(fd.read())
            if instrument: f.write('\n\n'.join(map(lambda e: e['plain'].instrdata, config.instrumentors)))

        compile_process.main(filepath)
        if instrument:
            for worker in config.instrumentors:
                worker['main'].aftercompile()
        if compile_process.reassemble() != 0: return False

    except Exception as e:
        print e
        traceback.print_exc()
        return False

    return True


def check(filepath, assumptions, gccopt='', excludedata='', instrument=False):
    """
    Perform basic check on analyzed executable and set configuration values
    :param filepath: path to executable
    :param assumptions: list of assumption codes
    :param gccopt: additional options for the compiler
    :param excludedata: path to file of address exclusions
    :param instrument: True if instrumentation enabled
    :return: True if everything ok
    """
    if not assumptions: assumptions = []

    if not os.path.isfile(filepath):
        sys.stderr.write("Cannot find input binary\n")
        return False

    if len(excludedata) != 0 and not os.path.isfile(excludedata):
        sys.stderr.write("File with exclusions not found\n")
        return False

    for f in glob.glob('*'): os.remove(f)

    if os.path.dirname(filepath) != os.getcwd():
        shutil.copy(filepath, '.')

    os.system('file ' + filepath + ' > elf.info')
    config.setup(filepath, gccopt, excludedata, instrument)

    if config.is_lib:
        sys.stderr.write("Uroboros doesn't support shared libraries\n")
        return False

    # if assumption three is utilized, then input binary should be unstripped.
    if ('3' in assumptions or instrument) and not config.is_unstrip:
        print colored('Warning:', 'yellow'), 'binary is stripped, function boundaries evaluation may not be precise'

    return True


def set_assumption (assumptions):
    """
    Save assumptions to file
    2 -> assumption two: fix data section starting address
    3 -> assumption three: function starting address + jump table
    :param assumptions: list of assumptions codes
    :return: True if everything ok
    """
    if not assumptions:
        with open('assumption_set.info', 'w') as f:
            f.write('1\n')
    else:
        chk = (i in ['2', '3'] for i in assumptions)
        if any(chk) == False:
            print "assumption undefined!"
            print "accepted assumptions: 2 for assumption two and 3 for assumption three"
            return False
        with open('assumption_set.info', 'w') as f:
            f.write(' '.join(assumptions) + '\n')
    return True


def set_diversification(d, iter):
    if d not in config.all_diver_modes:
        assert False, 'unrecognizible diversification mode %d for iteration %d' % (d, iter)
    config.diversification_mode = d
    print 'set diversification mode %d for iteration %d' % (d, iter)
    os.system('echo %d > mode' % d)


def reset_diversification():
    config.diversification_mode = 0


def main():
    """
    Main function
    """
    p = ArgumentParser(formatter_class=RawTextHelpFormatter)
    p.add_argument("binary", help="path to the input binary")
    p.add_argument("-o", "--output", help="destination output file")
    p.add_argument("-g", "--instrument", action='store_true', help="apply instrumentations to output")
    p.add_argument("-a", "--assumption", action="append",
                   help='''this option configures three addtional assumption,
note that two basic assumptions and addtional assumption one
(n-byte alignment) are set by default,
while assumption two and three need to be configured. For example, setting
assumption two and three: -a 2 -a 3''')
    p.add_argument("-gcc", "--gccopt", action="store", default="", help="A string of additional arguments for GCC")
    p.add_argument("-ex", "--exclude", default="", help="""File where each line is either a single value which must not be
a label or an address range of data section to exclude from symbol search""")
    p.add_argument("-fex", "--functionexclude", default="", help="File with a list of symbols not representing functions")
    p.add_argument("--version", action="version", version="Uroboros 0.2b")

    p.add_argument('-i', '--iteration', type=int, help='the number of disassemble-diversify-reassemble iterations')
    p.add_argument('-d', '--diversification', type=int, action='append',
                   help='the sequence of diversification for every iteration \n' + config.diversification_description)

    args = p.parse_args()
    filepath = os.path.realpath(args.binary)
    outpath = os.path.realpath(args.output) if args.output is not None else None
    exclude = os.path.realpath(args.exclude) if len(args.exclude) > 0 else ''
    fexclude = os.path.realpath(args.functionexclude) if len(args.functionexclude) > 0 else ''

    num_iteration = args.iteration
    if num_iteration is None or num_iteration <= 0:
        num_iteration = 1

    diversifications = args.diversification
    if diversifications is None:
        diversifications = [0]
    while len(diversifications) < num_iteration:
        diversifications.append(diversifications[-1])

    abs_path = os.path.dirname(os.path.abspath(__file__))

    for i in range(1, num_iteration + 1):
        workdir = abs_path + '/workdir_' + str(i)
        if not os.path.isdir(workdir):
            os.mkdir(workdir)

        print colored(('iteration %d dir:' + workdir) % i, 'green')
        os.chdir(workdir)
        # run after setting the work directory
        set_diversification(diversifications[i - 1], i)

        if check(filepath, args.assumption, args.gccopt, exclude, args.instrument) and set_assumption(args.assumption):
            if process(os.path.basename(filepath), args.instrument, fexclude):
                os.system('strip a.out')
                print colored("Processing %d succeeded" % i, "blue")
                if outpath is not None:
                    shutil.copy('a.out', outpath + '_' + str(i) + '_mode_' + str(config.diversification_mode))
                    shutil.copy('a.out', outpath)
                # change source file path
                filepath = workdir + '/a.out'
            else:
                print colored("Processing %d failed" % i, "red")
                exit(1)
        reset_diversification()


if __name__ == "__main__":
    main()
