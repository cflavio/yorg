from direct.showbase.DirectObject import DirectObject
from panda3d.core import loadPrcFileData
from unittest import TestCase
from ya2.decorators.evtdec import evt_dec
from ya2.engine import Engine


class Msg:
    pass


class Accepter(DirectObject):

    def __init__(self):
        self = evt_dec(self)

    def evt_MsgStr(self, arg):
        self.val_str = arg

    def evt_Msg(self, cls, arg):
        self.val_cls = arg


class SenderTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')

    def tearDown(self):
        self.engine.destroy()

    def test_sender(self):
        self.engine = Engine()
        acc = Accepter()
        msg = Msg()
        self.engine.messenger.send('MsgStr', [42])
        self.engine.messenger.send(msg, [43])
        self.assertEqual(acc.val_str, 42)
        self.assertEqual(acc.val_cls, 43)
