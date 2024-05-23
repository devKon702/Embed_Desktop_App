from tkinter import Tk, Label, Toplevel
import cv2
from PIL import Image, ImageTk
from views.custom import CustomButton, center_window

import configs.firebase_config
from services.url_services import UrlService
from services.socket_services import SocketService
from services.firestore_services import FirestoreService
from services.storage_services import StorageService
from firebase_admin import firestore, messaging
import constants
from utils.helpers import bgr_2_grayscale, equalizeHist_filter, image_to_bytes, bytes_to_image, hex_to_int_array, hex_to_c_array

import time
from datetime import datetime, timedelta
import threading
import os
import tensorflow as tf
from tensorflow.keras.models import load_model

root = Tk()
root.title("Gui")
screen_width = root.winfo_screenwidth() - 100
screen_height = root.winfo_screenheight() - 100
root.geometry(f"{screen_width}x{screen_height}")

width_camera, height_camera = screen_width, screen_height

video = cv2.VideoCapture(0)

video.set(cv2.CAP_PROP_FRAME_WIDTH, width_camera)
video.set(cv2.CAP_PROP_FRAME_HEIGHT, height_camera)

label_widget = Label(root)
label_widget.pack()

# thông tin staff
mock_staff = {}
# Tải model detect khuôn mặt
cascPath = 'haarcascade_frontalface_default.xml'
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascPath)
face_frame = None
recognite_count = 0 # Dúng đếm số lần nhận diện liên tiếp cùng một người
last_userID = 0
is_stop_predicting = False


btn_load_model = CustomButton(root, text="Load model", command=lambda: [handle_load_model()])
btn_load_model.pack(side="bottom",padx=24, pady=10)
# Khai báo các service 
url_connector = UrlService(hostname=constants.ESP32_IP, path=constants.LOW_QUAL_CAM)



def handle_correct_face(user, image):
    global is_stop_predicting
    print('correct face handle')
    user_ref = firestore.client().collection("users").document(user["docID"])
    if user_ref.get().exists:
        attendances_ref = user_ref.collection("attendances")

        today = datetime.now().date() # - timedelta(days=1)
        formatted_date = today.strftime('%d-%m-%Y')

        att_doc_ref = attendances_ref.document(formatted_date)

        # Save image
        attend_storage_connector = StorageService()
        dowload_url = attend_storage_connector.upload_image(image, f"attend/{datetime.now().timestamp()}", ".jpg")
        notify_msg = ""
        # Lưu thông tin chấm công
        if att_doc_ref.get().exists:
            att_doc_ref.update({
                "clockOutTime" : datetime.now().strftime("%H:%M"),
                "imageClockOut": dowload_url
            })
            notify_msg = f'{user["id"]}?{user["firstName"]} {user["lastName"]} vừa check out'
        else:
            att_doc_ref.set({
                "clockInTime" : datetime.now().strftime('%H:%M'),
                "clockOutTime" : "",
                "date": formatted_date,
                "imageClockIn": dowload_url,
                "imageClockOut": "",
                "statbility": 0
            })
            notify_msg = f'{user["id"]}?{user["firstName"]} {user["lastName"]} vừa check in'

    send_message(topic="attendance", title="New Notify", body=notify_msg)
        
    is_stop_predicting = False

def send_message(topic, title, body):
    message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            topic=topic
        )
    # Gửi thông báo đến topic và in ra kết quả
    try:
        response = messaging.send(message)
        print('Successfully sent message:', response)
    except Exception as e:
        print('Error sending message:', e)


def handle_incorrect_face():
    global is_stop_predicting
    print('incorrect face handle')
    is_stop_predicting = False


def show_popup(staff, image):
    custom_messagebox = Toplevel()
    custom_messagebox.title("Custom Messagebox")
    str_message = f"Email: {staff['email']}\nTên: {staff['firstName']} {staff['lastName']}\nGiới tính: {staff['gender']}"
    label = Label(custom_messagebox, text=str_message, font=("Arial", 16))
    label.pack(padx=20, pady=20)

    button_ok = CustomButton(custom_messagebox, text="OK",
                             command=lambda: [handle_correct_face(staff, image), custom_messagebox.destroy()])
    button_ok.pack(side="left", padx=24)

    button_cancel = CustomButton(custom_messagebox, text="Cancel",
                                 command=lambda: [handle_incorrect_face(), custom_messagebox.destroy()])
    button_cancel.pack(side="right", padx=24)
    center_window(custom_messagebox, 400, 190)

def show_notify(msg):
    custom_messagebox = Toplevel()
    custom_messagebox.title("Notification")
    
    label = Label(custom_messagebox, text=msg, font=("Arial", 16))
    label.pack(side="top",padx=20, pady=20)

    button_ok = CustomButton(custom_messagebox, text="OK", command=lambda: [custom_messagebox.destroy()])
    button_ok.pack(side="bottom", padx=24, pady=4)

    center_window(custom_messagebox, 400, 100)



def handle_load_model():
    global is_stop_predicting
    print("Button load")
    is_stop_predicting = True
    # Lấy file model isSelected
    model_firestore_connector = FirestoreService("models")
    models = model_firestore_connector.get_where("isSelected", "==", True)
    if len(models) == 0:
        show_notify("Not found selected model")
        return
    
    selected_model = models[0]
    # Nếu đã nhúng rồi thì không load
    if selected_model["isEmbedded"] == True:
        show_notify("Model was embedded")
        return
    
    storage_connector = StorageService()
    storage_connector.dowload_model("nn_model.h", f'models/{selected_model["docID"]}.h')

    show_notify("Finish loading")

    # # Truyền tflite model đến esp
    # socket_connector = SocketService(ip=constants.ESP32_IP, port=constants.TRANFER_MODEL_PORT)
    # socket_connector.connect()
    # print("Start tranfer")
    # socket_connector.send_int_arr(hex_to_int_array(tflite_model))
    # socket_connector.close()
    
    is_stop_predicting = False



def get_face_location(frame):
    # Chuyển ảnh xám
    # gray_frame = bgr_2_grayscale(frame)
    # Nhận diện khuôn mặt trong ảnh
    faces = faceCascade.detectMultiScale(
        frame,
        scaleFactor=1.1,
        minNeighbors=10,
        minSize=(150, 150)
    )
    if(len(faces)>0):
        (x,y,w,h) = faces[0]
        return (x,y,w,h)
    else:
        return (-1,-1,-1,-1)
    
def preprocess_before_predict(image, shape):
    image = equalizeHist_filter(bgr_2_grayscale(image))
    image = cv2.resize(image, shape)
    return image.flatten()

def recognite():
    global face_frame, recognite_count, last_userID, is_stop_predicting
    predict_socket_connector = SocketService(ip=constants.ESP32_IP, port=constants.PREDICT_PORT)
    users_firestore = FirestoreService(collectionPath="users")
    while(True):
        if(face_frame is not None and not is_stop_predicting):
            current_face_frame = face_frame[:]
            
            face_data = preprocess_before_predict(current_face_frame, (constants.DATASET_IMAGE_WIDTH, constants.DATASET_IMAGE_HEIGHT))
                
            predict_socket_connector.connect()
            predict_socket_connector.send_float_arr(data = face_data)
            result = int(predict_socket_connector.recieve(4))
            predict_socket_connector.close()
            print(result)   

            if(result == 0):
                # Reset
                recognite_count = 0 
                last_userID = 0         
            elif(result != last_userID):
                last_userID = result 
            else:
                recognite_count += 1
            
            if(recognite_count == 1):
                recognite_count = 0
                last_userID = 0
                for user in users_firestore.get_where("id", "==", result):
                    show_popup(user, current_face_frame[:])
                    is_stop_predicting = True
                    break
        # Dừng 2s
        time.sleep(2)


def process():
    global face_frame
    # Lấy ảnh từ ESP
    bgr_frame = url_connector.receive()
    # Lấy vị trí khuôn mặt
    (x,y,w,h) = get_face_location(bgr_frame)
    
    if(x != -1):
        face_frame = bgr_frame[y:y+h, x:x+w]
        cv2.rectangle(bgr_frame, (x, y), (x+w, y+h), (0, 255, 0), 2) 
    else: 
        face_frame = None

    # Show image
    rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGBA)
    captured_image = Image.fromarray(rgb_frame)
    photo_image = ImageTk.PhotoImage(image=captured_image)
    label_widget.photo_image = photo_image
    label_widget.configure(image=photo_image)
    label_widget.after(10, process)

if __name__ == "__main__":
    process()
    # root.after(2000, show_popup)  # giả sử 5s nhận diện được staff => gán thông tin cho object staff
    thread = threading.Thread(target=recognite)
    thread.daemon = True # thread kết thúc khi ctr kết thúc
    thread.start()
    root.mainloop()