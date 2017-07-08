from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    """User Table."""

    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    picture = Column(String(250))
    email = Column(String(100), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
            'name': self.name,
            'picture': self.picture,
            'email': self.email
        }

class Category(Base):
    """Category Table."""

    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    name = Column(String(80), nullable=False)
    description = Column(String(500), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
           'name': self.name,
           'user_id': self.user_id,
           'description': self.description,
           'id': self.id,
        }


class Item(Base):
    """Item Table."""

    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    name = Column(String(250), nullable=False)
    price = Column(String(8))
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "category": self.category.name
        }


engine = create_engine('sqlite:///item-catalog.db')
Base.metadata.create_all(engine)
