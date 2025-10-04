import unittest
from multi_tool.actions import action
from multi_tool import orchestrator

exec_sequence = []


@action('orch.step1', description='step1', supports_dry_run=True, priority=1)
def _step1(dry_run=False, params=None):
    exec_sequence.append('step1')
    return 's1'


@action('orch.step2', description='step2', supports_dry_run=True, depends=['orch.step1'], priority=0)
def _step2(dry_run=False, params=None):
    exec_sequence.append('step2')
    return 's2'


class OrchestratorTest(unittest.TestCase):
    def setUp(self):
        exec_sequence.clear()

    def test_orchestrator_runs_deps_in_order(self):
        res = orchestrator.run_actions(['orch.step2'], dry_run=True, params={})
        # both actions should be present in results and executed in dependency order
        self.assertIn('orch.step1', res)
        self.assertIn('orch.step2', res)
        self.assertEqual(exec_sequence, ['step1', 'step2'])


if __name__ == '__main__':
    unittest.main()
