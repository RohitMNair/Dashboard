import hashlib
import pandas as pd
from sqlalchemy.engine import create_engine
# Provides executable SQL expression construct
from sqlalchemy.sql import text
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu

db = create_engine("postgresql+psycopg2://postgres:123@localhost:5432/popular_movies")

st.title("Movie Modification")

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
        with st.form("modify_movie"):
            movies = connection.execute(text(
                "select title,year from movies;"
            ))
            movies = pd.DataFrame(movies.fetchall(), columns=movies.keys())
            movie_name = st.selectbox("Select movie name to update the rating",(movies.title.values))
            if str(movie_name).find('\'')>=0:
                str_n = list(movie_name)
                str_n.insert(movie_name.find("'"),'\\')
                movie_name = ''.join(str_n)
                movie_name = "E\'%"+str(movie_name)+"%\'"

            else:
                movie_name = "\'%"+str(movie_name)+"%\'"
            ratings = connection.execute(text(
                    f"select movies.title, ratings.user_id, ratings.movie_id, ratings.rating \
                    from ratings, movies \
                    where movies.title ilike {movie_name} and ratings.movie_id = movies.movie_id;"
                ))
            ratings = pd.DataFrame(ratings.fetchall(), columns=ratings.keys())
            movie_id = ratings.movie_id.values[0]
            user_id_to_modify_rating = int(st.selectbox(
                                        "Select the user ID whose rating is to be modified",
                                            ratings.user_id.values
                                        ))
            # old_rating_val = ratings.loc[ratings["user_id"] == user_id_to_modify_rating,"rating"].values
            # st.write(f"Old rating {old_rating_val[0]}")
            new_rating = float(st.selectbox("Enter the new rating",[0,0.5,1,1.5,2,2.5,3,3.5,4,4.5,5]))
            if st.form_submit_button("Update!"):
                connection.execute(text(
                        f"update ratings\
                        set rating = {new_rating}\
                        where user_id = {user_id_to_modify_rating} and movie_id = {movie_id};"
                    ))
                st.write("Rating Updated!")


        with st.form("read_rating"):
            movies = connection.execute(text(
                "select title,year from movies;"
            ))
            movies = pd.DataFrame(movies.fetchall(), columns=movies.keys())
            movie_name = st.selectbox("Select movie name to update the rating",(movies.title.values))
            if str(movie_name).find('\'')>=0:
                str_n = list(movie_name)
                str_n.insert(movie_name.find("'"),'\\')
                movie_name = ''.join(str_n)
                movie_name = "E\'%"+str(movie_name)+"%\'"

            else:
                movie_name = "\'%"+str(movie_name)+"%\'"
            ratings = connection.execute(text(
                    f"select movies.title, ratings.user_id, ratings.movie_id, ratings.rating \
                    from ratings, movies \
                    where movies.title ilike {movie_name} and ratings.movie_id = movies.movie_id;"
                ))
            ratings = pd.DataFrame(ratings.fetchall(), columns=ratings.keys())
            movie_id = ratings.movie_id.values[0]
            user_id_to_modify_rating = int(st.selectbox(
                                        "Select the user ID whose rating is to be modified",
                                            ratings.user_id.values
                                        ))
            if st.form_submit_button("Check!"):
                ratings = connection.execute(text(
                    f"select movies.title, ratings.user_id, ratings.movie_id, ratings.rating \
                    from ratings, movies \
                    where movies.title ilike {movie_name} and ratings.movie_id = movies.movie_id;"
                ))
                ratings = pd.DataFrame(ratings.fetchall(), columns=ratings.keys())
                old_rating_val = ratings.loc[ratings["user_id"] == user_id_to_modify_rating,"rating"].values
                st.write(f"rating {old_rating_val[0]}")
