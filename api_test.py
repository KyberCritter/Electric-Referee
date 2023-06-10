# Scott Ratchford
# This file contains examples of how to use the OpenAI API.

import os
import openai
import datetime
import tiktoken
import campaign_classes

def create_and_log(completion: openai.ChatCompletion) -> None:
    """Accepts a ChatCompletion object and logs it to a file.

    Args:
        completion (openai.ChatCompletion): AI response to a user message.
    """
    time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open("./log/" + time + "-completion.txt", "w") as f:
        f.write(str(completion))
    # with open("./log/" + time + "-message.txt", "w") as f:
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

if __name__ == "__main__":
    print("Beginning program.") # debug
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

    highlands = campaign_classes.World("Highlands", "A fantasy world consisting of many mountain ranges and valleys.")
    frostpeak = campaign_classes.Location("Frostpeak")
    highlands.add_location(frostpeak)
    mayor = campaign_classes.Character("John Doe")
    mayor.add_trait("occupation", "mayor")
    scepter = campaign_classes.Item("Scepter of the King")
    scepter.description = "A scepter made of gold and encrusted with jewels."
    mayor.add_item(scepter)
    highlands.add_character(mayor)
    sheriff = campaign_classes.Character("Jane Law")
    sheriff.add_trait("occupation", "sheriff")
    highlands.add_character(sheriff)
    friendship = campaign_classes.Relationship(mayor, sheriff)
    friendship.set_reciprocal_relationship("friends")
    highlands.add_relationship(friendship)
    
    question = {"role": "user", "content": "What relationship does the mayor have with Jane Law?"}

    all_messages = [highlands.as_system_msg(), question]
    # reply = openai.ChatCompletion.create(model=model, messages=all_messages, temperature=0.3)
    # create_and_log(reply)

    # print("Reply received. Cost: " + estimate_cost(reply.choices[0].message.content, model, str))
