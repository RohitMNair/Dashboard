#Database Utility Class
import pandas as pd
from sqlalchemy.engine import create_engine
# Provides executable SQL expression construct
from sqlalchemy.sql import text
import pandas as pd
import streamlit as st

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
st.sidebar()

from wordcloud import WordCloud

wc = WordCloud().fit_words({"A": 1, "B": 1, "C": 4,"D":1,})

st.image(wc.to_array())