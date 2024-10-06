import os
import sys
import warnings
warnings.filterwarnings("ignore")

from PIL import Image

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '..')))
from RAG_BASIC.Images_Tables.process_Images_Tables import ImageTable
from RAG_BASIC.utils.utils import _save_data_structure


PATH = "extracted_images/"

class ImageProcessor:
    def __init__(self, file_name, folder_name=PATH):
        self.file_name = file_name
        self.source_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.folder_path = os.path.join(self.source_path, folder_name)
        self.data_obj = []
        self.count = 0

        # Initialize ImageTable instance
        self.img_table = ImageTable(path=self.folder_path, filename=self.file_name)
        print(f"Images path: {self.img_table.path_images_tables}")

    def process_images(self):
        data = self.img_table()
        for img_path in data:
            self.handle_image(img_path)
        
        print("Done")

    def handle_image(self, img_path):
        image_obj = Image.open(img_path)
        image_obj.show()
        
        user_input = input(f"Do you want to delete the file {img_path}? (yes/no): ").lower()

        if user_input == 'yes':
            self.img_table.delete_file(img_path)
            print(f"{img_path} has been deleted.")
        else:
            self.save_image_data(img_path)

        image_obj.close()

    def save_image_data(self, img_path):
        enter_text = input(f"Enter Text: ")

        image_data = {
            'source': img_path,
            "formId": self.img_table.get_source(),
            "filetype": self.img_table.get_filetype(file_path=img_path),
            "chunk_id": self.img_table.get_image_table_id(seq_id=self.count),
            "text": enter_text
        }

        self.count += 1
        self.data_obj.append(image_data)

        _save_data_structure(self.data_obj, "./chunks_extracted", f"{self.file_name}_imgTable", compressed_save=False)
        
        # _save_data_structure(self.data_obj, self.img_table.path_images_tables, f"{self.file_name}_imgTable", compressed_save=False)