
#Database Utility Class
import pandas as pd
from sqlalchemy.engine import create_engine
# Provides executable SQL expression construct
from sqlalchemy.sql import text
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np
import hashlib


#Defining Db Credentials
USER_NAME = 'postgres'
PASSWORD = '123'
PORT = 5432
DATABASE_NAME = 'postgres'
HOST = 'localhost'

#Note - Database should be created before executing below operation
#Initializing SqlAlchemy Postgresql Db Instance

db = create_engine("postgresql+psycopg2://postgres:123@localhost:5432/popular_movies")

if "logged_in" not in st.session_state.keys() or st.session_state["logged_in"] is False:
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
                st.experimental_rerun()
        elif choice == "SignUp":
            username = st.text_input(label = "Username", value="")
            password = st.text_input(label = "Password",value = "" ,type="password")
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
                st.experimental_rerun()
        

    
else:

    select_query_stmnt_genre = text( "select genre \
                                from genres\
                            where genres is not NULL ")
    connection = db.connect()
    result_gen = connection.execute(select_query_stmnt_genre)
    df = pd.DataFrame(result_gen.fetchall(),columns=result_gen.keys())
    arr = df.genre.values

    ###################################


    option = st.selectbox('select the genre you want to find best tag of', (arr))
    st.write('You selected:', option)

    genre_ = str(option)


    number = st.number_input('Enter the number of top tags to find', min_value= 1, step= 1)
    st.write('You chose ', number)



    select_query_stmnt_tag_gen = text( "select ge.genre, tg.tag, count(tg.tag) \
                            from genres as ge, tags as tg, movie_genres as mg\
                            where ge.genre_Id= mg.genre_Id and mg.movie_Id=tg.movie_Id and ge.genre=\'" + str(genre_) + 
                            "\' group by ge.genre,tg.tag\
                            order by count(tg.tag) DESC\
                            limit " + str(number) +  ";")
    connection = db.connect()
    result_tg = connection.execute(select_query_stmnt_tag_gen)
    df = pd.DataFrame(result_tg.fetchall(),columns=result_tg.keys())



    st.table(df)