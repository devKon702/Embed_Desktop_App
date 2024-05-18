import socket
import struct

class SocketService:
    def __iniit__(self, ip, port):
        self.ip = ip
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.socket.connect(self.ip, self.port)

    def send(self, data):
        data_size = len(data)
    
        # Gửi số lượng phần tử của mảng float
        self.socket.send(struct.pack("H", data_size))

        # Gửi từng phần tử của mảng float
        for value in data:
            self.socket.send(struct.pack("f", value))

    def recieve(self,data_len):
        # Nhận kết quả từ Arduino
        result = self.socket.recv(data_len)
        result_float = struct.unpack('f', result)[0]
        return result_float

