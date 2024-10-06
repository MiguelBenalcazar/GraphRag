import os
import warnings
warnings.filterwarnings("ignore")

from src.data_extraction_class import DATA_EXTRACTION as de
from src.images_tables_class import ImageProcessor 
from src.add_graph_class import GraphProcessor
from src.add_BM25_class import BM25_Processor



def verify_clean():
    os.system('cls' if os.name == 'nt' else 'clear')

def menu():
    txt = '''
    \nMENU
    1. Get ready data from file (PDF)
    2. Check images and add description
    3. Add data to graph data
    4. Add data to BM25
    5. List Projects
    0. Exit

    '''
    print(txt)


def data_from_file():
    file_path = input("Enter the path to the PDF file: ")
    if os.path.exists(file_path):
        data_read = de(filename=file_path)
        data_read()
    else:
        print("File not found. Please provide a valid path.")



def add_data_to_graph():
    user_input = input(f"Enter the project name: \n")
    graph_processor = GraphProcessor(name_project=user_input)
    graph_processor()


def check_images_and_add_description():
    print("\n--- Checking images and adding description ---")
    user_input = input(f"Enter the project name: \n")
    image_processor = ImageProcessor(file_name=user_input)
    image_processor.process_images()
    

def bm25():
    processor = BM25_Processor()
    # Check all files in the folder and categorize them
    processor.check_all_files()
    processor.process_files()


def get_projects():
    folder_path = "./data_extracted"
    print('\n Projects \n')
    print(os.listdir(folder_path))


if __name__ == "__main__":
    verify_clean()
    while True:
        
        menu()
        choice = input("Select an option: ")

        if choice == "1":
            data_from_file()
        elif choice == "2":
           check_images_and_add_description()
        elif choice == "3":
           add_data_to_graph() 
        elif choice == "4":
           bm25() 
        elif choice == "5":
            get_projects()
        elif choice == "0":
            print("Exiting...")
            break
        else:
            print("Invalid option. Please choose a valid option.")
