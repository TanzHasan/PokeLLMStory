from modal import Image, Stub, wsgi_app
import modal

stub = Stub(
    "pllm",
    image=Image.debian_slim().pip_install("flask", "pymongo", "openai", "flask-cors"),
    secrets=[modal.Secret.from_name("flask_Secrets")],
)

@stub.function()
def unpack(data):   
    import pymongo
    import os
    client = pymongo.MongoClient(os.environ["MONGO_URL"])
    db = client["Data"]  # Replace with your actual database name
    
    entries = ["pokemon", "abilities", "moves", "items"]
    ans = []
    
    for entry in entries:
        collection = db[entry]  # Access the appropriate collection
        for item in data[entry]:
            result = collection.find_one({"name": item})
            rstring = f"{item}: "
            if 'descriptions' in result:
                rstring = rstring + str(result["descriptions"])
            if 'description' in result:
                rstring = rstring + result["description"]
            if 'biology' in result:
                rstring = rstring + result["biology"]
            ans.append(rstring)
    return ans

@stub.function()
def trash_talk(game_string, query, data):
    import pymongo
    import os
    import openai
    entries = unpack.local(data)
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    prompt = f"{query}:\n\n"
    prompt += f"Context: {entries}"
    response = client.chat.completions.create(
        messages=[{
                "role": "system",
                "content": prompt,
            },
            {"role": "user", "content": game_string}],
        model="gpt-3.5-turbo",
    )
    
    print(response.choices[0].message.content)
    expl = response.choices[0].message.content

    return {"result": expl}

@stub.function() 
def test_chat_generator(messages, data):
    import pymongo
    import os
    import openai
    entries = unpack.local(data)
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    # prompt = f"{query}:\n\n"
    # prompt += f"Context: {entries}"
    response = client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
    )
    
    print(response.choices[0].message.content)
    expl = response.choices[0].message.content

    return {"result": expl}

@stub.function()
def check_hallucination(next_part, story, battle_logs, data):
    import pymongo
    import os
    import openai
    entries = '\n'.join(unpack.local(data))
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    prompt = f"The next part of the story is:\n\n{next_part}\n\nThe story so far is:\n\n{story}\n\n The battle logs are:\n\n{battle_logs}\n\n The context is: {entries}"
    response = client.chat.completions.create(
        messages=[{
                "role": "system",
                "content": prompt,
            },
            {"role": "user", "content": "Yes or No to the following question: Do the battle logs and the next part of the story make sense? Only say Yes or No, nothing else. Only say Yes or No, nothing else. Only Say Yes or No, nothing else."}],
        model="gpt-3.5-turbo",
    )
    
    print(response.choices[0].message.content)
    expl = response.choices[0].message.content

    return {"result": expl}
    

@stub.function()
@wsgi_app()
def flask_app():
    from flask import Flask, request
    from flask_cors import CORS, cross_origin

    web_app = Flask(__name__)
    cors = CORS(web_app)

    @web_app.post("/get_battle")
    @cross_origin()
    def get_battle():
        log = request.json["game_string"]
        query = request.json["query"]
        data = request.json["data"]
        return trash_talk.remote(log, query, data)
    @web_app.post('/battle_chat_generator_test')
    @cross_origin()
    def battle_chat_generator_test():
        messages = request.json["messages"]
        data = request.json["data"]
        return test_chat_generator.remote(messages, data)
    
    @web_app.post('/check_hallucination_test')
    @cross_origin()
    def check_hallucination_test():
        next_part = request.json["next_part"]
        story = request.json["story"]
        data = request.json["data"]
        battle_logs = request.json["battle_logs"]
        
        return check_hallucination.remote(next_part, story, battle_logs,data)

    return web_app