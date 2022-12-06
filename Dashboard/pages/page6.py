#Database Utility Class
import hashlib
import pandas as pd
from sqlalchemy.engine import create_engine
# Provides executable SQL expression construct
from sqlalchemy.sql import text
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np


########################################################
######################    ... e ... #########################
#######################################################

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
                st.experimental_rerun()
else:
    movie_arr = []

    #movie_num = st.number_input("Enter the number of movies to compare")

    with db.connect() as connection:
        matched_mnames = connection.execute(text(
                    "select title\
                    from movies"
                ))
        df = pd.DataFrame(matched_mnames.fetchall(),columns=matched_mnames.keys())
        arr = df["title"].values

        st.header("Select the movies for comparing total ratings")
        movie_arr = st.multiselect("Selected Movies:",arr)

    st.write(movie_arr)

    avg_rate=[]
    with db.connect() as connection:

        for tit in movie_arr:
            x = connection.execute(text(
                "select avg(rating) from ratings where movie_id in (select movie_id from movies where title=\'"+tit+"\');"
            ))
            df = pd.DataFrame(x.fetchall(),columns=x.keys())
            val = df["avg"].values[0]
            avg_rate.append(val)


    st.write(avg_rate)


    dataf = pd.DataFrame({'name' : movie_arr, 'avg_rate': avg_rate})
    st.header("The total average rating of selected movies")
    st.bar_chart(dataf, x = 'name', y= 'avg_rate')
















# for i in range (int(movie_num)):
#     with db.connect() as connection:
#         movie_name = st.text_input("Enter movie name you want the find the 5 most relevant tags")
#         if str(movie_name).find('\'')>=0:
#             str_n = list(movie_name)
#             str_n.insert(movie_name.find("'"),'\\')
#             movie_name = ''.join(str_n)
#             movie_name = "E\'%"+str(movie_name)+"%\'"

#         else:
#             movie_name = "\'%"+str(movie_name)+"%\'"

        
#         matched_mnames = connection.execute(text(
#                 f"select title\
#                 from movies\
#                 where title ilike {movie_name}"
#             ))
#         df = pd.DataFrame(matched_mnames.fetchall(),columns=matched_mnames.keys())
#         arr = df["title"].values

#     movie_arr.append(st.multiselect("Select Movies:",arr))
#     # option1 = st.selectbox('select the movie', (arr))
    
# st.write(movie_arr)