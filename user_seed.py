"""
Category Seeder.

Uses faker to generate random word for category names
"""
from faker import Faker
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, engine

# Starting DB Session
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Initializing faker library
fake = Faker()

for i in xrange(20):
    name = fake.name()
    email = fake.free_email()
    new_user = User(name=name, email=email)
    session.add(new_user)
    session.commit()
