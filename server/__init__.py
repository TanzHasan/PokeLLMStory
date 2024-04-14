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
    return web_app