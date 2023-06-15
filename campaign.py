# Scott Ratchford
# This file contains classes for representing a campaign.

import json
from json import JSONEncoder, JSONDecoder
import enum
from typing import Any
import datetime

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
        self.created_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")   # serves as a unique ID

    def __str__(self):
        return json.dumps(self, cls=WorldEncoder, indent=4, ensure_ascii=True)
    
    def __repr__(self):
        return self.__str__()
    
    def add_character(self, character: "Character"):
        assert(type(character) == Character)
        self.characters.append(character)

    def add_relationship(self, relationship: "Relationship") -> bool:
        assert(type(relationship) == Relationship)
        if not relationship in self.relationships and not relationship.flipped() in self.relationships:
            self.relationships.append(relationship)
            return True
        return False

    def add_location(self, location):
        assert(type(location) == Location)
        self.locations.append(location)

    def get_relationship_between(self, characterA: "Character", characterB: "Character") -> "Relationship":
        """Returns the relationship between two characters, or None if no relationship exists."""
        for relationship in self.relationships:
            if relationship.characterAName == characterA.name and relationship.characterBName == characterB.name or relationship.characterAName == characterB.name and relationship.characterBName == characterA.name:
                return relationship
        return None
    
    def as_system_msg(self):
        """Returns a string representation of the world, formatted for OpenAI API system messages."""
        return {"role": "system", "content": self.__str__()}
    
    def characters_as_system_msg(self):
        """Returns a list of string representations of the Characters, formatted for OpenAI API system messages."""
        return [character.as_system_msg() for character in self.characters]
    
    def relationships_as_system_msg(self):
        """Returns a list of string representations of the Relationships, formatted for OpenAI API system messages."""
        return [relationship.as_system_msg() for relationship in self.relationships]
    
    def locations_as_system_msg(self):
        """Returns a list of string representations of the Locations, formatted for OpenAI API system messages."""
        return [location.as_system_msg() for location in self.locations]
    
    def world_basics(self) -> str:
        """Returns a list of string representations of the world's basic information, formatted for OpenAI API system messages."""
        return "The world is called " + self.name
    
    def encode(self) -> str:
        return self.__str__()
    
    def decode(self, json_string: str) -> "World":
        return json.loads(json_string, cls=WorldDecoder)

class Location():
    """Represents a single location in a World."""
    def __init__(self, name: str) -> None:
        self.name = name
        self.description = ""
        self.traits = []
        self.inventory = []
    
    def __str__(self):
        return json.dumps(self.__dict__, cls=LocationEncoder, indent=4, ensure_ascii=True)
    
    def __repr__(self):
        return self.__str__()
    
    def add_trait(self, quality: str, description: str):
        assert(type(quality) == str)
        assert(type(description) == str)
        self.traits.append((quality, description))
    
    def add_item(self, item: "Item"):
        assert(type(item) == Item)
        self.inventory.append(item)
    
    def encode(self) -> str:
        return self.__str__()

    def as_system_msg(self):
        """Returns a string representation of the Location, formatted for OpenAI API system messages."""
        return {"role": "system", "content": self.__str__()}

class Character():
    """Represents a single character."""
    def __init__(self, name) -> None:
        self.name = name
        self.description = ""
        self.traits = {}        # dictionary of trait: description
        self.inventory = []     # list of Item objects
        self.created_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")   # serves as a unique ID
    
    def __str__(self):
        return json.dumps(self.__dict__, cls=CharacterEncoder, indent=4, ensure_ascii=True)
    
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

    def as_system_msg(self):
        """Returns a string representation of the Character, formatted for OpenAI API system messages."""
        return {"role": "system", "content": self.__str__()}

class Relationship():
    """Represents both directions of a relationship between two characters."""
    def __init__(self, characterA: Character, characterB: Character) -> None:
        self.characterAName = characterA.name
        self.characterA_ID = characterA.created_time
        self.characterBName = characterB.name
        self.characterB_ID = characterB.created_time
        self.relateAB = ""
        self.relateBA = ""
        self.created_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")   # serves as a unique ID
    
    def __str__(self):
        return json.dumps(self.__dict__, default=RelationshipDecoder, indent=4, ensure_ascii=True)
    
    def __repr__(self):
        return self.__str__()
    
    def set_symmetric_relationship(self, relationship: str):
        assert(type(relationship) == str)
        self.relateAB = relationship
        self.relateBA = relationship
    
    def set_asymmetric_relationship(self, relateAB: str, relateBA: str):
        assert(type(relateAB) == str)
        assert(type(relateBA) == str)
        self.relateAB = relateAB
        self.relateBA = relateBA
    
    def encode(self) -> str:
        """Returns a JSON representation of the Relationship."""
        return self.__str__()
    
    def flipped(self) -> "Relationship":
        """Returns a new Relationship with the characters and relationships swapped."""
        tempRelationship = Relationship(Character(self.characterBName), Character(self.characterAName))
        tempRelationship.created_time = self.created_time
        tempRelationship.characterA_ID, tempRelationship.characterB_ID = self.characterB_ID, self.characterA_ID
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
        return json.dumps(self.__dict__, cls=ItemEncoder, indent=4, ensure_ascii=True)
    
    def __repr__(self):
        return self.__str__()
    
    def add_trait(self, quality: str, description: str):
        assert(type(quality) == str)
        assert(type(description) == str)
        self.traits[quality] = description

class WorldEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

class LocationEncoder(JSONEncoder):
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

class WorldDecoder(JSONDecoder):
    def decode(self, o):
        dct = json.loads(o)
        world = World(dct["name"], dct["description"])
        try:
            world.characters = json.loads(dct["characters"], cls=CharacterDecoder)
        except:
            world.characters = []
        try:
            world.relationships = json.loads(dct["relationships"], cls=RelationshipDecoder)
        except:
            world.relationships = []
        try:
            world.locations = json.loads(dct["locations"], cls=LocationDecoder)
        except:
            world.locations = []
        world.created_time = dct["created_time"]
        return world

class LocationDecoder(JSONDecoder):
    def decode(self, o):
        dct = json.loads(o)
        location = Location(dct["name"])
        location.description = dct["description"]
        try:
            location.traits = dct["traits"]
        except:
            location.traits = []
        try:
            location.inventory = json.loads(dct["inventory"], cls=ItemDecoder)
        except:
            location.inventory = []
        return location

class CharacterDecoder(JSONDecoder):
    def decode(self, o):
        dct = json.loads(o, )
        character = Character(dct["name"])
        try:
            character.traits = dct["traits"]
        except:
            character.traits = []
        try:
            character.inventory = json.loads(dct["inventory"], cls=ItemDecoder)
        except:
            character.inventory = []
        character.created_time = dct["created_time"]
        return character

class RelationshipDecoder(JSONDecoder):
    def decode(self, o):
        dct = json.loads(o)
        relationship = Relationship(dct["characterAName"], dct["characterBName"])
        relationship.relateAB = dct["relateAB"]
        relationship.relateBA = dct["relateBA"]
        relationship.created_time = dct["created_time"]
        return relationship

class ItemDecoder(JSONDecoder):
    def decode(self, o):
        dct = json.loads(o)
        item = Item(dct["name"])
        item.description = dct["description"]
        try:
            item.traits = dct["traits"]
        except:
            item.traits = []
        try:
            item.size = dct["size"]
        except:
            item.size = Size.MEDIUM
        return item
