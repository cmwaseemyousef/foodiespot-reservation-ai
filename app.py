import streamlit as st
import requests

st.title("🍽️ FoodieSpot Reservation Assistant")

st.write("Hello! I can help you book a table at the best restaurants in the city. Tell me your requirements (date, time, cuisine, guests)...")

# Conversation history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

user_input = st.text_input("You:", "")

if st.button("Send"):
    if user_input:
        # Add to history
        st.session_state["chat_history"].append({"role": "user", "content": user_input})
        # Call backend to process and get LLM/agent reply
        try:
            response = requests.post(
                "http://localhost:8000/agent", 
                json={"messages": st.session_state["chat_history"]}
            )
            data = response.json()
            agent_reply = data.get("reply", "Sorry, there was an error processing your request.")
        except Exception as e:
            agent_reply = f"Sorry, backend error: {e}"
        st.session_state["chat_history"].append({"role": "assistant", "content": agent_reply})

# Display chat
for msg in st.session_state["chat_history"]:
    st.write(f"**{msg['role'].capitalize()}**: {msg['content']}")
