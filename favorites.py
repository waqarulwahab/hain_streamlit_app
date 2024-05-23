import streamlit as st
import mysql.connector
import toml
from home import app, get_user_info
import time
from home import get_comments_for_recipe
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from streamlit_star_rating import st_star_rating



def connect_to_database():
    secrets = toml.load("streamlit/secrets.toml")
    mysql_config = secrets["connections"]["mysql"]
        
    return mysql.connector.connect(
        host=mysql_config["host"],
        port=mysql_config["port"],
        user=mysql_config["user"],
        password=mysql_config["password"],
        database=mysql_config["database"]
    )


def get_user_id():
    user_id = st.session_state.user_id
    return user_id
    
def get_liked_recipes(user_id):
    conn = connect_to_database()
    try:
        cursor = conn.cursor()
        query = "SELECT id, recipe_name, recipe_info FROM user_favorite_recipes WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        liked_recipes = cursor.fetchall()
        return liked_recipes
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if conn.is_connected(): 
            conn.close()
            
            
def remove_recipe(user_id, recipe_id):
    conn = connect_to_database()
    try:
        cursor = conn.cursor()
        query = "DELETE FROM user_favorite_recipes WHERE user_id = %s AND id = %s"
        cursor.execute(query, (user_id, recipe_id))
        conn.commit()
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.03)
            progress_bar.progress(i + 1)
        st.success("Recipe removed successfully!")    
        st.experimental_rerun()
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if conn.is_connected(): 
            conn.close()




def add_rating(meal_recipe_name, rating, add_comment_value):
    user_id, email = get_user_info()
    conn = connect_to_database()
    
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES LIKE 'ratings'")
    table_exists = cursor.fetchone()
    if not table_exists:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                email VARCHAR(255),
                recipe_name VARCHAR(255),
                rating INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        conn.commit()
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM ratings WHERE recipe_name = %s AND user_id = %s", (meal_recipe_name, user_id))
    existing_ratings_count = cursor.fetchone()[0]
    conn.close()

    if existing_ratings_count > 0:
        st.error("You have already rated on this recipe.")
        return

    add_button = st.button("Add", key=add_comment_value)
    if add_button:    
        conn = connect_to_database()
        try:
            cursor = conn.cursor()
            query = "INSERT INTO ratings (user_id, email, recipe_name, rating) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (user_id, email, meal_recipe_name, rating))
            conn.commit()
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.03)
                progress_bar.progress(i + 1)
            st.success('Rating added successfully')
            time.sleep(2)  
            st.experimental_rerun()          
        except mysql.connector.Error as e:
            st.error(f"Error: {e}")
        finally:
            cursor.close()
            conn.close()



def function_to_run_on_click(value):
    st.write(f"**{value}** stars!")

def generate_recipe_pdf(recipe_info, recipe_name):
    # Create a BytesIO buffer to store the PDF content
    from io import BytesIO
    buffer = BytesIO()
    
    # Create a canvas object with a larger width to accommodate longer text
    from reportlab.lib.pagesizes import letter, landscape
    c = canvas.Canvas(buffer, pagesize=landscape(letter))
    
    # Split recipe_info into lines
    lines = recipe_info.split("\n")
    
    # Calculate the height required for the text
    line_height = 15  # Adjust as needed
    total_height = len(lines) * line_height
    
    # Set the canvas size
    c.setPageSize((800, total_height))
    
    # Write recipe information to the PDF
    y = total_height - line_height  # Initial y coordinate
    for line in lines:
        c.drawString(100, y, line)
        y -= line_height  # Move to the next line
    
    # Save the PDF content
    c.save()
    
    # Get the value from the BytesIO buffer
    pdf_data = buffer.getvalue()
    
    # Close the buffer
    buffer.close()
    
    return pdf_data



def app():

    user_id, email = get_user_info()
    liked_recipes = get_liked_recipes(user_id)

    stars_selected = False
    label = "Rate this recipe?"
    amount_of_stars = 5
    default_value = 1
    size = 20
    emoticons = None



    if liked_recipes:
        st.write("My Liked Recipes:")
        for i, (recipe_id, meal_recipe_name, recipe_info) in enumerate(liked_recipes, start=1):
            with st.expander(meal_recipe_name):
                st.write(recipe_info)
                key_values = f"Fav_Recipe_{i}"

                # Create a column layout with two columns
                col1, col2 = st.columns([0.08, 1])

                # Column 1: "Remove" button
                with col1:
                    remove_fav = st.button("🗑️", key=key_values)
                    
                # Column 2: "Download Recipe as PDF" button
                with col2:
                    download_button = st.download_button(label="Download Recipe", data=generate_recipe_pdf(recipe_info, meal_recipe_name), file_name=f"{meal_recipe_name}-{i}.pdf")
                
                if remove_fav:
                    remove_recipe(user_id, recipe_id)

                # Add divider line
                st.markdown("<hr>", unsafe_allow_html=True)
                #download_button = st.download_button(label="Download Recipe", data=recipe_info, file_name=f"{meal_recipe_name}.txt")


                # col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
                col1, col2 = st.columns([1,1])
                with col2:
                    pass
                    rating_value = f"meal_rating-{i}"

                with col1:
                    rating = st_star_rating(label, amount_of_stars, default_value, size, emoticons, key=rating_value)
                    # rating = st_star_rating(label, amount_of_stars, default_value, size, emoticons, read_only, key=rating_value)
                    add_rating_value = f"add_rating_value_{i}"
                    add_rating(meal_recipe_name, rating, add_rating_value)  



                # Fetch comments for the specific meal recipe name
                comments_for_recipe = get_comments_for_recipe(meal_recipe_name)

                for comment in comments_for_recipe:
                    st.write(comment)



                    
    else:
        st.write("You haven't liked any recipes yet.")
