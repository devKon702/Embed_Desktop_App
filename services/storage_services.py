from firebase_admin import storage
from utils.helpers import *

class StorageService:
    def __init__(self):
        self.storage_client = storage.bucket()

    def get_image_from_url(self, url):
        try:
            # Kết nối và tải mảng byte của image
            image_blob = self.storage_client.blob(url)
            image_content = image_blob.download_as_string()

            # Chuyển đổi mảng bytes sang mảng unint8
            image = bytes_to_image(image_content)
            return image
        except Exception as e:
            print("Lỗi khi tải hình ảnh từ Storage: ", e)
            return None  

    def dowload_model(self, local_file_name, path):
        model_blob = self.storage_client.blob(path)
        model_blob.download_to_filename(local_file_name)
        
    def upload_image(self, image, filename, extension = ".jpg"):
        try:       
            # Chuyển đổi ảnh sang mảng bytes
            image_bytes = image_to_bytes(image, extension)     

            # Upload mảng byte lên storage
            image_blob = self.storage_client.blob(filename + extension)
            image_blob.upload_from_string(image_bytes)

            # Nhận download URL của image vừa được tải lên
            download_url = image_blob.public_url
            return download_url
        except Exception as e:
            print("Lỗi khi tải hình ảnh lên Storage: ", e)
            return None



