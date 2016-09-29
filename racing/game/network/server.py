'''This module provides the server for a network application.'''
from panda3d.core import QueuedConnectionListener, PointerToConnection, \
    NetAddress
from .network import AbsNetwork


class Server(AbsNetwork):
    '''This class models the server.'''

    def __init__(self, reader_cb, connection_cb):
        AbsNetwork.__init__(self, reader_cb)
        self.connection_cb = connection_cb
        self.c_listener = QueuedConnectionListener(self.c_mgr, 0)
        self.connections = []
        self.tcp_socket = self.c_mgr.openTCPServerRendezvous(9099, 1000)
        self.c_listener.addConnection(self.tcp_socket)
        args = (self.tsk_listener, 'connection listener', -39)
        self.listener_tsk = taskMgr.add(*args)
        eng.log_mgr.log('the server is up')

    def tsk_listener(self, task):
        '''The listener task.'''
        if self.c_listener.newConnectionAvailable():
            rendezvous = PointerToConnection()
            net_address = NetAddress()
            new_connection = PointerToConnection()
            args = (rendezvous, net_address, new_connection)
            if self.c_listener.getNewConnection(*args):
                new_connection = new_connection.p()
                self.connections.append(new_connection)
                self.c_reader.addConnection(new_connection)
                self.connection_cb(net_address.getIpString())
                msg = 'received a connection from ' + net_address.getIpString()
                eng.log_mgr.log(msg)
        return task.cont

    def _actual_send(self, datagram, receiver):
        '''Sends a datagram.'''
        dests = self.connections
        if receiver is not None:
            dests = [cln for cln in self.connections if cln == receiver]
        for cln in dests:
            self.c_writer.send(datagram, cln)

    def destroy(self):
        AbsNetwork.destroy(self)
        map(lambda cln: self.c_reader.removeConnection(cln), self.connections)
        self.c_mgr.closeConnection(self.tcp_socket)
        taskMgr.remove(self.listener_tsk)
        eng.log_mgr.log('the server has been destroyed')
