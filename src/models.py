from flask_sqlalchemy import SQLAlchemy
import enum
from sqlalchemy import String, Boolean, Text, ForeignKey, Float, Date, DateTime, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column,relationship
from datetime import datetime, date

db = SQLAlchemy()

class RoleEnum(enum.Enum):
    ADMIN = 'admin'
    USER = 'user'
    GUEST = 'guest'


class User(db.Model):
    __tablename__= "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    role: Mapped[RoleEnum] = mapped_column(
        Enum(RoleEnum, name="role_enum", create_type=True),
        default=RoleEnum.USER
        )
    pokemons:Mapped[list["Pokemon"]] = relationship(back_populates = "user",uselist=True)
    items:Mapped[list["Item"]] = relationship(back_populates ="user",uselist=True)
    favorites:Mapped[list["Favorites"]]=relationship(back_populates="user",uselist=True)


    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "role": self.role.value if self.role else None,
            "pokemons":[p.serialize() for p in self.pokemons] if self.pokemons else None,
            "items":[i.serialize() for i in self.items] if self.items else None,
            "favorites":[f.serialize() for f in self.favorites] if self.favorites else None  
        }

    
class Pokemon(db.Model):
    __tablename__ = "pokemon"
    id:Mapped[int] = mapped_column(primary_key = True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    name:Mapped[str] = mapped_column(Text(), nullable=False)
    type:Mapped[str] = mapped_column(Text(), nullable=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("user.id"))
    user:Mapped["User"] = relationship(back_populates ="pokemons",uselist=False)
    favorites_by:Mapped[list["Favorites"]] = relationship(back_populates ="pokemon",uselist=True)

    def serialize(self):
        return{
            "id":self.id,
            "name":self.name,
            "type":self.type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user":{
                "id":self.user.id,
                "username":self.user.username
            },
            "favorites_by":[f.serialize() for f in self.favorites_by] if self.favorites_by else None
        }

class Item(db.Model):
    __tablename__ = "item"
    id:Mapped[int] = mapped_column(primary_key = True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    name:Mapped[str] = mapped_column(Text(),nullable=False)
    categories:Mapped[str] = mapped_column(Text(),nullable=True)
    user_id:Mapped[int] = mapped_column(ForeignKey("user.id"))
    user:Mapped["User"] = relationship(back_populates="items",uselist=False)
    favorites_by:Mapped[list["Favorites"]] = relationship(back_populates="item",uselist=True)

    def serialize(self):
        return{
            "id":self.id,
            "name":self.name,
            "categories":self.categories,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user":{
                "id":self.user.id,
                "username":self.user.username
            },
            "favorites_by":[f.serialize() for f in self.favorites_by] if self.favorites_by else None
        }

class Favorites(db.Model):
    __tablename__ = "favorites"
    id:Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    user_id:Mapped[int] = mapped_column(ForeignKey("user.id"))
    pokemon_id:Mapped[int]=mapped_column(ForeignKey("pokemon.id"))
    item_id:Mapped[int]=mapped_column(ForeignKey("item.id"))
    user:Mapped["User"]= relationship(back_populates="favorites")
    pokemon:Mapped["Pokemon"] = relationship(back_populates ="favorites_by")
    item:Mapped["Item"]= relationship(back_populates="favorites_by")

    def serialize(self):
        return{
            "id":self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user":{
                "id":self.user.id,
                "username":self.user.username
            },
            "pokemon":{
                "id":self.pokemon.id,
                "name":self.pokemon.name
            },
            "item":{
                "id":self.item.id,
                "name":self.item.name,
                "categories":self.item.categories
            }
        }