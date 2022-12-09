import hashlib
import pandas as pd
from sqlalchemy.engine import create_engine
# Provides executable SQL expression construct
from sqlalchemy.sql import text
import streamlit as st
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt



#Note - Database should be created before executing below operation
#Initializing SqlAlchemy Postgresql Db Instance
db = create_engine("postgresql+psycopg2://postgres:123@localhost:5432/popular_movies")


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
    with db.connect() as connection:
        res = connection.execute(text(
            "select mo.title, g.genre\
            from movies mo, movie_genres mg, genres g\
            where mo.movie_id = mg.movie_id \
            and g.genre_id = mg.genre_id\
            and mo.movie_id in \
            (select m.movie_id\
            from movies m , ratings r\
            where m.movie_id = r.movie_id \
            group by m.movie_id, m.title \
            order by count(rating) desc, avg(rating) DESC \
            LIMIT 100);"
        ))
        df = pd.DataFrame(res.fetchall(),columns=res.keys())
        fig, ax = plt.subplots()
        ax.set_xlabel(xlabel="Genres")
        ax.set_ylabel(ylabel="frequency")
        df['genre'].value_counts().plot(ax=ax, kind='bar', xlabel='numbers', ylabel='frequency')
        ax.tick_params(axis='x', labelrotation = 90)
        st.pyplot(fig = fig)
        st.write("This is the frequency distribution of genres of top 100 movies \
        it can be observed that genres like action, Drama and adventure are the most \
        prevalent genres is top movies.")
        # st.table(df)