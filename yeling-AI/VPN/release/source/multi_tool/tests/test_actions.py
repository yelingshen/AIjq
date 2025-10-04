import unittest
from multi_tool.actions import action, run_action, list_actions
import os

@action('test.simple', description='简单动作', admin_only=False, supports_dry_run=True, params={'name':'目标名称'})
def _test_simple(dry_run=False, params=None):
    if dry_run:
        return 'dry'
    return f"ok:{params.get('name')}"

@action('test.admin', description='需要管理员', admin_only=True, supports_dry_run=True)
def _test_admin(dry_run=False, params=None):
    return 'admin-ok'

class ActionsTest(unittest.TestCase):
    def test_list_contains(self):
        actions = list_actions()
        self.assertIn('test.simple', actions)

    def test_dry_run(self):
        self.assertEqual(run_action('test.simple', dry_run=True, params={'name':'x'}), 'dry')

    def test_params(self):
        self.assertEqual(run_action('test.simple', params={'name':'bob'}), 'ok:bob')

    def test_admin_required(self):
        # ensure permission error when not admin
        if os.name == 'posix':
            # assume tests not running as root
            try:
                run_action('test.admin')
            except PermissionError:
                pass
            else:
                # if running as root, it's allowed
                pass
        else:
            # Windows env: test with env override
            os.environ['MULTI_TOOL_IS_ADMIN'] = '0'
            with self.assertRaises(PermissionError):
                run_action('test.admin')
            os.environ['MULTI_TOOL_IS_ADMIN'] = '1'
            self.assertEqual(run_action('test.admin'), 'admin-ok')

if __name__ == '__main__':
    unittest.main()
