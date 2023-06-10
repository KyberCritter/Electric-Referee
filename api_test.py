# Scott Ratchford
# This file contains examples of how to use the OpenAI API.

import os
import openai
import datetime
import tiktoken
import campaign
import json
import random

# global constants for sanity checking
MAX_LOCATIONS = 10
MAX_CHARACTERS = 10
# global constants for World generation
RELATIONSHIP_PROBABILITY = 0.3

def create_and_log(completion: openai.ChatCompletion) -> None:
    """Accepts a ChatCompletion object and logs it to a file.

    Args:
        completion (openai.ChatCompletion): AI response to a user message.
    """
    time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open("./log/" + time + "-completion.json", "w") as f:
        f.write(str(completion))
    # with open("./log/" + time + "-message.json", "w") as f:
    #     f.write(str(completion.choices[0].message))

def estimate_cost(prompt: str, modelName: str, returnType: type = float) -> float or str:
    """Estimates the cost of a prompt in USD. A very rough estimate.

    Args:
        prompt (str): Prompt to estimate cost of.
        modelName (str): Model to use for cost estimation.
        returnType (type, optional): Type to return. Defaults to float.
    """
    # per 1000 tokens
    model_costs = {
        "gpt-3.5-turbo": 0.002
    }
    numTokens = len(encoding.encode(prompt))
    if(returnType == str):
        return "$" + str(numTokens / 1000 * model_costs[modelName])
    else:
        return numTokens / 1000 * model_costs[modelName]

def generate_world(numLocations: int = 0, numCharacters: int = 0) -> campaign.World:
    """Generates a world using the OpenAI API.

    Returns:
        campaign_classes.World: The generated world.
        numLocations (int, optional): The number of locations to generate. Defaults to 0.
        numCharacters (int, optional): The number of characters to generate. Defaults to 0.
    """

    # TODO: relationships and items

    # sanity checks to prevent excessive API calls
    if(numLocations < 0):
        raise ValueError("numLocations must be greater than or equal to 0.")
    if(numLocations > MAX_LOCATIONS):
        raise ValueError("numLocations must be less than or equal to " + str(MAX_LOCATIONS) + ".")
    if(numLocations < 0):
        raise ValueError("numCharacters must be greater than or equal to 0.")
    if(numLocations > MAX_CHARACTERS):
        raise ValueError("numCharacters must be less than or equal to " + str(MAX_CHARACTERS) + ".")

    world_prompt = [
        {"role": "user", "content": "Generate a world for a 5e campaign."},
        {"role": "system", "content": "Create your reply in the format: { \"name\": \"World Name\", \"description\": \"World Description\" }"},
    ]
    reply = openai.ChatCompletion.create(model=model, messages=world_prompt, temperature=1.3, max_tokens=500)
    create_and_log(reply)
    if(reply.choices[0].finish_reason == "length"):
        raise ValueError("World generation failed due to length. Try again.")
        # TODO: append }" to reply.choices[0].message.content
    # print("JSON World:\n" + reply.choices[0].message.content)   # debug
    world = json.loads(reply.choices[0].message.content, cls=campaign.WorldDecoder)

    all_messages = []
    all_messages.append(world.as_system_msg()) # add the world as context for the next location
    for i in range(numLocations):
        # the prompt for the next location
        all_messages.extend([
            {"role": "user", "content": "Generate a location to add to the world of " + str(world.name) + "."},
            {"role": "system", "content": "Create your reply in the format: { \"name\": \"Location Name\", \"description\": \"Location Description\" }"}
        ])
        reply = openai.ChatCompletion.create(model=model, messages=all_messages, temperature=1.3, max_tokens=200)
        create_and_log(reply)
        # print("JSON Location:\n" + reply.choices[0].message.content)   # debug
        if(reply.choices[0].finish_reason == "length"):
            raise ValueError("Location generation failed due to length. Try again.")
            # TODO: append }" to reply.choices[0].message.content
        location = json.loads(reply.choices[0].message.content, cls=campaign.LocationDecoder)
        world.add_location(location)
        # remove all prompts and system messages from the list of messages
        for msg in all_messages:
            if(msg["role"] == "user"):
                all_messages.remove(msg)
            elif(msg["role"] == "system"):
                all_messages.remove(msg)
        # all_messages.append(location.as_system_msg()) # add the previous locations as context for the next location
        all_messages.append(world.as_system_msg()) # update the world as context for the next location
    
    all_messages = []
    all_messages.append(world.as_system_msg()) # add the world as context for the next location
    for i in range(numCharacters):
        # the prompt for the next location
        all_messages.extend([
            {"role": "user", "content": "Generate a character to add to the world of " + str(world.name) + "."},
            {"role": "system", "content": "Create your reply in the format: { \"name\": \"Character Name\", \"description\": \"Character Description\" }"}
        ])
        reply = openai.ChatCompletion.create(model=model, messages=all_messages, temperature=1.3, max_tokens=200)
        create_and_log(reply)
        # print("JSON Character:\n" + reply.choices[0].message.content)   # debug
        character = json.loads(reply.choices[0].message.content, cls=campaign.CharacterDecoder)
        if(reply.choices[0].message.finish_reason == "length"):
            raise ValueError("Character generation failed due to length. Try again.")
            # TODO: append }" to reply.choices[0].message.content
        world.add_character(character)
        # remove all prompts and system messages from the list of messages
        for msg in all_messages:
            if(msg["role"] == "user"):
                all_messages.remove(msg)
            elif(msg["role"] == "system"):
                all_messages.remove(msg)
        all_messages.append(world.as_system_msg()) # update the world as context for the next character
    
    all_messages = []
    all_messages.append(world.as_system_msg()) # add the world as context for the next location
    for characterA in world.characters:
        for characterB in world.characters:
            if(characterA == characterB):   # don't generate relationships between the same character
                continue
            if(random.random() < RELATIONSHIP_PROBABILITY):   # generate a relationship between the two characters only if the random number is less than the probability
                # the prompt for the next relationship
                all_messages.extend([
                    {"role": "user", "content": "Generate a relationship between " + str(characterA.name) + " and " + str(characterB.name) + "."},
                    {"role": "system", "content": "Create your reply in the format: { \"relateAB\": \"Character A to B relationship\", \"relateBA\": \"Character B to A relationship\" }"}
                ])
                reply = openai.ChatCompletion.create(model=model, messages=all_messages, temperature=1.0, max_tokens=200)
                create_and_log(reply)
                # print("JSON Relationship:\n" + reply.choices[0].message.content)   # debug
                if(reply.choices[0].message.finish_reason == "length"):
                    raise ValueError("Relationship generation failed due to length. Try again.")
                    # TODO: append }" to reply.choices[0].message.content
                description = json.loads(reply.choices[0].message.content)  # don't use the decoder here because it's not a full object
                relationship = campaign.Relationship(characterA, characterB, description["relateAB"], description["relateBA"])
                character.add_relationship(relationship)
                # remove all prompts and system messages from the list of messages
                for msg in all_messages:
                    if(msg["role"] == "user"):
                        all_messages.remove(msg)
                    elif(msg["role"] == "system"):
                        all_messages.remove(msg)
                all_messages.append(world.as_system_msg())

    return world

if __name__ == "__main__":
    print("Beginning program.") # debug
    random.seed(str(datetime.datetime.now()))   # seed the random number generator
    openai.api_key = os.getenv("OPENAI_API_KEY")
    model = "gpt-3.5-turbo"
    encoding = tiktoken.get_encoding("cl100k_base")

    """
    test_message = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello world"}]
    )
    create_and_log(test_message)
    """

    world = generate_world(numLocations=2, numCharacters=3)
    pretty_world = json.dumps(world, indent=4, cls=campaign.WorldEncoder, ensure_ascii=True)

    # print("Reply received. Cost: " + estimate_cost(reply.choices[0].message.content, model, str))
    print("Reply received.")
