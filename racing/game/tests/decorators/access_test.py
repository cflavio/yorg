from unittest import TestCase
from ya2.decorators.access import auto_properties


@auto_properties
class Access(object):

    def __init__(self):
        self.__x = 5
        self.__y = 40

    def get_double_x(self):
        return self.__x * 2

    def get_half_y(self):
        return self.__y / 2

    def set_quota(self, val):
        self.__quota = val + '%'

    def get_quota(self):
        return 'quota: ' + self.__quota


class AccessTests(TestCase):

    def test_read_attrs(self):
        acc = Access()
        self.assertEqual(acc.double_x, 10)
        self.assertEqual(acc.half_y, 20)
        acc.quota = '50'
        self.assertEqual(acc.quota, 'quota: 50%')
