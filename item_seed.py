"""
Item Seeder.

Uses faker to generate random attributes for items
"""
from faker import Faker
from random import randint
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Item, engine

# Starting DB Session
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Initializing faker library
fake = Faker()

for i in xrange(100):
    category_id = randint(1, 10)
    name = fake.words(nb=1, ext_word_list=None)[0]
    user_id = randint(0, 19)
    price = fake.pyint()
    description = fake.text(max_nb_chars=800, ext_word_list=None)
    item = Item(
        name=name,
        price=price,
        description=description,
        category_id=category_id)
    session.add(item)
    session.commit()
