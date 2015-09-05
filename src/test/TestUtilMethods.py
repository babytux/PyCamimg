"""
Test util methods

@author: babytux
"""
import unittest
from pycamimg.util.IOUtils import IOUtils


class TestIOMethods(unittest.TestCase):
    """Test drives IO methods"""

    def testGetDrives(self):
        """Test print drives"""
        p = IOUtils().getDrives();
        self.assertGreater(len(p), 0, 'Test does not pass the drives')


    def testFail(self):
        self.fail('Always fail')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    suite = unittest.TestLoader().loadTestsFromTestCase(TestIOMethods)
    unittest.TextTestRunner(verbosity=2).run(suite)