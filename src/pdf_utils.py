import os
import fitz
import uuid
from typing import List
import pymupdf4llm
import pymupdf
from streamlit import session_state as ss


def extract_images_text_pdf(
    path: str, image_path: str, export_images: bool = True, image_format: str = "jpg"
):
    """
    Extract text and images from a pdf file
    """
    return pymupdf4llm.to_markdown(
        doc=path,
        write_images=export_images,
        image_path=image_path,
        image_format=image_format,
    )


def docs_from_pymupdf4llm(path: str):
    """
    Args:
        path: path to pdf file
    """
    md_read = pymupdf4llm.LlamaMarkdownReader()
    data = md_read.load_data(path)
    return data


def extract_tables_from_pdf(path: str):
    """
    Extract tables from a pdf file
    """
    doc = pymupdf.open(path)
    tables = {}
    for i, page in enumerate(doc):
        tabs = page.find_tables()
        if len(tabs.tables) > 0:
            tables[i] = tabs
    return tables


def get_docs_to_add_vectorstore(pages, file, category="legal"):
    # get components to add to Faiis
    documents = []
    ids = []
    metadatas = []

    for page in pages:

        metadatas.append(
            {"page": page.metadata.get("page"), "filename": file, "category": category}
        )
        ids.append(uuid.uuid1().hex)
        documents.append(page.page_content)

    return documents, ids, metadatas


def count_pdf_pages(pdf_path):
    """
    count number of pages in a pdf file
    :param pdf_path: path to pdf file
    :return: number of pages
    """

    doc = fitz.open(pdf_path)

    num_pages = len(doc)

    return num_pages
