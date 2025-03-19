import streamlit as st


def apply_styles():
    st.markdown(
        """
        <style>
            .stApp {
                background-image: url('static/CanPrev_4D-background.jpg');
                background-size: cover;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }
        </style>
        """,
        unsafe_allow_html=True
    )



    # Apply custom styling
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

            
            html, body, [class*="st-"] {
                font-family: 'Poppins', sans-serif;
            }

            /* Style the title */
            .title {
                font-size: 28px !important;
                font-weight: 700 !important;
                color: #333333;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .user-info {
                display: flex;
                justify-content: flex-end;
                align-items: center;
                gap: 10px;
                font-size: 24px;
                font-weight: bold;
                padding: 20px 0 0 0;
                color: #626262;
                font-family: 'Poppins', sans-serif;
            }
            .logout-btn button {
                background-color: #13276e;
                color: white;
                border-radius: 8px;
                font-weight: bold;
                border: none;
                cursor: pointer;
                height: 40px;
                font-family: 'Poppins', sans-serif;
            }
            .logout-btn button:hover {
                background-color: #13276e;
            }
            .custom-title {
            font-family: 'Poppins', sans-serif;
            font-size: 32px;
            font-weight: 700;
            color: #333333;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
