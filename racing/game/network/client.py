'''This module provides the client for a network application.'''
from .network import AbsNetwork


class ClientError(Exception):
    '''The client can not connect.'''
    pass


class Client(AbsNetwork):
    '''This class models the client.'''

    def __init__(self, reader_cb, server_address):
        AbsNetwork.__init__(self, reader_cb)
        self.conn = self.c_mgr.openTCPClientConnection(server_address, 9099,
                                                       3000)
        if self.conn:
            self.c_reader.addConnection(self.conn)
        else:
            raise ClientError
        eng.log_mgr.log('the client is up')

    def _actual_send(self, datagram, receiver):
        self.c_writer.send(datagram, self.conn)

    def destroy(self):
        AbsNetwork.destroy(self)
        self.c_mgr.closeConnection(self.conn)
        eng.log_mgr.log('the client has been destroyed')
