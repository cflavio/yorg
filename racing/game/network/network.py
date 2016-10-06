'''This module provides an abstraction for network components.'''
from panda3d.core import QueuedConnectionManager, QueuedConnectionReader, \
    ConnectionWriter, NetDatagram
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator


class AbsNetwork(object):
    '''This class models an abstract network component.'''

    def __init__(self, reader_cb):
        self.c_mgr = QueuedConnectionManager()
        self.c_reader = QueuedConnectionReader(self.c_mgr, 0)
        self.c_writer = ConnectionWriter(self.c_mgr, 0)
        args = (self.tsk_reader, 'connection reader', -40)
        self.reader_tsk = taskMgr.add(*args)
        self.reader_cb = reader_cb

    def send(self, data_lst, receiver=None):
        '''Sends a packet.'''
        datagram = PyDatagram()
        dct_types = {bool: 'B', int: 'I', float: 'F', str: 'S'}
        datagram.addString(''.join(dct_types[type(part)] for part in data_lst))
        dct_meths = {
            bool: datagram.addBool, int: datagram.addInt64,
            float: datagram.addFloat64, str: datagram.addString}
        map(lambda part: dct_meths[type(part)](part), data_lst)
        self._actual_send(datagram, receiver)

    def tsk_reader(self, task):
        '''The reader task.'''
        if not self.c_reader.dataAvailable():
            return task.cont
        datagram = NetDatagram()
        if not self.c_reader.getData(datagram):
            return task.cont
        _iter = PyDatagramIterator(datagram)
        dct_meths = {'B': _iter.getBool, 'I': _iter.getInt64,
                     'F': _iter.getFloat64, 'S': _iter.getString}
        msg_lst = [dct_meths[c]() for c in _iter.getString()]
        self.reader_cb(msg_lst, datagram.getConnection())
        return task.cont

    def register_cb(self, callback):
        '''Registers a callback.'''
        self.reader_cb = callback

    def destroy(self):
        '''Destroys the component'''
        taskMgr.remove(self.reader_tsk)
