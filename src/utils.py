import pandas as pd
import os
import shutil
import streamlit as st
from PIL import Image

def display_refrence_table(result):
    """
    Converts the given result dictionary to a Pandas DataFrame and displays it in Streamlit.

    Parameters:
    - result (list of dict): List containing sales data with 'City' and 'TotalSalesAmount'.

    Returns:
    - None (Displays DataFrame in Streamlit)
    """
    # Convert to DataFrame
    df = pd.DataFrame(result)

    # Display DataFrame in Streamlit
    st.subheader("📊 Reference Table")
    st.dataframe(df, use_container_width=True, hide_index=True)




def display_and_pin_charts(chart_dir="chart", pinned_dir="pinned_folder"):
    """
    Displays charts from the specified directory and allows users to pin images to a pinned folder.
    
    Args:
        chart_dir (str): Directory containing chart images.
        pinned_dir (str): Directory to save pinned chart images.
    """
    # Ensure the pinned directory exists
    if not os.path.exists(pinned_dir):
        os.makedirs(pinned_dir)

    with st.expander("📈 View Data Visualization Code"):
        # Check if the chart directory exists
        if not os.path.exists(chart_dir):
            st.error(f"📂 Chart directory `{chart_dir}` not found. Please ensure it exists.")
        else:
            # Get all image files in the chart directory
            chart_images = [f for f in os.listdir(chart_dir) if f.endswith((".png", ".jpg", ".jpeg"))]

            if not chart_images:
                st.warning("⚠️ No chart images found in the directory.")
            else:
                st.subheader("📊 Available Charts")

                # Arrange images in a 2x2 grid
                cols = st.columns(2)

                for i, chart in enumerate(chart_images):
                    chart_path = os.path.join(chart_dir, chart)
                    
                    with cols[i % 2]:  # Distribute images across 2 columns
                        st.image(chart_path, caption=f"📈 {chart.replace('_', ' ').title()}", use_column_width=True)

                        # Add "Pin" button for each chart
                        if st.button(f"📌 Pin {chart}", key=f"pin_{i}"):
                            pinned_chart_path = os.path.join(pinned_dir, chart)
                            image =  Image.open(chart_path)
                            image.save(pinned_chart_path)
                            print(pinned_chart_path)
                            st.success(f"✅ {chart} has been pinned successfully!")
                    
                    # Create a new row after every 2 images
                    if (i + 1) % 2 == 0:
                        st.write("")  # Add spacing



def display_pinned_charts(directory: str):
    """
    Displays pinned charts in a single-column format based on creation time (descending).
    
    Args:
        directory (str): Path to the directory containing chart images.
    """
    if not os.path.exists(directory):
        st.error(f"Directory '{directory}' does not exist.")
        return

    # Fetch chart image files and their creation times
    chart_files = [
        (file, os.path.getctime(os.path.join(directory, file)))
        for file in os.listdir(directory)
        if file.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]

    # Sort the files by creation time in descending order
    sorted_chart_files = sorted(chart_files, key=lambda x: x[1], reverse=True)

    # Display each chart in a single-column format
    with st.container():
        if not sorted_chart_files:
            st.info("No chart images found in the directory.")
        for file_name, _ in sorted_chart_files:
            chart_path = os.path.join(directory, file_name)
            
            # Display chart image and caption
            st.image(chart_path, caption=f"📈 {file_name.replace('_', ' ').title()}", use_column_width=True)
