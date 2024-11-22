import streamlit as st
import os.path
from streamlit_pdf_viewer import pdf_viewer
from streamlit import session_state as ss
from pathlib import Path
from dotenv import dotenv_values
import json
import logging
import shutil  # For deleting folder contents
from src.utils import print_stack
from src.pdf_utils import count_pdf_pages, docs_from_pymupdf4llm
from src.helpers import init_session_1, reset_session_1, write_history_1
from src.work_nvidia import (
    get_llm,
    get_embeddings,
    vectorindex_from_data,
    create_chat_engine,
    setup_index,
)
from src.vector import load_index_from_disk, persist_index_to_disk
from IPython import embed


# where I am
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
path = Path(ROOT_DIR)
TMP_FOLDER = os.path.join(path.parent.absolute(), "tmp")
# Create folders
logging.info(f"Root Dir {ROOT_DIR} Temp Folder {TMP_FOLDER}")


def reset_saves_folder():
    folder_path = st.session_state.get("db_local_folder1", None)
    tmp_folder_path = TMP_FOLDER

    # Delete the saves folder
    if folder_path and os.path.exists(folder_path):
        try:
            shutil.rmtree(folder_path)
            logging.info(f"Reset: Cleared the folder {folder_path}")
        except Exception as e:
            logging.error(f"Error while clearing the saves folder: {str(e)}")

    # Clear contents of TMP_FOLDER but keep the folder itself
    if tmp_folder_path and os.path.exists(tmp_folder_path):
        try:
            for filename in os.listdir(tmp_folder_path):
                file_path = os.path.join(tmp_folder_path, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            logging.info(f"Reset: Cleared the contents of TMP_FOLDER {tmp_folder_path}")
        except Exception as e:
            logging.error(f"Error while clearing the contents of TMP_FOLDER: {str(e)}")

    # Clear all relevant session state variables
    st.session_state.clear()  # This clears all session state variables!
    logging.info("Session state has been completely cleared.")



def click_button_parse(st):
    st.session_state["click_button_parse1"] = True
    return


def main(col1, col2, placeholder, config):
    """
    Main loop with reset button to clear the saves folder
    """
    st.title("GeoGPT")  # Added title for the page
    # two columns
    if "vcol1doc" in st.session_state and "vcol2doc" in st.session_state:
        col1 = st.session_state["vcol1doc"]
        col2 = st.session_state["vcol2doc"]

    row1_1, row1_2 = st.columns((col1, col2))
    
    try:
        # Initialize Vars
        if "init_run_1" not in st.session_state:
            st.session_state["init_run_1"] = False
        if st.session_state["init_run_1"] == False:
            init_session_1(st, ss, col1, col2)

        with row1_1:
            # File upload logic...
            if st.session_state.value1 >= 0 and st.session_state["salir_1"] == False:
                uploaded_files = st.file_uploader(
                    "Upload PDF file",
                    type=("pdf"),
                    key="pdf",
                    accept_multiple_files=False,
                )
                
                if uploaded_files:
                    logging.info(f"Speak with PDF Page: file uploaded {uploaded_files.name}")
                    # To read file as bytes:
                    im_bytes = uploaded_files.getvalue()
                    file_path = f"{TMP_FOLDER}/{uploaded_files.name}"
                    print(file_path)
                    with open(file_path, "wb") as f:
                        f.write(im_bytes)
                    if ss.pdf:
                        ss.pdf_ref1 = im_bytes
                    numpages = count_pdf_pages(file_path)
                    logging.info(f"Number of pages {uploaded_files.name}: {numpages}")
                    st.session_state["file_name1"] = file_path
                    st.session_state["file_history1"] = uploaded_files.name
                    st.session_state["upload_state1"] = f"Number pages {uploaded_files.name}: {numpages}"

                st.session_state.value1 = 1  # file uploaded

            # Now you can access "pdf_ref1" anywhere in your app.
            if ss.pdf_ref1:
                with row1_1:
                    if "pdf_viewer" not in st.session_state:
                        st.session_state["pdf_viewer"] = None
                    if st.session_state.value1 >= 1 and st.session_state["salir_1"] == False:
                        binary_data = ss.pdf_ref1
                        width = 900 if st.session_state["vcol1doc"] == 50 else 350 if st.session_state["vcol1doc"] == 20 else 700
                        pdf_viewer(input=binary_data, width=width, height=400, key="pdf_viewer")
                        
                        if st.button("Parse pdf", on_click=click_button_parse, args=(st,)):
                            if st.session_state["vector_store1"] == None:
                                st.session_state["data1"] = docs_from_pymupdf4llm(st.session_state["file_name1"])
                                st.session_state["vector_store1"] = vectorindex_from_data(
                                    data=st.session_state["data1"],
                                    embed_model=st.session_state["embeddings1"],
                                )
                                logging.info(f"Number of pages in document {len(st.session_state['data1'])}")
                                # persist index
                                persist_index_to_disk(index=st.session_state["vector_store1"], path=st.session_state["db_local_folder1"])
                                logging.info("Vector Store created from document pages")
                                st.session_state["upload_state1"] = f"Number pages document {len(st.session_state['data1'])}\nVector Store created from document pages"

                        if st.session_state["click_button_parse1"] == True and st.session_state["vector_store1"] != None and st.session_state["salir_1"] == False:
                            logging.info(f"Status bottom parse {st.session_state['click_button_parse1']}")
                            input_prompt = st.text_input("Ask your queries 👇 👇", key="pdf_query")
                            st.session_state["chat_true1"] = "chat activo"
                            
                            if input_prompt and st.session_state["salir_1"] == False and st.session_state["chat_true1"] == "chat activo":
                                if st.session_state["llamaindex1"] == None:
                                    st.session_state["llamaindex1"] = create_chat_engine(st.session_state["vector_store1"])
                                response = st.session_state["llamaindex1"].chat(input_prompt)
                                st.session_state["upload_state1"] = str(response)
                                st.session_state["chat_history1"].append((input_prompt, str(response)))

            # Add a reset button to clear the saves folder



        with row1_2:
            if st.button("New document"):
                reset_saves_folder()
                st.rerun()  # Ensures that the Streamlit app completely resets after clearing
            with st.expander("Inference of GeoGPT 👇👇", expanded=st.session_state["expander_1"]):
                _ = st.text_area("GeoGPT status", "", key="upload_state1", height=500)

    except Exception as e:
        # handle exception
        st.session_state["salir_1"] = True
        placeholder.empty()
        text = print_stack()
        text = "Speak with PDF Page " + text
        logging.error(text)
        logging.error(str(e))
    
    return


if __name__ == "__main__":
    global col1, col2
    st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
    
    # go to login page if not authenticated
    if "authentication_status" not in st.session_state:
        st.session_state["authentication_status"] = None
    if st.session_state["authentication_status"] == None or st.session_state["authentication_status"] == False:
        st.session_state.runpage = "main.py"
        st.switch_page("main.py")
    
    if "salir_1" not in st.session_state:
        st.session_state["salir_1"] = False

    if st.session_state["salir_1"] == False:
        # Empty placeholder for session objects
        placeholder_1 = st.empty()
        with placeholder_1.container():
            col1, col2 = 50, 50
            ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
            path = Path(ROOT_DIR)
            config = dotenv_values(os.path.join(path.parent.absolute(), "keys", ".env"))

            # Initialize Model
            if "chat1" not in st.session_state:
                st.session_state["chat1"] = get_llm(model=config.get("NVIDIA_MODEL"))
            # Initialize embeddings models
            logging.info(f"Model {config.get('NVIDIA_MODEL')} initialized")
            if "embeddings1" not in st.session_state:
                st.session_state["embeddings1"] = get_embeddings(model=config["NVIDIA_EMBEDDINGS"])
            logging.info(f"Model Embeddings: {config.get('NVIDIA_EMBEDDINGS')} initialized")
            
            if "index1" not in st.session_state:
                st.session_state["index1"] = setup_index(
                    model=st.session_state["chat1"],
                    embeddings=st.session_state["embeddings1"],
                )
            logging.info("LLama Index initialized")
            
            # check if we have the index persisted in the folder
            if "db_local_folder1" not in st.session_state:
                st.session_state["db_local_folder1"] = os.path.join(path.parent.absolute(), "saves", config.get("INDEX_NAME"))
            if "db_local_file1" not in st.session_state:
                st.session_state["db_local_file1"] = os.path.join(path.parent.absolute(), "saves", config.get("INDEX_NAME") + ".json")

            main(col1, col2, placeholder_1, config)