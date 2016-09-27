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
        self.reader_tsk = taskMgr.add(self.tsk_reader, 'connection reader',
                                      -40)
        self.reader_cb = reader_cb

    @staticmethod
    def _format(data_lst):
        '''Formats a packet.'''
        dct_types = {bool: 'B', int: 'I', float: 'F', str: 'S'}
        return ''.join(dct_types[type(part)] for part in data_lst)

    def send(self, data_lst, receiver=None):
        '''Sends a packet.'''
        datagram = PyDatagram()
        datagram.addString(self._format(data_lst))
        dct_meths = {bool: datagram.addBool, int: datagram.addInt64,
                     float: datagram.addFloat64, str: datagram.addString}
        for part in data_lst:
            dct_meths[type(part)](part)
        self._actual_send(datagram, receiver)

    def tsk_reader(self, task):
        '''The reader task.'''
        if self.c_reader.dataAvailable():
            datagram = NetDatagram()
            if self.c_reader.getData(datagram):
                iterator = PyDatagramIterator(datagram)
                _format = iterator.getString()
                dct_meths = {'B': iterator.getBool, 'I': iterator.getInt64,
                             'F': iterator.getFloat64, 'S': iterator.getString}
                msg_lst = [dct_meths[c]() for c in _format]
                self.reader_cb(msg_lst, datagram.getConnection())
        return task.cont

    @property
    def is_active(self):
        '''Is the component active?'''
        return self.reader_tsk.is_alive()

    def register_cb(self, callback):
        '''Registers a callback.'''
        self.reader_cb = callback

    def destroy(self):
        '''Destroys the component'''
        taskMgr.remove(self.reader_tsk)
