import hashlib
import pandas as pd
from sqlalchemy.engine import create_engine
# Provides executable SQL expression construct
from sqlalchemy.sql import text
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

db = create_engine("postgresql+psycopg2://postgres:123@localhost:5432/popular_movies")



with db.connect() as connection:
    with st.form("modify_movie"):
        movies = connection.execute(text(
            "select title,year from movies;"
        ))
        movies = pd.DataFrame(movies.fetchall(), columns=movies.keys())
        movie_name = st.selectbox("Select movie name to update the rating",(movies.title.values))
        if str(movie_name).find('\'')>=0:
            str_n = list(movie_name)
            str_n.insert(movie_name.find("'"),'\\')
            movie_name = ''.join(str_n)
            movie_name = "E\'%"+str(movie_name)+"%\'"

        else:
            movie_name = "\'%"+str(movie_name)+"%\'"
        ratings = connection.execute(text(
                f"select movies.title, ratings.user_id, ratings.movie_id, ratings.rating \
                from ratings, movies \
                where movies.title ilike {movie_name} and ratings.movie_id = movies.movie_id;"
            ))
        ratings = pd.DataFrame(ratings.fetchall(), columns=ratings.keys())
        movie_id = ratings.movie_id.values[0]
        user_id_to_modify_rating = int(st.selectbox(
                                    "Select the user ID whose rating is to be modified",
                                        ratings.user_id.values
                                    ))
        # old_rating_val = ratings.loc[ratings["user_id"] == user_id_to_modify_rating,"rating"].values
        # st.write(f"Old rating {old_rating_val[0]}")
        new_rating = float(st.selectbox("Enter the new rating",[0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5]))
        if st.form_submit_button("Update!"):
            connection.execute(text(
                    f"update ratings\
                    set rating = {new_rating}\
                    where user_id = {user_id_to_modify_rating} and movie_id = {movie_id};"
                ))
            st.write("Rating Updated!")


    with st.form("read_rating"):
        movies = connection.execute(text(
            "select title,year from movies;"
        ))
        movies = pd.DataFrame(movies.fetchall(), columns=movies.keys())
        movie_name = st.selectbox("Select movie name to update the rating",(movies.title.values))
        if str(movie_name).find('\'')>=0:
            str_n = list(movie_name)
            str_n.insert(movie_name.find("'"),'\\')
            movie_name = ''.join(str_n)
            movie_name = "E\'%"+str(movie_name)+"%\'"

        else:
            movie_name = "\'%"+str(movie_name)+"%\'"
        ratings = connection.execute(text(
                f"select movies.title, ratings.user_id, ratings.movie_id, ratings.rating \
                from ratings, movies \
                where movies.title ilike {movie_name} and ratings.movie_id = movies.movie_id;"
            ))
        ratings = pd.DataFrame(ratings.fetchall(), columns=ratings.keys())
        movie_id = ratings.movie_id.values[0]
        user_id_to_modify_rating = int(st.selectbox(
                                    "Select the user ID whose rating is to be modified",
                                        ratings.user_id.values
                                    ))
        if st.form_submit_button("Check!"):
            ratings = connection.execute(text(
                f"select movies.title, ratings.user_id, ratings.movie_id, ratings.rating \
                from ratings, movies \
                where movies.title ilike {movie_name} and ratings.movie_id = movies.movie_id;"
            ))
            ratings = pd.DataFrame(ratings.fetchall(), columns=ratings.keys())
            old_rating_val = ratings.loc[ratings["user_id"] == user_id_to_modify_rating,"rating"].values
            st.write(f"rating {old_rating_val[0]}")
