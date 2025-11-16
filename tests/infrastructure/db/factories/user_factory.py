"""
Factory to create User test objects
"""
import factory


class UserFactory(factory.Factory):
    """Factory to create test users"""
    
    class Meta:
        model = dict  # Change to your actual model
    
    id = factory.Sequence(lambda n: n)
    email = factory.Faker("email")
    username = factory.Faker("user_name")
    is_active = True
    is_admin = False

