"""Orchestrator: schedule and run registered actions respecting dependencies and priority.

This module exposes a single function `run_actions(names, ...)` used by the CLI
and tests. It builds a transitive dependency graph for the requested action
names, computes a safe execution order (respecting dependencies and using
priority as a tie-breaker), acquires a lock, and sequentially runs the
registered actions.
"""

from typing import List, Dict, Any, Set
import time
import collections
import os
import tempfile

from . import actions as _actions
from .utils.lock import FileLock


def _build_transitive_registry(registry: Dict[str, Dict[str, Any]], targets: List[str]) -> Set[str]:
    """Return the set of targets plus their transitive dependencies present in registry."""
    seen = set()

    def visit(n: str) -> None:
        if n in seen:
            return
        if n not in registry:
            return
        seen.add(n)
        for d in registry.get(n, {}).get('depends', []) or []:
            visit(d)

    for t in targets:
        visit(t)
    return seen


def _topo_sort_with_priority(registry: Dict[str, Dict[str, Any]], nodes: Set[str]) -> List[str]:
    """Kahn's algorithm restricted to `nodes`, using action priority as tie-breaker."""
    graph = collections.defaultdict(list)  # u -> [v1, v2]
    indeg = {n: 0 for n in nodes}
    for n in nodes:
        for d in registry.get(n, {}).get('depends', []) or []:
            if d in nodes:
                graph[d].append(n)
                indeg[n] = indeg.get(n, 0) + 1

    # initial ready nodes
    ready = [n for n in nodes if indeg.get(n, 0) == 0]
    ready.sort(key=lambda n: registry.get(n, {}).get('priority', 0), reverse=True)

    order = []
    while ready:
        u = ready.pop(0)
        order.append(u)
        for v in graph.get(u, []):
            indeg[v] -= 1
            if indeg[v] == 0:
                ready.append(v)
        ready.sort(key=lambda n: registry.get(n, {}).get('priority', 0), reverse=True)

    return order


def run_actions(names: List[str], dry_run: bool = False, params: Dict[str, Any] = None, timeout: int = 30, check_admin: bool = True):
    """Run actions respecting dependencies and priority.

    Returns a mapping name -> {'ok': bool, 'result'|'error': ...} for each
    executed action in execution order. On first failure, execution stops.
    """
    params = params or {}
    registry = _actions.list_actions()
    nodes = _build_transitive_registry(registry, names)
    if not nodes:
        return {}

    exec_order = _topo_sort_with_priority(registry, nodes)

    # Use a cross-platform temporary directory for the lock file/dir
    lock_dir = tempfile.gettempdir()
    lock_path = os.path.join(lock_dir, 'multi_tool_orchestrator.lock')
    results: Dict[str, Dict[str, Any]] = {}
    with FileLock(lock_path, timeout=timeout):
        for name in exec_order:
            meta = registry.get(name, {})
            # If dry_run requested but action doesn't support it, record error and stop
            if dry_run and not meta.get('supports_dry_run'):
                results[name] = {'ok': False, 'error': f"Action '{name}' does not support dry-run"}
                break
            try:
                res = _actions.run_action(name, dry_run=dry_run, params=params or {}, check_admin=check_admin)
                results[name] = {'ok': True, 'result': res}
            except Exception as e:
                results[name] = {'ok': False, 'error': str(e)}
                break
            # small throttle
            time.sleep(0.02)
    return results


__all__ = ['run_actions']

