#Database Utility Class
import pandas as pd
from sqlalchemy.engine import create_engine
# Provides executable SQL expression construct
from sqlalchemy.sql import text
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np



#Defining Db Credentials
USER_NAME = 'postgres'
PASSWORD = '123'
PORT = 5432
DATABASE_NAME = 'postgres'
HOST = 'localhost'

#Note - Database should be created before executing below operation
#Initializing SqlAlchemy Postgresql Db Instance
db = create_engine("postgresql+psycopg2://postgres:123@localhost:5432/popular_movies")

with db.connect() as connection:
    select_query_stmnt_year = text( "select year \
                                from movies\
                            where year is not NULL\
                            group by year \
                            order by year asc;")
    result_yr = connection.execute(select_query_stmnt_year)
    df = pd.DataFrame(result_yr.fetchall(),columns=result_yr.keys())
    arr = df.year.values
    option = st.selectbox('select the year you want the find the 10 best movies wrt ratings', (arr))
    st.write('You selected:', option)

    year = str(option)

    new_query = "select ge.genre,count(mg.movie_id)\
                from genres as ge, movie_genres as mg, movies as mo\
                where ge.genre_id = mg.genre_id and mo.movie_id = mg.movie_id and year= " \
                + year +  " group by mg.genre_id,ge.genre order by count(mg.movie_id) desc limit 10; "

    result_yr = connection.execute(text(new_query))
    df = pd.DataFrame(result_yr.fetchall(),columns=result_yr.keys())

    st.table(df)




