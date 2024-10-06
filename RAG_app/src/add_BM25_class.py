import os
import sys
import warnings
warnings.filterwarnings("ignore")

from typing import Any, List
from tqdm import tqdm

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
from RAG_BASIC.utils.utils import _load_data_structure
from RAG_BASIC.BM25_rank.BM25_class import BM25_score


class BM25_Processor:
    def __init__(self, folder_name: str = "./chunks_extracted"):
        """
        Initialize BM25_Processor with the specified folder.
        
        :param folder_name: Path to the folder containing files to be processed.
        """
        self.folder_name = folder_name
        self.img_table_files: List[str] = []  # Files containing '_imgTable'
        self.other_files: List[str] = []      # All other files
        self.corpus = []

    def check_all_files(self):
        """
        Check all files in the specified folder and separate them into two arrays:
        - Files containing '_imgTable' in their name.
        - Other files.
        
        :return: None
        """
        try:
            # List all files in the folder
            all_files = [f for f in os.listdir(self.folder_name) if os.path.isfile(os.path.join(self.folder_name, f))]

            # Separate files into img_table_files and other_files
            self.img_table_files = [f for f in all_files if '_imgTable' in f]
            self.other_files = [f for f in all_files if '_imgTable' not in f]

            # Output the files found
            print(f"Files found in '{self.folder_name}':")
            print("\nFiles containing '_imgTable':")
            for file in self.img_table_files:
                print(file)
            
            print("\nOther files:")
            for file in self.other_files:
                print(file)

        except FileNotFoundError:
            print(f"Error: The folder '{self.folder_name}' does not exist.")
            sys.exit(1)  # Exit if the folder does not exist

    
    def process_files(self):
        """
        Placeholder method for processing files.
        This is where you process each file (e.g., run BM25 or other logic).
        """
        if not self.img_table_files and not self.other_files:
            print("No files to process. Please check the folder first.")
            return
        

        
        print("\nProcessing other files:")
        for file in tqdm(self.other_files, desc="Loading Files"):
            file_path = os.path.join(self.folder_name, file)
            info_general = _load_data_structure(file_path)
            
            for data in tqdm(info_general, desc=file_path):
                self.corpus.append(data["text"])
    
        
        # Example: Processing files
        print("\nProcessing '_imgTable' files:")
        for file in tqdm(self.img_table_files, desc="_imgTable files"):
            file_path = os.path.join(self.folder_name, file)
            info_general = _load_data_structure(file_path)
            for data in tqdm(info_general, desc=file_path):
                self.corpus.append(data["text"])

        
        bm25_score = BM25_score(corpus= self.corpus, load=False, language='english') 
        bm25_score.save(path='./BM25_retriever')

        