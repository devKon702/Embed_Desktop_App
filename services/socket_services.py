import socket
import struct

class SocketService:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.socket = None

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))

    def send_float_arr(self, data):
        data_size = len(data)
    
        # Gửi số lượng phần tử của mảng float
        self.socket.send(struct.pack("H", data_size))

        # Gửi từng phần tử của mảng float
        for value in data:
            self.socket.send(struct.pack("f", value))

    def send_int_arr(self, data):
        data_size = len(data)
    
        # Gửi số lượng phần tử của mảng int
        self.socket.send(struct.pack("H", data_size))

        # Gửi từng phần tử của mảng int
        for value in data:
            self.socket.send(struct.pack("i", value))

    def recieve(self,data_len):
        # Nhận kết quả từ Arduino
        result = self.socket.recv(data_len)
        result_float = struct.unpack('f', result)[0]
        return result_float

    def close(self):
        self.socket.close()
