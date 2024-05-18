from firebase_admin import firestore

class FirestoreService:
    def __init__(self, collectionPath):
        self.db = firestore.client()
        self.ref = self.db.collection(collectionPath)
    
    def get_all(self):
        result_list = []
        try:
            docs = self.ref.stream()

            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                result_list.append(data)
            return result_list
        except Exception as e:
            print(f"Lỗi lấy dữ liệu: {e}")
        
        return result_list

    def get_where(self, attr, operator, value):
        result_list = []
        try:
            docs = self.ref.where(attr,operator,value).stream()

            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id
                result_list.append(data)
        except Exception as e:
            print(f"Lỗi lọc dữ liệu: {e}")

        return result_list

    def get_by_id(self,id):
        try:
            doc = self.ref.document(id).get()
            if doc.exists():
                return doc.to_dict()
        except Exception as e:
            print(f"Lỗi lấy dữ liệu: {e}")
        
        return None
