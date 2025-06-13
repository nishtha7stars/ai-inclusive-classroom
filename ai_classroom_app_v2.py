import streamlit as st
import pandas as pd
import sqlite3
from openai import OpenAI

# Load OpenAI API key
api_key = st.secrets.get("OPENAI_API_KEY", None)
client = OpenAI(api_key=api_key) if api_key else None

# DB setup
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

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Functions
def login_user(username, password):
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return cursor.fetchone()

def add_user(username, password, role):
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()

# App layout
st.set_page_config(page_title="LearnEase AI", page_icon="🧠")
st.title("🧠 LearnEase AI – Inclusive Classroom Assistant")

menu = ["Login", "Register"]
choice = st.sidebar.radio("Navigate", menu)

# Registration
if choice == "Register":
    st.subheader("Create Your Account")
    new_user = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    role = st.selectbox("You are a:", ["Student", "Teacher"])
    if st.button("Register"):
        add_user(new_user, new_password, role)
        st.success("🎉 Account created. You can now log in!")

# Login
elif choice == "Login" and not st.session_state.logged_in:
    st.subheader("Login to Continue")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        result = login_user(username, password)
        if result:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = result[2]
            st.experimental_rerun()
        else:
            st.error("❌ Incorrect username or password.")

# Logged-in users
if st.session_state.logged_in:
    st.success(f"Welcome {st.session_state.username}!")

    if st.session_state.role == "Student":
        st.header("👩‍🎓 Student Learning Assistant")

        # Learning style + mood
        style = st.selectbox("Preferred learning style", ["Text", "Visual", "Audio"])
        mood = st.selectbox("Current mood", ["🙂", "😐", "😕", "😠"])

        # Mock mode toggle
        mock_mode = st.checkbox("🔧 Enable Mock AI Mode (No API needed)", value=not api_key)

        st.divider()
        st.subheader("Ask your AI tutor:")

        user_input = st.text_input("Enter your question here 👇", key="student_question_input")
        submit = st.button("Submit Question")

        if submit and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.write(f"**You:** {user_input}")

            try:
                if mock_mode or not client:
                    reply = "📘 This is a mock response. The AI tutor is currently offline, but your curiosity is always online! 🚀"
                else:
                    with st.spinner("Thinking..."):
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": f"You are a helpful AI tutor for {style.lower()} learners."}
                            ] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                            temperature=0.7
                        )
                        reply = response.choices[0].message.content.strip()

                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.markdown(f"**AI Tutor:** {reply}")

            except Exception as e:
                if "insufficient_quota" in str(e).lower():
                    st.error("🚫 You’ve exceeded your OpenAI usage quota. Please check your [billing page](https://platform.openai.com/account/billing).")
                    st.info("Meanwhile, here's a sample response to keep you going:")
                    st.markdown("**AI Tutor:** Learning is a journey — even small steps lead to big discoveries! 🌟")
                elif "429" in str(e):
                    st.warning("⚠️ Too many requests. Please wait a few seconds before trying again.")
                else:
                    st.error(f"Unexpected AI error: {e}")

    elif st.session_state.role == "Teacher":
        st.header("👩‍🏫 Teacher Dashboard")
        df = pd.read_sql_query("SELECT username, style, mood FROM users WHERE role='Student'", conn)
        st.dataframe(df)

