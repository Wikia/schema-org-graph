"""
Football (and other sports) related models
"""
from . import BaseModel


class PersonModel(BaseModel):
    """
    Person model
    """
    def __init__(self, name):
        # https://schema.org/Person
        super(PersonModel, self).__init__(model_type='Person', name=name)


class SportsTeamModel(BaseModel):
    """
    F.C. Model
    """
    def __init__(self, name):
        # https://schema.org/SportsTeam
        super(SportsTeamModel, self).__init__(model_type='SportsTeam', name=name)
