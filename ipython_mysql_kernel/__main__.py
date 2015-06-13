from IPython.kernel.zmq.kernelapp import IPKernelApp
from .kernel import MySQLKernel
IPKernelApp.launch_instance(kernel_class=MySQLKernel)
