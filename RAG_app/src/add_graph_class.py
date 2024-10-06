import os
import sys
import warnings
warnings.filterwarnings("ignore")
from typing import Any

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
from RAG_BASIC.GraphDatabase.knowledgeGraph_new import Create_Form_Nodes_Knowledge_Graph

class GraphProcessor:
    def __init__(self, name_project:str , folder_name:str="./chunks_extracted"):

        chunks = os.path.join(folder_name, f'{name_project}.json')
        img_tables =  os.path.join(folder_name, f'{name_project}_imgTable.json')

        if os.path.exists(chunks):
            self.chunk_file_path = chunks
        else: 
            raise ValueError("File not found")
        if os.path.exists(img_tables):
            self.chunk_images_tables_path = img_tables
        else: 
            self.chunk_images_tables_path = None   
            print("File image/tables not found")
              
        self.new_nodes = Create_Form_Nodes_Knowledge_Graph(chunk_file_path=self.chunk_file_path, chunk_images_tables_path= self.chunk_images_tables_path)
        

    def __call__(self) -> Any:
        print("Init Process")
        
        self.new_nodes()