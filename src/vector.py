from llama_index.core import StorageContext, load_index_from_storage


def load_index_from_disk(path: str):
    """
    Load index from disk
    """
    storage_context = StorageContext.from_defaults(persist_dir=path)
    index = load_index_from_storage(storage_context)
    return index


def persist_index_to_disk(index, path: str):
    """
    Persist index to disk
    """
    index.storage_context.persist(path)
    return
