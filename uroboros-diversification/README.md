# Uroboros
#### Infrastructure for Reassembleable Disassembling and Transformation

### Fork motivation

This fork is made with the idea of extending this technique to ARM Thumb executables. In such process, the OCaml core has been completely rewritten in Python.

To this date the rewritten tool has been tested to work on the following executables: bzip, gzip, BLAKE2, Himeno benchmark, dcraw (with statically linked libjpeg and liblcms, ARM requires assumption 3), FLAC encoder (with statically linked libFLAC), dolfyn, OPUS encoder (with statically linked libopus, ARM requires assumption 3).

## Installation

Uroboros uses the following utilities (version numbers are in line with what was used during development, older releases may work as well):

| Tool        | Version   |
|:------------|----------:|
| python      | 2.7       |
| objdump     | ≥2.22     |
| readelf     | ≥2.22     |
| awk         | ≥3.18     |
| libcapstone | 3.0.5-rc3 |

and the following python packages (available through `pip` repositories):

| Package     | Version |
|:------------|--------:|
| capstone    | ≥3.0.4  |
| termcolor   | ≥1.1.0  |
| pyelftools  | ≥0.24   |

## Build

Uroboros is now completely written in Python on the `allpy` branch. You don't need to build anything. However, you may want to modify some values in `config.py` to match your system configuration. Also, the parser, though recognising a large number of operators, is not complete; in case invalid operator exceptions are raised, these can be added to the right set in `Types.py`.

## Usage

Uroboros supports 64-bit and 32-bit ELF x86 executables and, experimentally, also Thumb2 ARM binaries.
To use Uroboros for disassembling:

```bash
 $> python uroboros.py path_to_bin
```

The disassembled output can be found in the `workdir` directory, named `final.s`. Uroboros will also assemble it back into an executable, `a.out`.

The startup Python script provides the following options:

* `-o output`

  This option allows to specify an output path for the reassembled binary.

* `-g`

  Apply instrumentations. New instrumentations can be implemented by creating subpackages in the `instrumentation` package. These **must** contain at least two modules (see the `example` package):

  * a module having the same name of the package with a function named `perform`, accepting a list of instructions and a list of function objects and returning the instrumented list of instructions, and a function named `aftercompile`. The first is invoked just after the symbol reconstruction phase is completed, while the latter allows further modifications after the code has already been adjusted for compilation;
  * a module named `plaincode` which must contain three string variables name `beforemain`, `aftercode` and `instrdata`. These are respectively inserted at the beginning of the main function, at the end of the `.text` section and at the end of the source file.

  Instrumentations are applied in alphabetical order, the task of preventing interference among different instrumentations is left to the user. If multiple instrumentations have been implemented but only a subset has to be used, adding their package names as strings in the `instrumentors` list of the `config.py` file will allow only these to be loaded and executed (in this case the order is the one specified by the user).

    Instrumentation against ROP attacks using an adaptation of the technique described in [\[2\]](#gfree) is already available in this repository.

* `-gcc "parameters"`

  String of additional arguments a user may want to pass to the compiler.

* `-ex exclusions_file`

  Allows to specify a file containing on each line either a hexadecimal value to exclude from symbol search inside the code or an address ranges, in the format `hexaddress-hexaddress`, of the data sections which will be skipped when searching for pointers.

* `-fex function_exclusion_file`

  In case a non-stripped binary is being analysed, allows to specify a file containing a list of symbol which should not be considered functions.

* `-a assumption_number`

  This option configures the three symbolization assumptions proposed in the original Uroboros paper [\[1\]](#uroboros). Note that in the current version, the first assumption (**n-byte alignment**) are set by default. The other two assumptions can be set by users.

  Assumption two reqires to put data sections (.data, .rodata and .bss) to its original starting addresses. Linker scripts can be used during reassembling (`gcc -T ld_script.sty final.s`). Users may write their own linker script, some examples are given at `ld_script` folder.

  Assumption three requires to know the function starting addresses. To obtain this information, Uroboros can take unstripped binaries as input. The function starting address information is obtained from the input, which is then stripped before disassembling.

  These assumptions can also be used at the same time (`python uroboros.py path_to_bin -a 3 -a 2`)

* `-i iteration_number`

  This option configures the number of iterations for disassembling -> diversification -> reassembling

* `-d diversification_mode`

  This option configures the mode of diversification. We provide 10 sorts of diversification mode currently. The diversification_mode must be from 0 to 10(inclusive), and every iteration with only one diversification_mode.

  Note: 1.The iteration whose diversification_mode is 10 must be used the the last iteration; otherwise the following iteration will meet error! 2.The 10th diversification is not compatible with 64bit ELFs currently.

  These modes can be used as (`python uroboros.py path_to_bin -i 5 -d 1 -d 2 -d 3 -d 4 -d 10`).

  Please use `-h` or `--help` to read the description of diversification modes.

## Stuff it would be nice to do
* **More testing on real applications and, after that, even more testing.**
* **Change the way data flow is managed**: now, to ease the debugging process, most of the data is passed along via file, which implies a lot of unnecessary IO operations.


<a name="uroboros">[1]</a> [Reassembleable Disassembling](https://www.usenix.org/conference/usenixsecurity15/technical-sessions/presentation/wang-shuai), by Shuai Wang, Pei Wang, and Dinghao Wu. In Proceedings of the 24th USENIX Security Symposium, Washington, D.C., August 12-14. 2015.

<a name="gfree">[2]</a> [G-Free: defeating return-oriented programming through gadget-less binaries](https://doi.org/10.1145/1920261.1920269), by Onarlioglu Kaan, Leyla Bilge, Andrea Lanzi, Davide Balzarotti, and Engin Kirda. In Proceedings of the 26th Annual Computer Security Applications Conference, pp. 49-58. ACM, 2010."
