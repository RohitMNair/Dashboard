
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

st.table(df)