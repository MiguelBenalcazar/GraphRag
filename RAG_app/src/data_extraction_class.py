import os
import sys
import warnings
warnings.filterwarnings("ignore")

from typing import Any
import gc

# Add the path to your RAG_BASIC package
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
from RAG_BASIC.extractData.extractData import FileReader
from RAG_BASIC.semantic_chunkers.chunkers.statistical import StatisticalChunker
from RAG_BASIC.encoder.custom_embeddings import CustomEmbeddings
from RAG_BASIC.utils.utils import _save_data_structure

# Set the folder where uploaded files will be saved

CHUNK_PATH = "./chunks_extracted/"
MODEL = "all-MiniLM-L6-v2"
MAX_SPLIT_TOKENS = 300



# Define the RAG class
class DATA_EXTRACTION():
    def __init__(self, filename: str, language: str = "english") -> None:
        # Extract data from file
        self.file = filename
        self.language = language
        self.reader = FileReader(filename=self.file, languages=self.language)
        
        filename_info = os.path.basename(filename)
        self.file_name = os.path.splitext(filename_info)[0]
        
        # Perform statistical chunking
        self.encoder = CustomEmbeddings(model=MODEL)
        self.chunker = StatisticalChunker(
            encoder=self.encoder, 
            max_split_tokens=MAX_SPLIT_TOKENS, 
            plot_chunks=False, 
            enable_statistics=False,
            language=language,
            dynamic_threshold=False
        )

    def __call__(self) -> Any:
        # Extract data from the file
        _, sorted_data_extracted = self.reader(compressed_save=False)
        chunks = self.chunker(docs=sorted_data_extracted, batch_size=16, print_chunks=False)
        

        _save_data_structure(chunks, CHUNK_PATH, self.file_name, compressed_save=False)


        del sorted_data_extracted
        gc.collect()

