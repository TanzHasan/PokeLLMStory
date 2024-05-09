from modal import Image, Stub, wsgi_app
import modal

FINE_TUNED_MODELS = ["gpt-3.5-turbo",
    "ft:gpt-3.5-turbo-0125:personal:pokellmtest1:9Dg1nzhp",
"ft:gpt-3.5-turbo-0125:personal:pokellmtest1:9Dg1pPFW:ckpt-step-28",
"ft:gpt-3.5-turbo-0125:personal:pokellmtest1:9Dg1qQwq:ckpt-step-56",
"ft:gpt-3.5-turbo-0125:personal:pokellmtest1:9Dg1qMuH:ckpt-step-84",
"ft:gpt-3.5-turbo-1106:personal:pokellmtrashtalk:9LyPN3kH",
"ft:gpt-3.5-turbo-1106:personal:newfinetunejsonl:9LzvImtM", 
"gpt-3.5-turbo",
]
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
    # print(data)
    
    for entry in entries:
        collection = db[entry]  # Access the appropriate collection
        for item in data[entry]:
            result = collection.find_one({"name": item})
            if not result: 
                continue
            rstring = f"{item}: "
            if 'descriptions' in result:
                rstring = rstring + str(result["descriptions"][0])
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
    # entries = ""
    # print(entries)
    client = openai.OpenAI(api_key=os.environ["FINE_TUNED_OPENAI_API_KEY"])
    if entries != "":
        messages[-1]['content'] += f"\n\nContext: {entries}"
    response = client.chat.completions.create(
        messages=messages,
        model=FINE_TUNED_MODELS[-2],
    )
    
    print(response.choices[0].message.content)
    expl = response.choices[0].message.content

    return {"result": expl, "prev_message": messages[-1]['content']}

@stub.function()
def check_hallucination(prompt, hallucination_ask, data):
    import pymongo
    import os
    import openai
    entries = '\n'.join(unpack.local(data))
    # entries = ""
    client = openai.OpenAI(api_key=os.environ["FINE_TUNED_OPENAI_API_KEY"])
    if entries != "":
        prompt += f"\n\nContext: {entries}"
    response = client.chat.completions.create(
        messages=[{
                "role": "system",
                "content": prompt,
            },
            {"role": "user", "content": hallucination_ask}],
        model=FINE_TUNED_MODELS[-1],
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
        prompt = request.json["prompt"]
        hallucination_ask = request.json["hallucination_ask"]
        data = request.json["data"]

        return check_hallucination.remote(prompt, hallucination_ask, data)

    return web_app