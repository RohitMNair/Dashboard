#Database Utility Class
import pandas as pd
from sqlalchemy.engine import create_engine
# Provides executable SQL expression construct
from sqlalchemy.sql import text
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np

from wordcloud import WordCloud


#Defining Db Credentials
USER_NAME = 'postgres'
PASSWORD = '123'
PORT = 5432
DATABASE_NAME = 'postgres'
HOST = 'localhost'

#Note - Database should be created before executing below operation
#Initializing SqlAlchemy Postgresql Db Instance
db = create_engine("postgresql+psycopg2://postgres:123@localhost:5432/popular_movies")

select_query_stmnt = text("select gt.tag as tag,gs.relevance as relevance\
                        from genome_tags as gt, genome_scores as gs \
                        where gs.movie_id = (select mv.movie_id \
					    from movies as mv \
					    where movie_name = 'Jumanji ') and gs.tag_id = gt.tag_id \
                        ORDER BY gs.relevance DESC LIMIT 5;")

connection = db.connect()
result_1 = connection.execute(select_query_stmnt)
df = pd.DataFrame(result_1.fetchall(),columns=result_1.keys())
# print(df)s

#from dash import Dash, dash_table


# st.title('Uber pickups in NYC')
st.table(df)
st.bar_chart(df['relevance'])
with st.sidebar:
    selected = option_menu("Main Menu", ["Home", 'Settings'], 
        icons=['house', 'gear'], menu_icon="cast", default_index=1)
    selected

select_query_stmnt_year = text( "select year_released \
                            from movies\
                        where year_released is not NULL\
                        group by year_released \
                        order by year_released asc;")
connection = db.connect()
result_yr = connection.execute(select_query_stmnt_year)
df = pd.DataFrame(result_yr.fetchall(),columns=result_yr.keys())
arr = df.year_released.values


option = st.selectbox('select the year you want the find the 10 best movies wrt ratings', (arr))
st.write('You selected:', option)




wc = WordCloud().fit_words({"A": 1, "B": 1, "C": 4,"D":1,})

st.image(wc.to_array())