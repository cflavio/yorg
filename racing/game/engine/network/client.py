from .network import AbsNetwork


class ClientError(Exception):
    pass


class Client(AbsNetwork):

    def __init__(self, mdt):
        AbsNetwork.__init__(self, mdt)
        self.conn = None

    def start(self, reader_cb, server_address):
        AbsNetwork.start(self, reader_cb)
        args = (server_address, 9099, 3000)
        self.conn = self.c_mgr.openTCPClientConnection(*args)
        if not self.conn:
            raise ClientError
        self.c_reader.addConnection(self.conn)
        eng.log_mgr.log('the client is up')

    def _actual_send(self, datagram, receiver):
        self.c_writer.send(datagram, self.conn)

    def destroy(self):
        AbsNetwork.destroy(self)
        self.c_mgr.closeConnection(self.conn)
        eng.log_mgr.log('the client has been destroyed')
