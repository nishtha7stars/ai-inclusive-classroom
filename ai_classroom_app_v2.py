import streamlit as st
import pandas as pd
import sqlite3
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

# Set up OpenAI client using the new API
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# Set up database
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT,
    role TEXT,
    style TEXT DEFAULT 'Text',
    mood TEXT DEFAULT '🙂'
)
''')
conn.commit()

def login_user(username, password):
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return cursor.fetchone()

def add_user(username, password, role):
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()

st.set_page_config(page_title="LearnEase AI - Inclusive Classroom", page_icon="🧠")
st.title("🧠 LearnEase AI - Inclusive Classroom Assistant")

menu = ["Login", "Register"]
choice = st.sidebar.radio("Navigate", menu)

if choice == "Register":
    st.subheader("Create Your Account")
    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    role = st.selectbox("You are a:", ["Student", "Teacher"])
    if st.button("Register"):
        add_user(new_user, new_password, role)
        st.success("🎉 Account created. You can now log in!")

elif choice == "Login":
    st.subheader("Login to Continue")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        result = login_user(username, password)
        if result:
            st.success(f"Welcome {username}!")
            role = result[2]

            if role == "Student":
                st.header("👩‍🎓 Student Learning Assistant")
                style = st.selectbox("Choose learning style", ["Text", "Visual", "Audio"])
                mood = st.selectbox("Your current mood", ["🙂", "😐", "😕", "😠"])
                question = st.text_area("Ask a question to your AI assistant")

                if question:
                    try:
                        with st.spinner("Thinking..."):
                            response = client.chat.completions.create(
                                model="gpt-3.5-turbo",
                                messages=[
                                    {"role": "system", "content": f"You are a helpful AI tutor. Answer in a way that fits a {style.lower()} learner."},
                                    {"role": "user", "content": question}
                                ],
                                temperature=0.7
                            )
                            answer = response.choices[0].message.content.strip()
                            st.markdown(f"**AI Answer:** {answer}")
                    except Exception as e:
                        st.error(f"⚠️ AI could not answer: {str(e)}")

            elif role == "Teacher":
                st.header("👩‍🏫 Teacher Dashboard")
                df = pd.read_sql_query("SELECT username, style, mood FROM users WHERE role='Student'", conn)
                st.dataframe(df)
        else:
            st.error("❌ Incorrect username or password.")