from network import AbsNetwork


class Server(AbsNetwork):

    def __init__(self, reader_cb, connection_cb):
        AbsNetwork.__init__(self, reader_cb)
        self.connection_cb = connection_cb
        self.c_listener = QueuedConnectionListener(self.c_mgr, 0)
        self.connections = []
        self.tcp_socket = self.c_mgr.openTCPServerRendezvous(9099, 1000)
        self.c_listener.addConnection(self.tcp_socket)
        self.listener_tsk = taskMgr.add(self.tsk_listener, 'connection listener', -39)
        eng.log_mgr.log('the server is up')

    def tsk_listener(self, task):
        if self.c_listener.newConnectionAvailable():
            rendezvous = PointerToConnection()
            net_address = NetAddress()
            new_connection = PointerToConnection()
            if self.c_listener.getNewConnection(rendezvous, net_address, new_connection):
                new_connection = new_connection.p()
                self.connections.append(new_connection)
                self.c_reader.addConnection(new_connection)
                self.connection_cb(net_address.getIpString())
                eng.log_mgr.log('received a connection from ' + net_address.getIpString())
        return task.cont

    def _actual_send(self, datagram, receiver):
        if receiver is not None:
            for client in self.connections:
                if client == receiver:
                    self.c_writer.send(datagram, client)
        else:
            for client in self.connections:
                self.c_writer.send(datagram, client)

    def destroy(self):
        AbsNetwork.destroy(self)
        for client in self.connections:
            self.c_reader.removeConnection(client)
        self.c_mgr.closeConnection(self.tcp_socket)
        taskMgr.remove(self.listener_tsk)
        eng.log_mgr.log('the server has been destroyed')
