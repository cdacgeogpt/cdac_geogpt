import streamlit as st
from streamlit_pdf_viewer import pdf_viewer
from tabula import read_pdf
import pandas as pd
from PyPDF2 import PdfReader
import os
import time

# Define temporary folder for storing uploaded files
TMP_FOLDER = "tmp"
os.makedirs(TMP_FOLDER, exist_ok=True)

# Function to extract tables from the uploaded PDF with progress and percentage
def extract_tables_with_progress(pdf_path, output_excel, start_page=None, end_page=None):
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    error_pages = []
    extracted_tables = []

    # Determine the pages to process
    if start_page and end_page:
        pages_to_process = range(start_page, end_page + 1)
    else:
        pages_to_process = range(1, total_pages + 1)

    # Initialize progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()  # Placeholder for status message
    total_steps = len(pages_to_process)

    for step, page in enumerate(pages_to_process, start=1):
        try:
            # Attempt to read tables from the current page
            tables = read_pdf(pdf_path, pages=str(page), multiple_tables=True)
            if tables:
                extracted_tables.append((page, tables))
        except Exception as e:
            error_pages.append(page)

        # Update progress bar and percentage
        progress = int((step / total_steps) * 100)
        progress_bar.progress(progress)
        status_text.text(f"Processing, please wait... {progress}% completed")
        time.sleep(0.1)  # Optional: Simulate delay for better visualization

    # Save extracted tables to Excel if any
    if extracted_tables:
        with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
            for page, tables in extracted_tables:
                for i, table in enumerate(tables):
                    sheet_name = f"Page_{page}_Table_{i+1}"
                    table.to_excel(writer, sheet_name=sheet_name, index=False)
        return total_pages, error_pages, output_excel
    else:
        return total_pages, error_pages, None


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

    # Reset button logic
    if "reset_trigger" not in st.session_state:
        st.session_state["reset_trigger"] = False

    if st.session_state["reset_trigger"]:
        st.session_state["reset_trigger"] = False
        st.experimental_rerun()

    # File upload section
    uploaded_file = st.file_uploader(
        "Upload a PDF file",
        type=("pdf"),
        key="pdf_upload",
        accept_multiple_files=False,
    )

    if uploaded_file:
        # Save the uploaded file
        pdf_name = os.path.splitext(uploaded_file.name)[0]  # Extract the PDF file name without extension
        pdf_path = os.path.join(TMP_FOLDER, uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        st.success(f"Uploaded: {uploaded_file.name}")

        # Two columns: Left for PDF display, Right for output
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("PDF Display")
            pdf_viewer(input=uploaded_file.getvalue(), width=800, height=600, key="pdf_display")

        with col2:
            st.subheader("Output Window")

            # Display total number of pages
            reader = PdfReader(pdf_path)
            total_pages = len(reader.pages)
            st.write(f"Total Pages in the Document: **{total_pages}**")

            # Button to specify page range
            specify_pages = st.checkbox("Specify Pages for Extraction")
            start_page, end_page = None, None

            if specify_pages:
                start_page = st.number_input("Start Page", min_value=1, max_value=total_pages, step=1)
                end_page = st.number_input("End Page", min_value=start_page, max_value=total_pages, step=1)

            # Button to extract tables
            if st.button("Extract Tables"):
                output_excel = os.path.join(TMP_FOLDER, f"{pdf_name}_extracted_tables.xlsx")
                total_pages, error_pages, excel_path = extract_tables_with_progress(
                    pdf_path, output_excel, start_page=start_page, end_page=end_page
                )

                if excel_path:
                    st.success("Tables extracted successfully!")
                    st.write(f"**Pages Processed:** {start_page or 1} to {end_page or total_pages}")
                    if error_pages:
                        st.warning(f"Failed to extract tables from pages: {error_pages}")
                    else:
                        st.write("All pages processed successfully!")

                    # Provide a download button
                    with open(excel_path, "rb") as f:
                        st.download_button(
                            label="Download Extracted Tables",
                            data=f,
                            file_name=f"{pdf_name}_extracted_tables.xlsx",  # Dynamic file name
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )
                else:
                    st.error("No tables found in the specified pages.")

        # Add a button to reset and upload a new PDF
        if st.button("Upload New PDF"):
            st.session_state["reset_trigger"] = True


if __name__ == "__main__":
    # Mock authentication for testing (replace with real logic)
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = True  # Set to False to test auth flow

    main()
