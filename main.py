# Scott Ratchford
# This file contains examples of how to use the OpenAI API.

import os
import shutil
import openai
import datetime
import tiktoken
import campaign
import json
import random
import campaign_generators as gen

def log_data():
    """Moves all files from the 'data' folder to a new folder inside the 'examples' folder.
    """

    # Find the World name to create a folder with that name
    world_name = None
    for filename in os.listdir("data"):
        if filename.startswith('World-') and filename.endswith('.json'):
            world_name = filename[6:-5]
            # print("World name: " + world_name)  # debug
            break

    # Create the 'CURRENT' folder inside the 'examples' folder
    world_dir = os.path.join("examples", world_name)
    os.mkdir(world_dir)
    
    # Move all files from the 'data' folder to the 'CURRENT' folder
    for filename in os.listdir("data"):
        source = os.path.join("data", filename)
        destination = os.path.join(world_dir, filename)
        shutil.move(source, destination)

if __name__ == "__main__":
    print("Beginning program.") # debug
    random.seed(str(datetime.datetime.now()))   # seed the random number generator
    openai.api_key = os.getenv("OPENAI_API_KEY")
    model = "gpt-3.5-turbo"
    encoding = tiktoken.get_encoding("cl100k_base")

    world = gen.generate_world(numLocations=5, numCharacters=15, numItems=5)
    print("Reply received.")
    pretty_world = json.dumps(world, indent=4, cls=campaign.WorldEncoder, ensure_ascii=True)
    with open("./log/" + world.name + ".json", "w") as f:
        f.write(pretty_world)

    print("Cleaning up...") # debug
    log_data()
    print("Program complete.")  # debug
