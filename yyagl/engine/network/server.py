from panda3d.core import QueuedConnectionListener, PointerToConnection, \
    NetAddress
from .network import AbsNetwork


class Server(AbsNetwork):

    def __init__(self, mdt):
        AbsNetwork.__init__(self, mdt)
        self.c_listener = None
        self.tcp_socket = None
        self.connection_cb = None
        self.listener_tsk = None
        self.connections = []

    def start(self, reader_cb, connection_cb):
        AbsNetwork.start(self, reader_cb)
        self.connection_cb = connection_cb
        self.c_listener = QueuedConnectionListener(self.c_mgr, 0)
        self.connections = []
        self.tcp_socket = self.c_mgr.openTCPServerRendezvous(9099, 1000)
        self.c_listener.addConnection(self.tcp_socket)
        args = (self.tsk_listener, 'connection listener', -39)
        self.listener_tsk = taskMgr.add(*args)
        eng.log_mgr.log('the server is up')

    def tsk_listener(self, task):
        if not self.c_listener.newConnectionAvailable():
            return task.cont
        net_address = NetAddress()
        new_connection = PointerToConnection()
        args = (PointerToConnection(), net_address, new_connection)
        if not self.c_listener.getNewConnection(*args):
            return task.cont
        new_connection = new_connection.p()
        self.connections.append(new_connection)
        self.c_reader.addConnection(new_connection)
        self.connection_cb(net_address.getIpString())
        msg = 'received a connection from ' + net_address.getIpString()
        eng.log_mgr.log(msg)
        return task.cont

    def _actual_send(self, datagram, receiver):
        dests = [cln for cln in self.connections if cln == receiver] \
            if receiver else self.connections
        map(lambda cln: self.c_writer.send(datagram, cln), dests)

    def destroy(self):
        AbsNetwork.destroy(self)
        map(self.c_reader.removeConnection, self.connections)
        self.c_mgr.closeConnection(self.tcp_socket)
        taskMgr.remove(self.listener_tsk)
        eng.log_mgr.log('the server has been destroyed')
