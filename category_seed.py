"""
Category Seeder.

Uses faker to generate random word for category names
"""
from faker import Faker
from sqlalchemy.orm import sessionmaker
from random import randint
from database_setup import Base, Category, engine

# Starting DB Session
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Initializing faker library
fake = Faker()

for i in xrange(10):
    name = fake.words(nb=1, ext_word_list=None)[0]
    description = fake.text(max_nb_chars=800, ext_word_list=None)
    user_id = randint(0, 19) 
    new_category = Category(name=name, description=description)
    session.add(new_category)
    session.commit()
