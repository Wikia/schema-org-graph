"""
Models test suite
"""
import pytest

from grapher.models import BaseModel


def test_model_assert():
    with pytest.raises(AssertionError) as ex:
        BaseModel(name=None, model_type='foo')

    assert str(ex).endswith('name of a model cannot be None')

    BaseModel(name='bar', model_type='foo')
