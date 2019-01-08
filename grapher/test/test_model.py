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


def test_encode():
    assert BaseModel.encode_name('1. FC Sankt Pauli') == 'FC_Sankt_Pauli', 'Remove starting digits'
    assert BaseModel.encode_name('Schalke 04') == 'Schalke_04', 'Keep digits inside the string'
    assert BaseModel.encode_name('Manchester United') == 'Manchester_United', 'Spaces are replaced'
    assert BaseModel.encode_name('Alt\xc4\xb1nordu_S_K') == 'Altnordu_S_K', 'UTF characters are properly encoded'
    assert BaseModel.encode_name('Altınordu S.K.') == 'Altnordu_S_K', 'UTF characters are properly encoded'
