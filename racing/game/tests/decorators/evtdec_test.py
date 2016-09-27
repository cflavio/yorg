from direct.fsm.FSM import FSM
from panda3d.core import loadPrcFileData
from unittest import TestCase
from ya2.decorators.evtdec import evt_dec
from ya2.engine import Engine


class AFsm(FSM):

    def __init__(self):
        FSM.__init__(self, 'a fsm')

    def enterStateA(self):
        self.flag = True

    def enterStateB(self):
        self.flag_b = True


class A:

    def __init__(self):
        self.fsm = AFsm()
        self = evt_dec(self, self.fsm)

    def destroy(self):
        self.flag_destroy = True


class B(A):
    pass


class C(B):

    def evt_message_a(self):
        self.flag_a = True

    def evt_message_b(self, val):
        self.flag_b = val

    def evt_message_c(self, val0, val1):
        self.flag_c0 = val0
        self.flag_c1 = val1

    def evt_message_d__State_a(self):
        self.flag_d = True

    def evt_message_e__State_b(self):
        self.flag_e = True

    def evt_message_f__State_a__State_c(self):
        self.flag_f = True

    def evt_message_g__not_State_c(self):
        self.flag_g = True

    def evt_message_h__not_State_c__State_d(self):
        self.flag_h = True

    def evt_message_i__State_e(self):
        self.flag_i = True

    def evt_message_i__State_f(self):
        self.flag_i2 = True

    def evt_message_z(self):
        self.flag_z = True


class EvtDecTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')

    def tearDown(self):
        self.engine.destroy()

    def test_evt(self):
        c = C()
        self.engine = Engine()

        self.assertRaises(AttributeError, getattr, c, 'flag_a')
        self.engine.messenger.send('message_a')
        self.assertTrue(c.flag_a)

        self.assertRaises(AttributeError, getattr, c, 'flag_b')
        self.engine.messenger.send('message_b', [42])
        self.assertEqual(c.flag_b, 42)

        self.assertRaises(AttributeError, getattr, c, 'flag_c0')
        self.assertRaises(AttributeError, getattr, c, 'flag_c1')
        self.engine.messenger.send('message_c', [43, '44'])
        self.assertEqual(c.flag_c0, 43)
        self.assertEqual(c.flag_c1, '44')

        self.engine.messenger.send('message_d')
        self.assertRaises(AttributeError, getattr, c, 'flag_d')
        c.fsm.request('State_a')
        self.engine.messenger.send('message_d')
        self.assertTrue(c.flag_d)

        self.engine.messenger.send('message_e')
        self.assertRaises(AttributeError, getattr, c, 'flag_e')
        c.fsm.request('State_b')
        self.engine.messenger.send('message_e')
        self.assertTrue(c.flag_e)

        self.engine.messenger.send('message_f')
        self.assertRaises(AttributeError, getattr, c, 'flag_f')
        c.fsm.request('State_c')
        self.engine.messenger.send('message_f')
        self.assertTrue(c.flag_f)

        self.engine.messenger.send('message_g')
        self.assertRaises(AttributeError, getattr, c, 'flag_g')
        c.fsm.request('State_d')
        self.engine.messenger.send('message_g')
        self.assertTrue(c.flag_g)

        self.engine.messenger.send('message_h')
        self.assertRaises(AttributeError, getattr, c, 'flag_h')
        c.fsm.request('State_e')
        self.engine.messenger.send('message_h')
        self.assertTrue(c.flag_h)

        self.engine.messenger.send('message_i')
        self.assertTrue(c.flag_i)
        self.assertRaises(AttributeError, getattr, c, 'flag_i2')

        c2 = C()
        self.engine.messenger.send('message_d')
        self.assertTrue(c.flag_d)
        self.assertRaises(AttributeError, getattr, c2, 'flag_d')
        c2.fsm.request('State_a')
        self.engine.messenger.send('message_d')
        self.assertTrue(c2.flag_d)

        self.assertRaises(AttributeError, getattr, c, 'flag_destroy')
        c.destroy()
        self.assertTrue(c.flag_destroy)
        self.engine.messenger.send('message_z')
        self.assertRaises(AttributeError, getattr, c, 'flag_z')


class EmptyInitDestroy:

    def __init__(self):
        self = evt_dec(self)

    def fun(self):
        self.flag_fun = True


class EvtEmptyTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')

    def tearDown(self):
        self.engine.destroy()

    def test_evt(self):
        self.engine = Engine()
        empty = EmptyInitDestroy()
        self.assertRaises(AttributeError, getattr, empty, 'flag_fun')
        empty.fun()
        self.assertTrue(empty.flag_fun)


class NoFsm:

    def __init__(self):
        self = evt_dec(self)

    def evt_message_a(self):
        self.flag_a = True


class EvtNoFsmTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')

    def tearDown(self):
        self.engine.destroy()

    def test_evt(self):
        self.engine = Engine()
        no_fsm = NoFsm()

        self.engine.messenger.send('message_a')
        self.assertTrue(no_fsm.flag_a)


class Message:
    pass


class AClass:

    def __init__(self):
        self = evt_dec(self)

    def evt_message_a(self):
        self.flag_a = True

    def evt_Message(self, msg):
        self.field_a = msg.x


class EvtMsgTests(TestCase):

    def setUp(self):
        loadPrcFileData('', 'window-type none')

    def tearDown(self):
        self.engine.destroy()

    def test_evt(self):
        self.engine = Engine()

        a_class = AClass()
        self.assertRaises(AttributeError, getattr, a_class, 'flag_a')
        self.engine.messenger.send('message_a')
        self.assertTrue(a_class.flag_a)

        e = Message()
        e.x = 42
        self.assertRaises(AttributeError, getattr, a_class, 'field_a')
        self.engine.messenger.send(e)
        self.assertEqual(a_class.field_a, 42)
