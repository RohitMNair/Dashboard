import hashlib
import pandas as pd
import streamlit as st
from sqlalchemy.engine import create_engine
from sqlalchemy.sql import text
#Defining Db Credentials
USER_NAME = 'postgres'
PASSWORD = '123'
PORT = 5432
DATABASE_NAME = 'postgres'
HOST = 'localhost'

#Note - Database should be created before executing below operation
#Initializing SqlAlchemy Postgresql Db Instance
db = create_engine("postgresql+psycopg2://postgres:123@localhost:5432/popular_movies")

def make_hashes(str_to_hash):
    """
    function to hash a string
    params: str_to_hash (string)
    returns hashed string
    """
    return hashlib.sha256(str.encode(str_to_hash)).hexdigest()

def check_hashes(hash_to_match,str_to_hash_n_match):
    """
    function to check 2 strings match or not
    params: hash_to_match (string), str_to_hash_n_match(string)
    returns: bool
    """
    if make_hashes(str_to_hash_n_match) == hash_to_match:
        return True
    return False

choice = st.selectbox("Login or SignUp!",["Login","SignUp"])
with db.connect() as connection:
    if choice == "Login":
        username = st.text_input(label = "Username", value="")
        password = st.text_input(label = "Password",value = "" ,type="password")
        if st.button("Login!"):
            details = connection.execute(text(
                f"select username, password from usertable where username = '{username}';"
            ))
            df = pd.DataFrame(details.fetchall(),columns=details.keys())
            actual_pass = df["password"].values[0]
            if check_hashes(actual_pass, password):
                st.session_state["logged_in"] = True
                st.write("You are logged in")
            else:
                st.session_state["logged_in"] = False
                st.write("You are not logged in")
    elif choice == "SignUp":
        username = st.text_input(label = "Username", value="", key = "username")
        password = st.text_input(label = "Password",value = "" ,type="password", key="password")
        existing_details = connection.execute(text(
            f"select username, password from usertable where username = '{username}';"
        ))
        df = pd.DataFrame(existing_details.fetchall(),columns=existing_details.keys())
        if st.button("SignUp!"):
            if len(df.username) > 0:
                st.write("Username already exists")
            else:
                connection.execute(text(
                    f"INSERT INTO usertable (username, password) \
                        VALUES ('{username}','{make_hashes(password)}');"
                    ))
                st.write("User created")
