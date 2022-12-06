
#Database Utility Class
import pandas as pd
from sqlalchemy.engine import create_engine
# Provides executable SQL expression construct
from sqlalchemy.sql import text
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np
import altair as alt
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



    movie_name = st.text_input("Enter movie name you want the rating distribution of")
    if str(movie_name).find('\'')>=0:
        str_n = list(movie_name)
        str_n.insert(movie_name.find("'"),'\\')
        movie_name = ''.join(str_n)
        movie_name = "E\'%"+str(movie_name)+"%\'"

    else:
        movie_name = "\'%"+str(movie_name)+"%\'"

    connection = db.connect()
    matched_mnames = connection.execute(text(
        f"select title, movie_id\
        from movies\
        where title ilike {movie_name}"
    ))
    df = pd.DataFrame(matched_mnames.fetchall(),columns=matched_mnames.keys())
    arr = df["title"].values
    option1 = st.selectbox('select the movie', (arr))
    st.write('You selected:', option1)


    mov_id = df[df['title'] == option1]['movie_id'].values[0]

    ###################################




    select_query_stmnt_rate = text( "select distinct rating,count(user_id)\
                                        from ratings\
                                        where movie_id= " + str(mov_id) +
                                        " group by distinct rating\
                                        order by rating DESC;")
    connection = db.connect()
    result_rate = connection.execute(select_query_stmnt_rate)
    df = pd.DataFrame(result_rate.fetchall(),columns=result_rate.keys())


    st.text("Following are the ratings and their corresponding counts:")
    st.table(df)

    st.text("The distribution of the ratings:")
    st.line_chart(df, x = 'rating', y = 'count')

    # c = alt.Chart(df).mark_circle().encode(
    #     x='rating', y='count', color='c', tooltip=['count'])

    # st.altair_chart(c, use_container_width=True)


    st.header("Compare two movies")


    col1, col2= st.columns((1,1))

    with col1:


                movie_name = st.text_input("Enter first movie name")
                if str(movie_name).find('\'')>=0:
                    str_n = list(movie_name)
                    str_n.insert(movie_name.find("'"),'\\')
                    movie_name = ''.join(str_n)
                    movie_name = "E\'%"+str(movie_name)+"%\'"

                else:
                    movie_name = "\'%"+str(movie_name)+"%\'"

                connection = db.connect()
                matched_mnames = connection.execute(text(
                    f"select title, movie_id\
                    from movies\
                    where title ilike {movie_name}"
                ))
                df = pd.DataFrame(matched_mnames.fetchall(),columns=matched_mnames.keys())
                arr = df["title"].values
                option1 = st.selectbox('select the first movie', (arr))
                st.write('You selected:', option1)


                mov_id = df[df['title'] == option1]['movie_id'].values[0]

                ###################################




                select_query_stmnt_rate = text( "select distinct rating,count(user_id)\
                                                    from ratings\
                                                    where movie_id= " + str(mov_id) +
                                                    " group by distinct rating\
                                                    order by rating DESC;")
                connection = db.connect()
                result_rate = connection.execute(select_query_stmnt_rate)
                df = pd.DataFrame(result_rate.fetchall(),columns=result_rate.keys())


                #st.text("Following are the ratings and their corresponding counts:")
                #st.table(df)

                st.text("The distribution of the ratings:")
                st.line_chart(df, x = 'rating', y = 'count')




    with col2:


                movie_name = st.text_input("Enter second movie ")
                if str(movie_name).find('\'')>=0:
                    str_n = list(movie_name)
                    str_n.insert(movie_name.find("'"),'\\')
                    movie_name = ''.join(str_n)
                    movie_name = "E\'%"+str(movie_name)+"%\'"

                else:
                    movie_name = "\'%"+str(movie_name)+"%\'"

                connection = db.connect()
                matched_mnames = connection.execute(text(
                    f"select title, movie_id\
                    from movies\
                    where title ilike {movie_name}"
                ))
                df = pd.DataFrame(matched_mnames.fetchall(),columns=matched_mnames.keys())
                arr = df["title"].values
                option1 = st.selectbox('select the second movie', (arr))
                st.write('You selected:', option1)


                mov_id = df[df['title'] == option1]['movie_id'].values[0]

                ###################################




                select_query_stmnt_rate = text( "select distinct rating,count(user_id)\
                                                    from ratings\
                                                    where movie_id= " + str(mov_id) +
                                                    " group by distinct rating\
                                                    order by rating DESC;")
                connection = db.connect()
                result_rate = connection.execute(select_query_stmnt_rate)
                df = pd.DataFrame(result_rate.fetchall(),columns=result_rate.keys())


                #st.text("Following are the ratings and their corresponding counts:")
                #st.table(df)

                st.text("The distribution of the ratings:")
                st.line_chart(df, x = 'rating', y = 'count')