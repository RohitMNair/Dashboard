
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

#Defining Db Credentials
USER_NAME = 'postgres'
PASSWORD = '123'
PORT = 5432
DATABASE_NAME = 'postgres'
HOST = 'localhost'

#Note - Database should be created before executing below operation
#Initializing SqlAlchemy Postgresql Db Instance
db = create_engine("postgresql+psycopg2://postgres:123@localhost:5432/popular_movies")

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