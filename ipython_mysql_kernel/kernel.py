#!/usr/bin/env python

from IPython.kernel.zmq.kernelbase import Kernel

class MySQLKernel(Kernel):
    implementation = 'MySQL'
    implementation_version = '0.1'
    language = 'mysql'
    language_version = '0.1'
    language_info = {'mimetype': 'text/plain'}
    banner = "MySQL kernel"

    def __init__(self, **kwargs):
        Kernel.__init__(self, **kwargs)

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
        if not silent:
            stream_content = {'name': 'stdout', 'text': code}
            self.send_response(self.iopub_socket, 'stream', stream_content)

        return {'status': 'ok',
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }

if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=MySQLKernel)
