# import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

#Database Utility Class
from sqlalchemy.engine import create_engine
# Provides executable SQL expression construct
from sqlalchemy.sql import text
# import streamlit as st
    
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
PASSWORD = '123'
PORT = 5432
DATABASE_NAME = 'postgres'
HOST = 'localhost'
#Note - Database should be created before executing below operation
#Initializing SqlAlchemy Postgresql Db Instance
db = PostgresqlDB(user_name=USER_NAME,
                    password=PASSWORD,
                    host=HOST,port=PORT,
                    db_name=DATABASE_NAME)
select_query_stmnt = text("select gt.tag as tag,gs.relevance as relevance\
                        from genome_tags as gt, genome_scores as gs \
                        where gs.movie_id = (select mv.movie_id \
					    from movies as mv \
					    where movie_name = 'Jumanji ') and gs.tag_id = gt.tag_id \
                        ORDER BY gs.relevance DESC LIMIT 5;")
result_1 = db.execute_dql_commands(select_query_stmnt)
if result_1 is not None:
    best_tag = {}
    for i in result_1:
        best_tag[i.tag] = i.relevance
    print(best_tag)
    # st.bar_chart(best_tag)
else:
    print("result is none")