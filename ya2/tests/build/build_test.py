from os import getcwd, makedirs
from os.path import basename
from shutil import rmtree
from unittest import TestCase

from ya2.build.build import InsideDir, get_files, get_size, exec_cmd, set_path


class BuildTests(TestCase):

    def setUp(self):
        makedirs('test_get_files/a')
        makedirs('test_get_files/b')
        makedirs('test_get_files/c')
        with open('test_get_files/a/c.ext1', 'w') as f:
            f.write('0123456789')
        open('test_get_files/a/d.ext2', 'w')
        with open('test_get_files/b/e.ext2', 'w') as f:
            f.write('0123456789')
        open('test_get_files/b/f.ext3', 'w')
        open('test_get_files/c/g.ext2', 'w')

    def tearDown(self):
        rmtree('test_get_files')

    def test_inside_dir(self):
        self.assertNotEqual(basename(getcwd()), 'tests')
        with InsideDir('ya2/tests'):
            self.assertEqual(basename(getcwd()), 'tests')
        self.assertNotEqual(basename(getcwd()), 'tests')

    def test_get_files(self):
        files = get_files(['ext2'], 'c')
        self.assertSetEqual(set(files),
                            set(['./test_get_files/a/d.ext2',
                                 './test_get_files/b/e.ext2']))

    def test_get_size(self):
        self.assertEqual(get_size('test_get_files'), 20)

    def test_exec_cmd(self):
        self.assertEqual(exec_cmd('echo abc'), 'abc\n\n')

    def test_path(self):
        self.assertEqual(set_path('abc'), 'abc/')
        self.assertEqual(set_path('abc/'), 'abc/')
