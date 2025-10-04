import unittest
from unittest.mock import patch, MagicMock

from multi_tool.vpn_router.vpn import ip_detector as ipd

class TestIPDetector(unittest.TestCase):
    @patch('multi_tool.vpn_router.vpn.ip_detector.subprocess')
    def test_enable_virtual_device_linux(self, mock_subproc):
        # Simulate non-Windows
        with patch('multi_tool.vpn_router.vpn.ip_detector.os.name', 'posix'):
            mock_subproc.run = MagicMock()
            ipd.enable_virtual_device()
            mock_subproc.run.assert_called()

    @patch('multi_tool.vpn_router.vpn.ip_detector.subprocess')
    def test_restore_dns(self, mock_subproc):
        with patch('multi_tool.vpn_router.vpn.ip_detector.os.name', 'posix'):
            mock_subproc.run = MagicMock()
            ipd.restore_dns()
            mock_subproc.run.assert_called()

if __name__ == '__main__':
    unittest.main()
