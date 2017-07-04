from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    """User Table."""

    __tablename__ = 'user'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    picture = Column(String(250))
    email = Column(String(100), nullable=False)


class Category(Base):
    """Category Table."""

    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(500), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
           'name': self.name,
           'description': self.description,
           'id': self.id,
        }


class Item(Base):
    """Item Table."""

    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    price = Column(String(8))
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
            "name": self.name,
            "id": self.id,
            "price": self.price,
            "description": self.description,
            "category": self.category.name
        }


engine = create_engine('sqlite:///item-catalog.db')
Base.metadata.create_all(engine)
