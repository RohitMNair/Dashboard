#Database Utility Class
import hashlib
import pandas as pd
from sqlalchemy.engine import create_engine
# Provides executable SQL expression construct
from sqlalchemy.sql import text
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import numpy as np
from wordcloud import WordCloud
########################################

#Theme

primaryColor="#d33682"
backgroundColor="#002b36"
secondaryBackgroundColor="#586e75"
textColor="#fafafa"
font="sans serif"


#########################################



##Defining Db Credentials
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




############    Intro

##########################################################

##########################################################

st.header("Movie Database")

##########################################################

if "logged_in" not in st.session_state.keys() or st.session_state["logged_in"] is False:     
    def make_hashes(str_to_hash):
        """
        function to hash a string
        params: str_to_hash (string)
        returns hashed string
        """
        return hashlib.sha256(str.encode(str_to_hash)).hexdigest()

    def check_hashes(hash_to_match,str_to_hash_n_match):
        """
        function to check 2 strings match or not
        params: hash_to_match (string), str_to_hash_n_match(string)
        returns: bool
        """
        if make_hashes(str_to_hash_n_match) == hash_to_match:
            return True
        return False

    choice = st.selectbox("Login or SignUp!",["Login","SignUp"])
    with db.connect() as connection:
        if choice == "Login":
            username = st.text_input(label = "Username", value="")
            password = st.text_input(label = "Password",value = "" ,type="password")
            if st.button("Login!"):
                details = connection.execute(text(
                    f"select username, password from usertable where username = '{username}';"
                ))
                df = pd.DataFrame(details.fetchall(),columns=details.keys())
                actual_pass = df["password"].values[0]
                if check_hashes(actual_pass, password):
                    st.session_state["logged_in"] = True
                    st.write("You are logged in")
                else:
                    st.session_state["logged_in"] = False
                    st.write("You are not logged in")
                st.experimental_rerun()

        elif choice == "SignUp":
            username = st.text_input(label = "Username", value="", key = "username")
            password = st.text_input(label = "Password",value = "" ,type="password", key="password")
            existing_details = connection.execute(text(
                f"select username, password from usertable where username = '{username}';"
            ))
            df = pd.DataFrame(existing_details.fetchall(),columns=existing_details.keys())
            if st.button("SignUp!"):
                if len(df.username) > 0:
                    st.write("Username already exists")
                else:
                    connection.execute(text(
                        f"INSERT INTO usertable (username, password) \
                            VALUES ('{username}','{make_hashes(password)}');"
                        ))
                    st.write("User created")
                st.experimental_rerun()
                
    
else:
    ##########################################################
    with db.connect() as connection:

        best_movie = connection.execute(text(
            "select m.movie_id as movie_id, m.title as title \
            from movies m, ratings r \
            where m.movie_id = r.movie_id \
            group by m.movie_id \
            order by count(r.rating) DESC, avg(r.rating) desc \
            limit 10;"
        ))
        df = pd.DataFrame(best_movie.fetchall(),columns=best_movie.keys())
        st.write("The best movie is ", df["title"].values[0])
    ###########################################################

    select_query_stmnt_year = text( "select year \
                                from movies\
                            where year is not NULL\
                            group by year \
                            order by year asc;")

    with db.connect() as connection:
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

        result_yr = connection.execute(text(new_query))
        df = pd.DataFrame(result_yr.fetchall(),columns=result_yr.keys())
        arr = df.title.values

        st.table(df)

    #######################################################################################

    movie_name = st.text_input("Enter movie name you want the find the 5 most relevant tags")
    if str(movie_name).find('\'')>=0:
        str_n = list(movie_name)
        str_n.insert(movie_name.find("'"),'\\')
        movie_name = ''.join(str_n)
        movie_name = "E\'%"+str(movie_name)+"%\'"

    else:
        movie_name = "\'%"+str(movie_name)+"%\'"

    with db.connect() as connection:
        matched_mnames = connection.execute(text(
            f"select title\
            from movies\
            where title ilike {movie_name}"
        ))
        df = pd.DataFrame(matched_mnames.fetchall(),columns=matched_mnames.keys())
        arr = df["title"].values


        option1 = st.selectbox('select the movie', (arr))
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

        try:
            wc = WordCloud().fit_words(dict_)
            st.image(wc.to_array())
        except ValueError:
            # Prevent the error from propagating into your Streamlit app.
            st.write("Nothing to show.... No tags for that particular movie")

    ############################################################################


    def main_page():
        st.markdown("# Main page ????")
        st.sidebar.markdown("# Main page ????")

    def page2():
        st.markdown("# Page 2 ??????")
        st.sidebar.markdown("# Page 2 ??????")

    def page3():
        st.markdown("# Page 3 ????")
        st.sidebar.markdown("# Page 3 ????")

    page_names_to_funcs = {
        "Main Page": main_page,
        "Page 2": page2,
        "Page 3": page3,
    }

    selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
    page_names_to_funcs[selected_page]()
