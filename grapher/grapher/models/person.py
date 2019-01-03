"""
https://schema.org/Person
"""
from . import BaseModel


class PersonModel(BaseModel):
    """
    Person model
    """
    def __init__(self, name, birth_date):
        super(PersonModel, self).__init__(schema='https://schema.org/Person')

        self.add_property('name', name)
        self.add_property('birthDate', birth_date)
