from panda3d.core import QueuedConnectionManager, QueuedConnectionReader, \
    ConnectionWriter, NetDatagram
from direct.distributed.PyDatagram import PyDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from ...gameobject.gameobject import Colleague


class AbsNetwork(Colleague):

    def __init__(self, mdt):
        Colleague.__init__(self, mdt)
        self.c_mgr = None
        self.c_reader = None
        self.c_writer = None
        self.reader_cb = None

    def start(self, reader_cb):
        self.c_mgr = QueuedConnectionManager()
        self.c_reader = QueuedConnectionReader(self.c_mgr, 0)
        self.c_writer = ConnectionWriter(self.c_mgr, 0)
        eng.event.attach(self.tsk_reader, 1)
        self.reader_cb = reader_cb

    def send(self, data_lst, receiver=None):
        datagram = PyDatagram()
        dct_types = {bool: 'B', int: 'I', float: 'F', str: 'S'}
        datagram.addString(''.join(dct_types[type(part)] for part in data_lst))
        dct_meths = {
            bool: datagram.addBool, int: datagram.addInt64,
            float: datagram.addFloat64, str: datagram.addString}
        map(lambda part: dct_meths[type(part)](part), data_lst)
        self._actual_send(datagram, receiver)

    def tsk_reader(self):
        if not self.c_reader.dataAvailable():
            return
        datagram = NetDatagram()
        if not self.c_reader.getData(datagram):
            return
        _iter = PyDatagramIterator(datagram)
        dct_meths = {'B': _iter.getBool, 'I': _iter.getInt64,
                     'F': _iter.getFloat64, 'S': _iter.getString}
        msg_lst = [dct_meths[c]() for c in _iter.getString()]
        self.reader_cb(msg_lst, datagram.getConnection())

    def register_cb(self, callback):
        self.reader_cb = callback

    @property
    def is_active(self):
        return self.tsk_reader in [obs[0] for obs in eng.event.observers]

    def destroy(self):
        eng.event.detach(self.tsk_reader)
