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
import altair as alt
#from vega_datasets import data


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
        ratings_ar = [0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
        movie_rat_count_df = pd.DataFrame(columns = ['movie','rating','count'])
        
        arr1=[]
        for tit in movie_arr:
            x = connection.execute(text(
                "select rating, count(rating) from ratings where movie_id in (select movie_id from movies where title=\'"+tit+"\') group by rating;"
            ))
            df = pd.DataFrame(x.fetchall(),columns=x.keys())
            #val = df["count"].values
            #arr1 = []
            #arr1.append(tit)
            #st.write(arr1)
            for rat_type in ratings_ar:
                count_rat = 0
                if rat_type in df["rating"].values:
                    count_rat = df[df['rating']== rat_type]['count'].values[0]
                arr1.append([tit,rat_type, count_rat ])
                #movie_rat_count_df.loc[len(movie_rat_count_df.index)] = arr1
            #st.write( arr1.append([rat_type, count_rat ]))
        #st.write(arr1)

    movie_rat_count_df = pd.DataFrame(arr1,columns = ['movie','rating','count'])
    st.write(movie_rat_count_df) 

######################################################
    #source = data.barley()

    p=alt.Chart(movie_rat_count_df).mark_bar().encode(x='movie',y='sum(count)',color='rating').properties(width= 500, height=800)
    st.write(p)