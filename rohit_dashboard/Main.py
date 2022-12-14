#Database Utility Class
import hashlib
import pandas as pd
from sqlalchemy.engine import create_engine
# Provides executable SQL expression construct
from sqlalchemy.sql import text
import streamlit as st
from streamlit_option_menu import option_menu

########################################
#Initializing SqlAlchemy Postgresql Db Instance
db = create_engine("postgresql+psycopg2://postgres:123@localhost:5432/popular_movies")

############    Intro

##########################################################

##########################################################

st.title("Overall Best Movie and yearwise top 10 movies")

##########################################################

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
    ##########################################################
    with db.connect() as connection:

        best_movie = connection.execute(text(
            "select m.title as title \
            from movies m, ratings r \
            where m.movie_id = r.movie_id \
            group by m.movie_id, m.title \
            order by count(r.rating) DESC, avg(r.rating) desc \
            limit 10;"
        ))
        df = pd.DataFrame(best_movie.fetchall(),columns=best_movie.keys())
        st.header("Overall top 10 movies")
        st.table(df)
    ###########################################################

        select_query_stmnt_year = text( "select year \
                                    from movies\
                                where year is not NULL\
                                group by year \
                                order by year asc;")
    
        result_yr = connection.execute(select_query_stmnt_year)
        df = pd.DataFrame(result_yr.fetchall(),columns=result_yr.keys())
        arr = df.year.values
        st.header("year-wise top 10 movies")
        option = st.selectbox('select the year you want the find the 10 best movies wrt ratings', (arr))
        st.write('You selected:', option)

    ####################################
        
        year = str(option)
        new_query = "select title from movies as mo where movie_id in \
                        ( select rt.movie_id  from ratings as rt where movie_id in\
                        (select movie_id from movies as mv where year = " + " " + year + " " + ") group by rt.movie_id order by avg(rating) desc limit 10)"

        result_yr = connection.execute(text(new_query))
        df = pd.DataFrame(result_yr.fetchall(),columns=result_yr.keys())
        st.table(df.title.values)