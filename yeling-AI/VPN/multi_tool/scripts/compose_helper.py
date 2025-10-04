"""Small helper to parse docker-compose YAML and extract service image names.

This avoids brittle grep-based extraction and supports basic YAML constructs.
Requires PyYAML (already in requirements-pin.txt)
"""
from __future__ import annotations

import os
import yaml
from typing import Optional


def get_service_image(compose_path: str, service_name: str = "multi_tool") -> Optional[str]:
    """Return the image string for the given service in the compose file, or None if not found."""
    if not os.path.isfile(compose_path):
        return None
    try:
        with open(compose_path, 'r') as f:
            data = yaml.safe_load(f)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    services = data.get('services') or {}
    svc = services.get(service_name) or {}
    img = svc.get('image') if isinstance(svc, dict) else None
    # image can be None or a dict in some advanced setups; normalize to str
    if isinstance(img, str):
        return img
    return None


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument('compose', help='path to docker-compose.yml')
    p.add_argument('--service', default='multi_tool')
    args = p.parse_args()
    print(get_service_image(args.compose, args.service) or '')
