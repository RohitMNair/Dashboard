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




with st.sidebar:
    selected = option_menu("Main Menu", ["Home", 'Settings'], 
        icons=['house', 'gear'], menu_icon="cast", default_index=1)
    selected

#######################################
movie_name = st.text_input("Enter movie name you want the find the 5 most relevant tags")
if str(movie_name).find('\'')>=0:
    str_n = list(movie_name)
    str_n.insert(movie_name.find("'"),'\\')
    movie_name = ''.join(str_n)
    movie_name = "E\'%"+str(movie_name)+"%\'"

else:
    movie_name = "\'%"+str(movie_name)+"%\'"

connection = db.connect()
matched_mnames = connection.execute(text(
    f"select title\
    from movies\
    where title ilike {movie_name}"
))
df = pd.DataFrame(matched_mnames.fetchall(),columns=matched_mnames.keys())
arr = df["title"].values


option1 = st.selectbox('select the movie you want the find the 5 most relevant tags', (arr))
st.write('You selected:', option1)

if str(option1).find('\'')>=0:
    str_n = list(option1)
    str_n.insert(option1.find("'"),'\\')
    option1 = ''.join(str_n)
    option1 = "E\'"+str(option1)+"\'"

else:
    option1 = "\'"+str(option1)+"\'"

select_query_stmnt = text("select gt.tag as tag,gs.relevance as relevance\
                        from genome_tags as gt, genome_scores as gs \
                        where gs.movie_id = (select mv.movie_id \
					    from movies as mv \
					    where title = " + option1 + " ) and gs.tag_id = gt.tag_id \
                        ORDER BY gs.relevance DESC LIMIT 5;")


result_2 = connection.execute(select_query_stmnt)
df = pd.DataFrame(result_2.fetchall(),columns=result_2.keys())

st.table(df)
st.bar_chart(df['relevance'])


dict_ = dict(zip(df.tag,df.relevance))


from wordcloud import WordCloud



try:
    wc = WordCloud().fit_words(dict_)
    st.image(wc.to_array())
except ValueError:
  # Prevent the error from propagating into your Streamlit app.
  st.write("Nothing to show.... No tags for that particular movie")


##########################################################

select_query_stmnt_year = text( "select year \
                            from movies\
                        where year is not NULL\
                        group by year \
                        order by year asc;")
connection = db.connect()
result_yr = connection.execute(select_query_stmnt_year)
df = pd.DataFrame(result_yr.fetchall(),columns=result_yr.keys())
arr = df.year.values


option = st.selectbox('select the year you want the find the 10 best movies wrt ratings', (arr))
st.write('You selected:', option)

####################################


year = str(option)


new_query = "select title from movies as mo where movie_id in \
                ( select rt.movie_id  from ratings as rt where movie_id in\
                 (select movie_id from movies as mv where year = " + " " + year + " " + ") group by rt.movie_id order by avg(rating) desc limit 10)"

connection = db.connect()
result_yr = connection.execute(text(new_query))
df = pd.DataFrame(result_yr.fetchall(),columns=result_yr.keys())
arr = df.title.values

st.table(df)

#######################################################################################




def main_page():
    st.markdown("# Main page 🎈")
    st.sidebar.markdown("# Main page 🎈")

def page2():
    st.markdown("# Page 2 ❄️")
    st.sidebar.markdown("# Page 2 ❄️")

def page3():
    st.markdown("# Page 3 🎉")
    st.sidebar.markdown("# Page 3 🎉")

page_names_to_funcs = {
    "Main Page": main_page,
    "Page 2": page2,
    "Page 3": page3,
}

selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()