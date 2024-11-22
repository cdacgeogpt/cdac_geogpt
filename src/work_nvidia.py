# test run and see that you can genreate a respond successfully

import os
from llama_index.llms.nvidia import NVIDIA
from llama_index.embeddings.nvidia import NVIDIAEmbedding
import logging
from llama_index.core import VectorStoreIndex
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.chat_engine import CondensePlusContextChatEngine
from llama_index.core import Settings

TEXT_SPLITTER_CHUNCK_SIZE = 200
TEXT_SPLITTER_CHUNCK_OVERLAP = 50


def get_llm(model):
    return NVIDIA(model=model, max_tokens=1024, temperature=0.7)


def get_embeddings(model):
    return NVIDIAEmbedding(model=model, truncate="END")


def setup_index(model, embeddings):
    """
    Args:
        model: str
        embeddings: str
    """
    Settings.llm = model
    Settings.embed_model = embeddings
    return


def vectorindex_from_data(data, embed_model):
    """
    Args:
        data: data. list of LLamaIndex Documents
    """
    index = VectorStoreIndex(data, embed_model=embed_model)
    return index


def create_memory_buffer(token_limit: int = 4500):
    """
    Create a memory buffer
    args:
        token_limit: int

    """
    return ChatMemoryBuffer.from_defaults(token_limit=token_limit)


def create_chat_engine(index):
    """
    create a chat engine
    Args:
        index: llama_index.core.VectorStoreIndex
    """
    memory = create_memory_buffer()
    return CondensePlusContextChatEngine.from_defaults(
        index.as_retriever(), memory=memory
    )
