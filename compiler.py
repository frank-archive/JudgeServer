import json
import os

import _judger

import config as _conf


class CompileErrorException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


compile_config = json.load(open('compiler.json', 'r'))


def compile_code(path, code, lang):
    '''
    returns: code_path, output_path
    '''
    if lang not in compile_config.keys():
        raise CompileErrorException('Language Not Supported')
    config = compile_config[lang]
    source_path = os.path.join(path, config['source_name'])
    output_path = os.path.join(path, config['output_name'])
    compile_output_path = os.path.join(path, 'compiler.out')
    command = config['compile']['command'].format(
        source_path=source_path,
        output_path=output_path,
        output_dir=path
    ).split(' ')
    with open(source_path, 'w') as f:
        f.write(code)
    res = _judger.run(
        max_cpu_time=config['compile']["max_cpu_time"],
        max_real_time=config['compile']["max_real_time"],
        max_memory=config['compile']["max_memory"],
        max_stack=128 * 1024 * 1024,
        max_output_size=1024 * 1024,
        max_process_number=_judger.UNLIMITED,
        exe_path=command[0],
        input_path=source_path,
        output_path=compile_output_path,
        error_path=compile_output_path,
        args=command[1::],
        env=["PATH=" + os.getenv("PATH")],
        seccomp_rule_name=None,
        log_path=_conf.JUDGE_LOG,
        uid=0, gid=0
    )
    if res['result'] != _judger.RESULT_SUCCESS:
        if os.path.exists(compile_output_path):
            with open(compile_output_path, 'r') as f:
                error = f.read().strip()
            os.remove(compile_output_path)
            raise CompileErrorException(error or json.dumps(res))
    os.remove(compile_output_path)
    return source_path, output_path
