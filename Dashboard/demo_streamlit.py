# import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

#Database Utility Class
from sqlalchemy.engine import create_engine
# Provides executable SQL expression construct
from sqlalchemy.sql import text
#import streamlit as st
    


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
if result_1 is not None:
    best_tag = {}
    for i in result_1:
        best_tag[i.tag] = i.relevance
    print(best_tag)
    # st.bar_chart(best_tag)
else:
    print("result is none")