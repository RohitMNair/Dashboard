import hashlib
import pandas as pd
from sqlalchemy.engine import create_engine
# Provides executable SQL expression construct
from sqlalchemy.sql import text
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
from wordcloud import WordCloud

db = create_engine("postgresql+psycopg2://postgres:123@localhost:5432/popular_movies")

st.header("Top 5 tags of a movie based on relevance score")

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
            username = st.text_input(label = "Username", value="")
            password = st.text_input(label = "Password",value = "" ,type="password")
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
    with db.connect() as connection:
        movie_name = st.text_input("Enter movie name you want the find the 5 most relevant tags")
        if str(movie_name).find('\'')>=0:
            str_n = list(movie_name)
            str_n.insert(movie_name.find("'"),'\\')
            movie_name = ''.join(str_n)
            movie_name = "E\'%"+str(movie_name)+"%\'"

        else:
            movie_name = "\'%"+str(movie_name)+"%\'"

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