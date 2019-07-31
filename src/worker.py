import json
import os

import _judger

import config as _conf
from constants import *
from problem import Problems


class CompileErrorException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class LanguageNotSupportedException(Exception):
    def __init__(self):
        super().__init__()


worker_config = json.load(open('worker.json', 'r'))


class Worker:

    def __init__(self, work_dir, code, lang, prob_id):
        self.work_dir = work_dir
        self.code = code
        self.lang = lang

        self.prob_id = prob_id
        if lang not in worker_config.keys():
            raise LanguageNotSupportedException()
        self.config = worker_config[self.lang]
        self.source_path, self.output_path = None, None

    def compile(self):
        """
        :return: code_path, output_path
        """
        self.source_path = os.path.join(
            self.work_dir, self.config['source_name'])
        self.output_path = os.path.join(
            self.work_dir, self.config['output_name'])
        compile_output_path = os.path.join(self.work_dir, 'compiler.out')

        with open(self.source_path, 'w') as f:
            f.write(self.code)

        if self.config['compile']['command'] is None:
            return self.source_path, self.source_path
        command = self.config['compile']['command'].format(
            source_path=self.source_path,
            output_path=self.output_path,
            output_dir=self.work_dir
        ).split(' ')

        res = _judger.run(
            max_cpu_time=self.config['compile']["max_cpu_time"],
            max_real_time=self.config['compile']["max_real_time"],
            max_memory=self.config['compile']["max_memory"],
            max_stack=128 * 1024 * 1024,
            max_output_size=1024 * 1024,
            max_process_number=_judger.UNLIMITED,
            exe_path=command[0],
            input_path=self.source_path,
            output_path=compile_output_path,
            error_path=compile_output_path,
            args=command[1::],
            env=["PATH=" + os.getenv("PATH")],
            seccomp_rule_name=None,
            log_path=_conf.JUDGE_LOG,
            uid=0, gid=0
        )
        if res['result'] != RESULT_SUCCESS:
            if os.path.exists(compile_output_path):
                with open(compile_output_path, 'r') as f:
                    error = f.read().strip()
                os.remove(compile_output_path)
                raise CompileErrorException(error or json.dumps(res))
        os.remove(compile_output_path)
        return self.source_path, self.output_path

    def execute(self):
        """
        :return: list of results, problem case count
        """
        problem = Problems.query.filter_by(id=self.prob_id).first()
        cases = json.loads(problem.cases)
        limits = json.loads(problem.limits)
        command = self.config['execute']['command'].format(
            source_path=self.source_path,
            output_path=self.output_path,
            output_dir=self.work_dir,
            max_memory=limits["max_memory"]//1024,
        ).split(' ')
        weight = self.config['execute']['weight']
        assert (type(weight) == dict)
        for key in limits.keys():
            if key in weight.keys() and type(weight[key]) == int:
                if weight[key] < 0 or limits[key] == -1:
                    limits[key] = -1
                else:
                    limits[key] *= weight[key]
        res = []
        for i in range(problem.case_cnt):
            with open(os.path.join(self.work_dir, 'input'), 'w') as f:
                f.write(cases[i]['input'])
            with open(os.path.join(self.work_dir, 'output'), 'w') as f:
                f.write(cases[i]['output'])
            res.append(_judger.run(
                max_cpu_time=limits["max_cpu_time"],
                max_real_time=limits["max_real_time"],
                max_memory=limits["max_memory"],
                max_stack=limits["max_stack"],
                max_output_size=limits["max_output_size"],
                max_process_number=limits["max_process_number"],
                exe_path=command[0],
                input_path=os.path.join(self.work_dir, 'input'),
                output_path=os.path.join(self.work_dir, 'program_output'),
                error_path=os.path.join(self.work_dir, 'program_error_output'),
                args=command[1::],
                env=["PYTHONIOENCODING=UTF-8"],
                seccomp_rule_name=None,
                log_path=_conf.JUDGE_LOG,
                uid=0, gid=0
            ))
            if res[-1]['result'] == RESULT_SUCCESS:
                with open(os.path.join(self.work_dir, 'program_output'), 'r') as f:
                    res[-1]['result'] = self.compare_output(
                        f.read(), cases[i]['output'])
            if res[-1]['result'] != RESULT_SUCCESS:
                break
        return res, problem.case_cnt

    @staticmethod
    def compare_output(got_output, output):
        output = output.strip(' \n')
        got_output = got_output.strip(' \n')
        result = RESULT_SUCCESS
        if output != got_output:
            if output.replace('\n', '').replace(' ', '') \
                    == got_output.replace('\n', '').replace(' ', ''):
                result = RESULT_PRESENTATION_ERROR
            else:
                result = RESULT_WRONG_ANSWER
        return result

    def destroy(self):
        self._destroy(self.work_dir)

    @staticmethod
    def _destroy(directory):
        for i in os.listdir(directory):
            if os.path.isdir(os.path.join(directory, i)):
                Worker._destroy(os.path.join(directory, i))
                os.rmdir(os.path.join(directory, i))
            else:
                os.remove(os.path.join(directory, i))
        os.rmdir(directory)
