# LearnEase AI - Streamlit App with Improved Login and Logout
import streamlit as st
import pandas as pd
import sqlite3
from openai import OpenAI

# Set page config
st.set_page_config(page_title="LearnEase AI", page_icon="🧠", layout="centered")

# Load OpenAI API key
api_key = st.secrets.get("OPENAI_API_KEY", None)
client = OpenAI(api_key=api_key) if api_key else None

# Database setup
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

# Session state defaults
if "page" not in st.session_state:
    st.session_state.page = "Login"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "messages" not in st.session_state:
    st.session_state.messages = []

def login_user(username, password):
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return cursor.fetchone()

def add_user(username, password, role):
    cursor.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()

def logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.messages = []
    st.session_state.page = "Login"
    st.rerun()

# Sidebar navigation
with st.sidebar:
    if st.session_state.logged_in:
        st.write(f"👤 Logged in as: {st.session_state.username}")
        if st.button("🔓 Logout"):
            logout()
    else:
        st.session_state.page = st.radio("Navigation", ["Login", "Register"])

# Login Page
if st.session_state.page == "Login" and not st.session_state.logged_in:
    st.subheader("🔐 Login")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        result = login_user(username, password)
        if result:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.role = result[2]
            st.session_state.page = "Home"
            st.success("✅ Logged in successfully")
            st.rerun()
        else:
            st.error("❌ Invalid username or password.")

# Register Page
if st.session_state.page == "Register" and not st.session_state.logged_in:
    st.subheader("📝 Register")
    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")
    role = st.selectbox("Role", ["Student", "Teacher"])
    if st.button("Register"):
        add_user(new_user, new_pass, role)
        st.success("✅ Registration successful. Redirecting to login...")
        st.session_state.page = "Login"
        st.experimental_rerun()

# Home Page
if st.session_state.logged_in and st.session_state.page == "Home":
    st.title("🧠 LearnEase AI – Inclusive Learning Assistant")

    if st.session_state.role == "Student":
        style = st.selectbox("Learning Style", ["Text", "Visual", "Audio"])
        mood = st.selectbox("Mood", ["🙂", "😐", "😕", "😠"])
        mock_mode = st.checkbox("Mock AI Mode", value=not api_key)
        user_input = st.text_input("Ask your question:")
        if st.button("Submit") and user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            try:
                if mock_mode or not client:
                    reply = "This is a mock response. Your AI tutor is offline, but your brain isn't! 🚀"
                else:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": f"You're a helpful tutor for {style} learners."}
                        ] + st.session_state.messages,
                        temperature=0.7
                    )
                    reply = response.choices[0].message.content.strip()
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.markdown(f"**AI Tutor:** {reply}")
            except Exception as e:
                if "insufficient_quota" in str(e):
                    st.error("🚫 Quota exceeded. Check your OpenAI billing settings.")
                    st.markdown("**AI Tutor:** Learning is a journey — small steps matter! 🌟")
                else:
                    st.error(f"Unexpected error: {e}")

    elif st.session_state.role == "Teacher":
        st.subheader("👩‍🏫 Student Overview")
        df = pd.read_sql_query("SELECT username, style, mood FROM users WHERE role='Student'", conn)
        st.dataframe(df)




