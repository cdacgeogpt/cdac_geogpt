import streamlit as st
import os
from pathlib import Path
from src.pdf_utils import extract_images_text_pdf, count_pdf_pages  # Assuming these functions already exist
from streamlit_pdf_viewer import pdf_viewer
import logging
import shutil
import zipfile
from io import BytesIO

# Constants
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
path = Path(ROOT_DIR)
TMP_FOLDER = os.path.join(path.parent.absolute(), "tmp")
os.makedirs(TMP_FOLDER, exist_ok=True)

# Function to extract images from a PDF
def extract_images_from_pdf(uploaded_file_path, output_folder):
    """
    Extract images and text from a PDF file and display them in the Streamlit app.

    Args:
        uploaded_file_path (str): Path to the uploaded PDF file.
        output_folder (str): Path to the folder where extracted images will be saved.
    """
    # Clear the previous extraction folder
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    try:
        # Extract images and text from the PDF
        extracted_text = extract_images_text_pdf(
            path=uploaded_file_path,
            image_path=output_folder,
            export_images=True,
        )
        logging.info(f"Extraction complete. Text and images saved to {output_folder}")

        # Display extracted images
        st.subheader("Extracted Images:")
        image_files = [
            os.path.join(output_folder, img)
            for img in os.listdir(output_folder)
            if img.endswith((".png", ".jpg", ".jpeg"))
        ]
        if image_files:
            for img_path in image_files:
                # Set the width to 500 pixels or adjust as necessary
                st.image(img_path, caption=os.path.basename(img_path), use_container_width=500)
        else:
            st.info("No images found in the document.")

        return image_files

    except Exception as e:
        logging.error(f"Error during image extraction: {str(e)}")
        st.error("An error occurred while extracting images and text.")
        return None

# Function to create a ZIP file from the extracted images
def create_zip_from_images(image_files, zip_name):
    """
    Create a ZIP file containing all the extracted images.

    Args:
        image_files (list): List of image file paths.
        zip_name (str): The name of the ZIP file to be created.

    Returns:
        BytesIO: A BytesIO object containing the ZIP file data.
    """
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for img_path in image_files:
            # Add image to the ZIP file, preserving the file name
            zip_file.write(img_path, os.path.basename(img_path))
    zip_buffer.seek(0)  # Rewind the buffer to the beginning
    return zip_buffer

# Streamlit UI

def main():
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    st.title("GeoGPT - PDF Table Extractor")

    # Authentication
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None

    if (
        st.session_state["authentication_status"] is None
        or st.session_state["authentication_status"] is False
    ):
        st.warning("Please log in to access this application.")
        st.stop()

    st.title("PDF Image Extractor")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"], accept_multiple_files=False)
    
    if uploaded_file:
        # Save the uploaded file temporarily
        file_path = os.path.join(TMP_FOLDER, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"File uploaded: {uploaded_file.name}")
    
        # Display the PDF using pdf_viewer
        st.subheader("Uploaded PDF:")
        with open(file_path, "rb") as pdf_file:
            pdf_binary = pdf_file.read()
            pdf_viewer(input=pdf_binary, width=800, height=500)
    
        # Count and display the number of pages
        num_pages = count_pdf_pages(file_path)
        st.write(f"Number of pages: {num_pages}")
    
        # Button to extract images and text
        if st.button("Extract Images"):
            output_folder = os.path.join(TMP_FOLDER, "extracted_images")
            image_files = extract_images_from_pdf(file_path, output_folder)
    
            # Button to download images as a ZIP file
            if image_files:
                zip_name = f"{uploaded_file.name.split('.')[0]}_images.zip"
                zip_buffer = create_zip_from_images(image_files, zip_name)
    
                # Streamlit download button
                st.download_button(
                    label="Download Images as ZIP",
                    data=zip_buffer,
                    file_name=zip_name,
                    mime="application/zip"
                )
                
if __name__ == "__main__":
    # Mock authentication for testing (replace with real logic)
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = True  # Set to False to test auth flow

    main()
