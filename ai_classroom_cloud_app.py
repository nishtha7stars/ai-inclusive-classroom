import streamlit as st
import pandas as pd
import openai
import os

openai.api_key = st.secrets.get("OPENAI_API_KEY", "sk-...")  # Replace with your OpenAI key in .streamlit/secrets.toml

# Sidebar - Mode Selector
mode = st.sidebar.radio("Choose Mode", ["Student Assistant", "Teacher Dashboard"])

if mode == "Student Assistant":
    st.title("🎓 AI Learning Assistant")
    name = st.text_input("Enter your name:")
    style = st.selectbox("Preferred Style", ["Text", "Visual", "Audio"])
    mood = st.selectbox("How are you feeling today?", ["🙂 Happy", "😐 Okay", "😕 Confused", "😠 Frustrated"])
    question = st.text_input("Ask a question:")

    if question:
        with st.spinner("Thinking..."):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"Explain in {style.lower()} style"},
                    {"role": "user", "content": question}
                ]
            )
            answer = response['choices'][0]['message']['content']
            st.markdown(f"**AI:** {answer}")

elif mode == "Teacher Dashboard":
    st.title("📊 Teacher Dashboard")
    data = pd.DataFrame({
        "Student": ["Anya", "Sam", "Ishaan", "Rahul", "Priya"],
        "Focus Score (out of 10)": [7, 4, 6, 8, 5],
        "Emotion": ["🙂 Happy", "😐 Okay", "😕 Confused", "🙂 Happy", "😠 Frustrated"],
        "Requests for Help": [0, 2, 1, 0, 3],
        "Learning Preference": ["Visual", "Audio", "Text", "Text", "Audio"]
    })
    st.dataframe(data)

    low = data[data["Focus Score (out of 10)"] <= 5]
    if not low.empty:
        st.warning("⚠️ Students needing attention:")
        st.write(low)