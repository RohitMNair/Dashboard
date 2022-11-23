#Database Utility Class
import pandas as pd
from sqlalchemy.engine import create_engine
# Provides executable SQL expression construct
from sqlalchemy.sql import text
import pandas as pd
import streamlit as st
class PostgresqlDB:
    def __init__(self,user_name,password,host,port,db_name):
        self.user_name = user_name
        self.password = password
        self.host = host
        self.port = port
        self.db_name = db_name
        self.engine = self.create_db_engine()

    def create_db_engine(self):
        try:
            db_uri = 'postgresql+psycopg2://{user_name}:{password}@{host}:{port}/{db_name}'.format(
                      user_name=self.user_name,password=self.password,
                      host=self.host,db_name=self.db_name,port=self.port)
            return create_engine(db_uri)
        except Exception as err:
            raise RuntimeError(f'Failed to establish connection -- {err}') from err

    def execute_dql_commands(self,stmnt,values=None):
        """DQL - Data Query Language
           SQLAlchemy execute query by default as 
            BEGIN
            ....
            ROLLBACK
            BEGIN will be added implicitly everytime but if we don't mention commit or rollback eplicitly 
            then rollback will be appended at the end.
           We can execute only retrieval query with above transaction block.If we try to insert or update data 
           it will be rolled back.That's why it is necessary to use commit when we are executing 
           Data Manipulation Langiage(DML) or Data Definition Language(DDL) Query.
        """
        try:
            with self.engine.connect() as conn:
                if values is not None:
                    result = conn.execute(stmnt,values)
                else:
                    result = conn.execute(stmnt)
            return result
        except Exception as err:
            print(f'Failed to execute dql commands -- {err}')
    
    def execute_ddl_and_dml_commands(self,stmnt,values=None):
        connection = self.engine.connect()
        trans = connection.begin()
        try:
            if values is not None:
                result = connection.execute(stmnt,values)
            else:
                result = connection.execute(stmnt)
            trans.commit()
            connection.close()
            print('Command executed successfully.')
        except Exception as err:
            trans.rollback()
            print(f'Failed to execute ddl and dml commands -- {err}')


#Defining Db Credentials
USER_NAME = 'postgres'
PASSWORD = 'qwerty'
PORT = 5432
DATABASE_NAME = 'postgres'
HOST = 'localhost'

#Note - Database should be created before executing below operation
#Initializing SqlAlchemy Postgresql Db Instance
db = PostgresqlDB(user_name=USER_NAME,
                    password=PASSWORD,
                    host=HOST,port=PORT,
                    db_name=DATABASE_NAME)


select_query_stmnt = text("select * from flights;") 
result_1 = db.execute_dql_commands(select_query_stmnt)
df = pd.DataFrame(result_1.fetchall(),columns=result_1.keys())
print(df)

#from dash import Dash, dash_table


st.title('Uber pickups in NYC')
st.table(df)

from wordcloud import WordCloud

wc = WordCloud().fit_words({"A": 1, "B": 1, "C": 4,"D":1,})

st.image(wc.to_array())