# coding=utf-8
import bdb
import sys
import inspect
import zmq
import pickle
import traceback
from IPython.core.debugger import Pdb as IPdb
from IPython.core.getipython import get_ipython


class RapunzelPdb(IPdb, object):

    def __init__(self, port=5555, breakpoints=None):

        super(RapunzelPdb, self).__init__()
        self.clear_all_breaks()
        self._set_breakpoints(breakpoints)
        self._zmq_context = zmq.Context()
        self._zmq_socket = self._zmq_context.socket(zmq.REQ)
        self._zmq_socket.connect('tcp://localhost:{}'.format(port))
        self._zmq_socket.send_pyobj({'type': 'pdb_start'})
        self.post_mortem = False
       
    def clear_all_breaks(self):
        
        # Adapted from SpyderPDB.set_spyder_break_points. For some reason you
        # need to work hard to avoid breakpoints from becoming persistent
        super(RapunzelPdb, self).clear_all_breaks()
        for bp in bdb.Breakpoint.bpbynumber:
            if bp:
                bp.deleteMe()
        bdb.Breakpoint.next = 1
        bdb.Breakpoint.bplist = {}
        bdb.Breakpoint.bpbynumber = [None]
        
    def _set_breakpoints(self, breakpoints):
        
        if not breakpoints:
            return
        for break_path, lines in breakpoints.items():
            for line in lines:
                self.set_break(break_path, line + 1)
                
    def _transmit_workspace(self, frame):
        
        # # See transparent_jupyter_widget
        workspace_variables = frame.f_locals
        workspace_variables.update(frame.f_globals)
        workspace_variables = ({
            key: (
                repr(val),
                val.__class__.__name__,
                (
                    val.shape if hasattr(val, 'shape')
                    else len(val) if hasattr(val, '__len__')
                    else None
                )
            )
            for key, val in workspace_variables.items()
            if not key.startswith(u'_') and
            key not in ('In', 'Out') and
            not callable(val) and
            not inspect.isclass(val) and
            not inspect.ismodule(val)
        })
        try:
            self._zmq_socket.send_pyobj({
                'type': 'pdb_frame',
                'path': frame.f_code.co_filename,
                'line': frame.f_lineno,
                'workspace': workspace_variables
            })
        except zmq.error.ZMQError:
            pass
        try:
            self._zmq_socket.recv()
        except zmq.error.ZMQError:
            pass
        
    def close(self):
        
        self._zmq_socket.send_pyobj({'type': 'pdb_stop'})
        self._zmq_socket.close()

    def interaction(self, frame, traceback):
        
        self._transmit_workspace(frame)
        super(RapunzelPdb, self).interaction(frame, traceback)

    def postcmd(self, stop, line):
        
        self._transmit_workspace(self.curframe)
        return super(RapunzelPdb, self).postcmd(stop, line)


def runfile(path):

    with open(path) as f:
        code = f.read()
    bytecode = compile(code, path, 'exec')
    exec(bytecode, {})


def rpdb(path, port=5555, breakpoints=None):

    print('''
* Enter `c` (continue) to start execution
* Enter `q` (quit) to quit
* Enter `?` for help
''')
    # Ideally we'd set the first breakpoint to line 1 and then execute until
    # there. However, this is tricky to accomplish.
    # if not breakpoints or all(not lines for lines in breakpoints.values()):
    #     print('Settig first breakpoint at line 1')
    #     breakpoints = {path: [0]}
    pdb = RapunzelPdb(port, breakpoints)
    try:
        pdb.run('runfile({})'.format(repr(path)))
    except Exception as e:
        tb = sys.exc_info()[2]
        traceback.print_exception(type(e), e, tb)
        pdb.reset()
        pdb.post_mortem = True
        while tb.tb_next:  # Get the highest frame (where the error occurred)
            tb = tb.tb_next
        pdb.interaction(tb.tb_frame, tb)
    finally:
        pdb.close()  # Close connection also on crash
