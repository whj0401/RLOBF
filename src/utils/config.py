#CONTAINER_ID = '984f8a6e2a41'
import json


LOG_ON = True

prj_dir = None

ps_threshold = 32

uroboros_env = None

OBJDUMP = 'objdump -d '

instrs_size = 400
max_ops_len = 50000
div_modes_size = 10

ida_pro_path = None

bindiff_path = None

perf_path = None


with open('./config.json') as _jf:
    _j = json.load(_jf)
    prj_dir = _j['prj_dir']
    uroboros_env = _j['uroboros_env']
    ida_pro_path = _j['ida_pro_path']
    bindiff_path = _j['bindiff_path']
    perf_path = _j['perf_path']


