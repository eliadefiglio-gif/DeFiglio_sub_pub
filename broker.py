#!/usr/bin/env python3
import threading
import socket
import logging

class Broker(threading.Thread):
    def __init__(self, conn):
        super().__init__()
        self.sock = conn

    def run(self):
        try:
            while True:
                pass
        except ConnectionError:
            logging.warning("Client disconnected")
        finally:
            self.sock.close()
            logging.info("Connection to client closed")

    def readLine(self, sk):
        data = b''
        while b'\n' not in data:
            packet = sk.recv(1024)
            if not packet:
                return b''
            data += packet

        line, _ = data.split(b'\n', 1)
        return line + b'\n'



def main():
    logging.info("Starting broker")
    HOST = ''
    PORT = 6767
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)

    try:
        while True:
            conn, addr = s.accept()
            logging.info('client connected ip:<' + str(addr) + '>')
            broker = Broker(conn)
            broker.daemon = True
            broker.start()
    except KeyboardInterrupt:
        logging.info("Stopping broker")
        s.close()

if __name__ == '__main__':
    main()