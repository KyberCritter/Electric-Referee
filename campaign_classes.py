# Scott Ratchford
# This file contains classes for representing a campaign.

import json
from json import JSONEncoder
import enum
from typing import Any

class Size(enum.IntEnum):
    """Represents the size of a creature or object."""
    TINY = 0
    SMALL = 1
    MEDIUM = 2
    LARGE = 3
    HUGE = 4
    GARGANTUAN = 5

class World():
    """Represents a world in which a campaign takes place."""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.characters = []
        self.relationships = []
        self.locations = []

    def __str__(self):
        return str({
            "name": self.name,
            "description": self.description,
            "characters": json.dumps(self.characters, cls=CharacterEncoder),
            "relationships": self.relationships,
            "locations": self.locations
        })
    
    def __repr__(self):
        return self.__str__()
    
    def add_character(self, character: "Character"):
        assert(type(character) == Character)
        self.characters.append(character)

    def add_relationship(self, relationship: "Relationship") -> bool:
        assert(type(relationship) == Relationship)
        if not relationship in self.relationships and not relationship.flip() in self.relationships:
            self.relationships.append(relationship)
            return True
        return False

    def add_location(self, location):
        assert(type(location) == Location)
        self.locations.append(location)
        self.locations[-1].world = self

    def get_relationship_between(self, characterA: "Character", characterB: "Character") -> "Relationship":
        """Returns the relationship between two characters, or None if no relationship exists."""
        for relationship in self.relationships:
            if relationship.characterA == characterA and relationship.characterB == characterB or relationship.characterA == characterB and relationship.characterB == characterA:
                return relationship
        return None
    
    def as_system_msg(self):
        """Returns a string representation of the world, formatted for OpenAI API system messages."""
        return {"role": "system", "content": self.__str__()}

class Location():
    """Represents a single location in a World."""
    def __init__(self, name: str, world: World = None) -> None:
        self.name = name
        self.description = ""
        self.traits = []
        self.inventory = []
        self.world = world

class Character():
    """Represents a single character."""
    def __init__(self, name) -> None:
        self.name = name
        # self.description = ""
        self.traits = {}        # dictionary of trait: description
        # self.relationships = [] # list of Relationship objects
        self.inventory = []     # list of Item objects
    
    def __str__(self):
        return json.dumps(self.__dict__, cls=CharacterEncoder)
    
    def __repr__(self):
        return self.__str__()
    
    def add_trait(self, quality: str, description: str):
        assert(type(quality) == str)
        assert(type(description) == str)
        self.traits[quality] = description
    
    def add_item(self, item: "Item"):
        assert(type(item) == Item)
        self.inventory.append(item)
    
    def encode(self) -> str:
        return self.__str__()

class Relationship():
    """Represents both directions of a relationship between two characters."""
    def __init__(self, characterA: "Character", characterB: "Character") -> None:
        self.characterA = characterA
        self.characterB = characterB
        self.relateAB = ""
        self.relateBA = ""
    
    def __str__(self):
        return json.dumps(self.__dict__, default=lambda self: self.encode())
    
    def __repr__(self):
        return self.__str__()
    
    def set_reciprocal_relationship(self, relationship: str):
        assert(type(relationship) == str)
        self.relateAB = relationship
        self.relateBA = relationship
    
    def set_bidirectional_relationship(self, relateAB: str, relateBA: str):
        assert(type(relateAB) == str)
        assert(type(relateBA) == str)
        self.relateAB = relateAB
        self.relateBA = relateBA
    
    def encode(self) -> str:
        """Returns a JSON representation of the Relationship."""
        return str({
            "characterA": str(self.characterA),
            "characterB": str(self.characterB),
            "relateAB": self.relateAB,
            "relateBA": self.relateBA
        })
    
    def flip(self) -> "Relationship":
        """Returns a new Relationship with the characters and relationships swapped."""
        tempRelationship = Relationship(self.characterB, self.characterA)
        tempRelationship.relateAB, tempRelationship.relateBA = self.relateBA, self.relateAB
        return tempRelationship

class Item():
    """Represents a single item."""
    def __init__(self, name: str) -> None:
        self.name = name
        self.description = ""
        self.traits = {}        # dictionary of trait: description
        self.size = Size.MEDIUM # Size enum
    
    def __str__(self):
        return json.dumps(self.__dict__)
    
    def __repr__(self):
        return self.__str__()
    
    def add_trait(self, quality: str, description: str):
        assert(type(quality) == str)
        assert(type(description) == str)
        self.traits[quality] = description

class WorldEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

class CharacterEncoder(JSONEncoder):
    def default(self, o: Character):
        return o.__dict__

class RelationshipEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

class ItemEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

class LocationEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
