"""
Factory to create Mission test objects
"""
import factory
from datetime import datetime


class MissionFactory(factory.Factory):
    """Factory to create test missions"""
    
    class Meta:
        model = dict  # Change to your actual model
    
    id = factory.Sequence(lambda n: n)
    name = factory.Faker("sentence", nb_words=3)
    status = "pending"
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)

