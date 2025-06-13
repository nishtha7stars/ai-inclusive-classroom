import streamlit as st
import pandas as pd
import sqlite3
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Initialize DB
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    role TEXT,
    style TEXT DEFAULT 'Text',
    mood TEXT DEFAULT '🙂'
)''')
conn.commit()

def login_user(username, password):
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return cursor.fetchone()

def add_user(username, password, role):
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()

st.title("🧠 AI Classroom for All (Fixed)")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    st.subheader("Create New Account")
    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type='password')
    role = st.selectbox("I am a...", ["Student", "Teacher"])
    if st.button("Register"):
        add_user(new_user, new_password, role)
        st.success("Account created successfully. Go to Login.")

elif choice == "Login":
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        result = login_user(username, password)
        if result:
            st.success(f"Welcome {username}!")
            role = result[2]
            if role == "Student":
                st.header("🎓 Student AI Assistant")
                style = st.selectbox("Preferred Style", ["Text", "Visual", "Audio"])
                mood = st.selectbox("How are you feeling?", ["🙂", "😐", "😕", "😠"])
                question = st.text_input("Ask your question:")
                if question:
                    with st.spinner("Getting help..."):
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": f"Explain in {style.lower()} style."},
                                {"role": "user", "content": question}
                            ]
                        )
                        st.markdown(f"**AI:** {response.choices[0].message.content}")
            elif role == "Teacher":
                st.header("📊 Teacher Dashboard")
                df = pd.read_sql("SELECT username, style, mood FROM users WHERE role='Student'", conn)
                st.dataframe(df)
        else:
            st.error("Incorrect username/password")