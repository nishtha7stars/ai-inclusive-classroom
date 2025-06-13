import streamlit as st
import pandas as pd
import openai
from gtts import gTTS
import playsound
import os

openai.api_key = "sk-..."  # Replace with your OpenAI API key

# Sidebar - Mode Selector
mode = st.sidebar.radio("Choose Mode", ["Student Assistant", "Teacher Dashboard"])

if mode == "Student Assistant":
    st.title("🎓 AI Learning Assistant")
    name = st.text_input("Enter your name:")
    style = st.selectbox("Preferred Style", ["Text", "Visual", "Audio"])
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

            if style == "Audio":
                tts = gTTS(answer)
                tts.save("speech.mp3")
                playsound.playsound("speech.mp3")
                os.remove("speech.mp3")

elif mode == "Teacher Dashboard":
    st.title("📊 Teacher Dashboard")
    data = pd.DataFrame({
        "Student": ["Anya", "Sam", "Ishaan", "Rahul", "Priya"],
        "Focus Score (out of 10)": [7, 4, 6, 8, 5],
        "Emotion": ["Happy", "Bored", "Confused", "Happy", "Frustrated"],
        "Requests for Help": [0, 2, 1, 0, 3],
        "Learning Preference": ["Visual", "Audio", "Text", "Text", "Audio"]
    })
    st.dataframe(data)

    low = data[data["Focus Score (out of 10)"] <= 5]
    if not low.empty:
        st.warning("⚠️ Students needing attention:")
        st.write(low)