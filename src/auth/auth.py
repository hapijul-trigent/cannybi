import streamlit as st
import bcrypt
import json
from datetime import datetime
from src.auth.hashing import hash_password, authenticate
# Load credentials from config file
def load_credentials(config_file="config.json"):
    with open(config_file, "r") as file:
        data = json.load(file)
    return data

# Save updated credentials to config file
def save_credentials(data, config_file="config.json"):
    with open(config_file, "w") as file:
        json.dump(data, file, indent=4)



# Admin feature to add a new user
def admin_add_user():
    st.subheader("Add a New User")
    with st.form("add_user_form"):
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        submitted = st.form_submit_button("Add User")
        
        if submitted:
            if new_username and new_password:
                if new_username in st.session_state["credentials"]["users"]:
                    st.error("User already exists!")
                else:
                    hashed_password = hash_password(new_password)
                    st.session_state["credentials"]["users"][new_username] = hashed_password
                    save_credentials(st.session_state["credentials"])
                    st.success(f"User '{new_username}' added successfully!")
            else:
                st.error("Both username and password are required!")

# Admin feature to remove an existing user
def admin_remove_user():
    st.subheader("Remove an Existing User")
    users = list(st.session_state["credentials"]["users"].keys())
    users.remove("admin")  # Prevent admin from being removed
    if users:
        with st.form("remove_user_form"):
            user_to_remove = st.selectbox("Select User to Remove", options=users)
            submitted = st.form_submit_button("Remove User")
            
            if submitted:
                if user_to_remove:
                    del st.session_state["credentials"]["users"][user_to_remove]
                    save_credentials(st.session_state["credentials"])
                    st.success(f"User '{user_to_remove}' removed successfully!")
                else:
                    st.error("Please select a user to remove.")
    else:
        st.write("No users available to remove.")


