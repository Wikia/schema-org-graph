"""
https://schema.org/Person
"""
from . import BaseModel


class PersonModel(BaseModel):
    """
    Person model
    """
    def __init__(self, name):
        super(PersonModel, self).__init__(model_type='Person', name=name)
