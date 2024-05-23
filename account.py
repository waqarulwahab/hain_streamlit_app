import streamlit as st
import mysql.connector
from main import connect_to_database
import time
import json
import requests
from streamlit_lottie import st_lottie
from streamlit_lottie import st_lottie_spinner



def update_user_info(first_name, new_lastname, user_id):
    db = connect_to_database()
    cursor = db.cursor()
    update_query = "UPDATE users SET first_name = %s , last_name = %s WHERE id = %s"
    cursor.execute(update_query, (first_name, new_lastname, user_id))
    db.commit()
    cursor.close()
    db.close()


@st.cache_data
def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        data = json.load(f)
    return data


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def get_user_id():
    user_id = st.session_state.user_id
    return user_id
    
def app():
        
    if 'user_id' in st.session_state:        
        user_id = st.session_state.user_id
        username = st.session_state.get('username', None)

        # username = st.session_state.username
        first_name = st.session_state.first_name
        last_name  = st.session_state.last_name
        email      = st.session_state.email

        col1, col2 = st.columns([1,2.1])
        with col1:
            lottie_file4 = './Animations/update.json'
            lottie_json4 = load_lottiefile(lottie_file4)
            st_lottie(
                lottie_json4,
                speed    = 1,
                reverse  = False,
                loop     = True,
                quality  = "low",
                height   = 300,
                width    = 250,
                key      = 'update', 
            )
        with col2:
            st.write("""
                <div style="background-color:#f0f0f0;padding:10px;border-radius:10px">
                    <h1 style="color:#333">Hi, {} {}!</h1>
                    <p style="font-size:26px;color:#666;margin-bottom:20px">User ID: {}</p>
                    <p style="font-size:26px;color:#666;margin-bottom:20px">UserName: {}</p>
                    <p style="font-size:28px;color:#555;margin-bottom:20px">Email: {}</p>
                </div>
            """.format(first_name, last_name, user_id, username, email ), unsafe_allow_html=True)  

        
        st.write("--------------------------------------------------------")
    
    
    with st.expander("Update Info"):
        col1 , col2 = st.columns(2)
        with col1:
            new_firstname = st.text_input("Enter First name:")
        with col2:    
            new_lastname  = st.text_input("Enter Last name:")
        
        if st.button("Update User Info"):
            # Check if new username is not empty
            if new_firstname.strip() == "" or new_lastname.strip() == "":
                st.error("Please enter a valid Name.")
            else:
                # Assuming you have stored the current username in session state
                current_username = st.session_state.username
                # Get user ID based on current username
                user_id = get_user_id()
                if user_id is not None:
                    # Update username in database
                    update_user_info(new_firstname, new_lastname, user_id)
                    
                    # Fetch updated information from the database
                    st.session_state.first_name = new_firstname
                    st.session_state.last_name  = new_lastname

                    # Display progress bar for 3 seconds
                    progress_bar = st.progress(0)
                    for i in range(100):
                        time.sleep(0.03)
                        progress_bar.progress(i + 1)
                    st.success("Name updated successfully!")
                    time.sleep(3)  
                    st.experimental_rerun()
                else:
                    st.error("User not found!")  # Handle the case if user is not found in database