#!/usr/bin/env python

import json
import os
import signal

from IPython.kernel.zmq.kernelbase import Kernel
import pexpect

class MySQLKernel(Kernel):
    """MySQLKernel for IPython
       this program use pexpect to interact with the mysql process
       mysql configs are read from ~/.ipython/mysql_config.json
       default configs are
            mysql_config = {
               "user"     : "root",
               "host"     : "127.0.0.1",
               "port"     : "3306",
               "charset"  : "utf8"
            }
        you can set "password" in mysql_config.json if needed
    """
    implementation = 'MySQL'
    implementation_version = '0.1'
    language = 'mysql'
    language_version = '0.1'
    language_info = {
            'mimetype': 'text/plain',
            'name': 'mysql',
            'file_extension': '.sql',
            }
    banner = "MySQL kernel"

    mysql_setting_file = os.path.join(os.path.expanduser("~"),
                                     ".ipython/mysql_config.json")
    mysql_config = {
       "user"     : "root",
       "host"     : "127.0.0.1",
       "port"     : "3306",
       "charset"  : "utf8"
    }

    def __init__(self, prompt="mysql> ", **kwargs):
        Kernel.__init__(self, **kwargs)
        self.prompt = prompt
        self._start_process()

    def _start_process(self):
        if os.path.exists(self.mysql_setting_file):
            with open(self.mysql_setting_file,"r") as f:
                self.mysql_config.update(json.load(f))

        # make childprocess interuptible by SIGINT
        sig = signal.signal(signal.SIGINT, signal.SIG_DFL)
        try:
            if "password" in self.mysql_config:
                self.ch = pexpect.spawn(
                        'mysql -A -h {host} -P {port} -u {user} -p'.format(**self.mysql_config))
            else:
                self.ch = pexpect.spawn(
                        'mysql -A -h {host} -P {port} -u {user}'.format(**self.mysql_config))
        finally:
            signal.signal(signal.SIGINT, sig)

        if self.ch.echo:
            self.ch.setecho(False)
            self.ch.waitnoecho()

        if "password" in self.mysql_config:
            self.ch.expect('Enter password: ')
            self.ch.sendline(self.mysql_config["password"])

        self.ch.expect(self.prompt)

    def do_execute(self, code, silent, store_history=True,
                   user_expressions=None, allow_stdin=False):

        if not code.strip():
            return {'status': 'ok',
                    'execution_count': self.execution_count,
                    'payload': [],
                    'user_expressions': {}}

        mes = ""
        for c in code.split("\n"):
            c = c.strip()
            if len(c) > 0:
                if c[0] == "#":
                    #skip comment
                    continue
                mes += c + " "
        mes = mes.strip()
        if mes[-1] != ";":
            mes += ";"

        interrupted = False
        try:
            self.ch.sendline(mes)
            self.ch.expect(self.prompt)
            output = self.ch.before
        except KeyboardInterrupt:
            self.sh.sendintr()
            self.ch.sendintr()
            self.ch.expect(self.prompt)
            interrupted = True
            output = self.sh.before
        except pexpect.EOF:
            output = self.ch.before + 'Restarting Process...'
            self._start_process()

        res = output.decode(self.mysql_config["charset"])
        # remove echo string
        # TODO: can't I disable echo?
        if res.find(mes) == 0:
            res = res[len(mes):]

        if not silent:
            stream_content = {'name': 'stdout', 'text': res}
            self.send_response(self.iopub_socket, 'stream', stream_content)

        if interrupted:
            return {'status': 'abort', 'execution_count': self.execution_count}

        return {'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }

if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=MySQLKernel)
