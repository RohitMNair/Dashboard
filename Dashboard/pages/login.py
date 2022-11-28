import numpy as np
import pandas as pd
import streamlit as st
import hashlib
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

def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
	if hashed_text == password:
		return True
	return False
choice = st.selectbox("Login or SignUp!",["Login","SignUp"])
with db.connect() as connection:
    username = st.text_input("Username")
    password = st.text_input("Password",type="password")
    
    if choice == "Login":
        details = connection.execute(text(
            f"select username, password from usertable where username = '{username}';"
        ))
        df = pd.DataFrame(details.fetchall(),columns=details.keys())
        actual_pass = df["password"].values[0]
        if check_hashes(actual_pass, make_hashes(password)):
            st.session_state["logged_in"] = True
            st.write("You are logged in")
        else:
            st.session_state["logged_in"] = False
            st.write("YOu are not logged in")
    elif choice == "SignUp":
        connection.execute(text(
            f"INSERT INTO usertable (username, password) VALUES ('{username}','{make_hashes(password)}');"
        ))
        st.write("User created and logged in")
        st.session_state["logged_in"] = True
