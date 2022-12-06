
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