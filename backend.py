import os
import json
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for local Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load restaurant data
with open("restaurants.json", "r") as f:
    restaurants = json.load(f)

# Rule-based mock LLM for intent extraction (replace with real LLM API as needed)
def call_llm(messages):
    user_msg = messages[-1]['content'].lower()
    # Example demo logic - adapt/expand as needed
    if "book" in user_msg and "indian" in user_msg and "koramangala" in user_msg:
        return json.dumps({
            "intent": "book",
            "num_guests": 4,
            "cuisine": "Indian",
            "location": "Koramangala",
            "datetime": "tonight 8pm"
        })
    elif "indian" in user_msg:
        return json.dumps({
            "intent": "search",
            "cuisine": "Indian",
            "location": "Koramangala"
        })
    else:
        return json.dumps({
            "intent": "search",
            "cuisine": "",
            "location": ""
        })

@app.post("/agent")
async def agent(request: Request):
    data = await request.json()
    messages = data.get("messages", [])

    # 1. Call the (mock) LLM to get intent & entities as JSON
    llm_output = call_llm(messages)
    try:
        parsed = json.loads(llm_output)
    except Exception:
        return {"reply": f"Sorry, I could not understand. (Debug: {llm_output})"}

    # 2. Process the intent & entities
    intent = parsed.get("intent")
    cuisine = parsed.get("cuisine")
    location = parsed.get("location")
    num_guests = parsed.get("num_guests", 2)
    datetime_str = parsed.get("datetime", "")

    if intent in ["search", "recommend"]:
        matches = [
            r for r in restaurants
            if (not cuisine or cuisine.lower() in r["cuisine"].lower())
            and (not location or location.lower() in r["location"].lower())
        ]
        if matches:
            names = ", ".join([r["name"] for r in matches])
            reply = f"Here are some {cuisine or ''} restaurants in {location or 'the city'}: {names}"
        else:
            reply = "Sorry, no matching restaurants found."
    elif intent == "book":
        reply = f"Table for {num_guests} booked at a {cuisine} restaurant in {location} on {datetime_str}! (Demo only, not real booking.)"
    else:
        reply = f"Sorry, I can only help with searching and booking right now. (Debug: {intent})"

    return {"reply": reply}
