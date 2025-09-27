import os
from ai.model_loader import ModelLoader


def test_self_check_returns_structure():
    ml = ModelLoader()
    res = ml.self_check()
    assert 'model_dirs' in res
    assert 'supported_formats' in res
