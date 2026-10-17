#!/usr/bin/env python3
import threading
import socket
import logging

logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )

class Broker(threading.Thread):

    topics = {}
    topics_lock = threading.Lock()

    def __init__(self, conn, addr):
        super().__init__()
        self.sock = conn
        self.addr = addr


    def run(self):
        try:
            while True:
                message = self.readLine(self.sock)

                if not message:
                    break

                command = message.decode("utf-8").strip()

                if command[:3] == 'pub':
                    parts = command.split(':', 2)

                    if len(parts) == 3:
                        topic_name = parts[1].strip()
                        message = parts[2]

                    if topic_name in self.topics:
                        self.sock.sendall("OK\n".encode("utf-8"))
                        with self.topics_lock:
                            for client_sock in self.topics[topic_name]:
                                try:
                                    client_sock.sendall(f"{message}\n".encode("utf-8"))
                                    logging.info(f"Published message to '{topic_name}'")
                                    logging.info(f"Message received by {self.addr}")
                                except ConnectionRefusedError:
                                    logging.warning(f"Connection refused from {self.addr}")
                                except Exception as e:
                                    logging.error(e)
                    else:
                        self.sock.sendall("NOTFOUND\n".encode("utf-8"))

                if command[:3] == 'sub':
                    topic_name = command[4:].strip()

                    with self.topics_lock:
                        if topic_name not in self.topics:
                            self.topics[topic_name] = [self.sock]
                            logging.debug(f"Created new topic '{topic_name}' from {self.addr}")
                        else:
                            if self.sock not in self.topics[topic_name]:
                                self.topics[topic_name].append(self.sock)
                                logging.debug(f"Client {self.addr} added to topic '{topic_name}'")
                        self.sock.sendall("OK\n".encode())

        except ConnectionError:
            logging.warning(f"Client {self.addr} disconnected")
        finally:

            with self.topics_lock:
                for topic in list(self.topics):
                    if self.sock in self.topics[topic]:
                        logging.info(f"Client {self.addr} removed from topic '{topic}'")
                        self.topics[topic].remove(self.sock)
                    if not self.topics[topic]:
                        del self.topics[topic]

            self.sock.close()
            logging.info(f"Connection to client {self.addr} closed")

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
            logging.info(f'Broker connected to {addr}')
            broker = Broker(conn, addr)
            broker.daemon = True
            broker.start()
    except KeyboardInterrupt:
        logging.info("Stopping broker")
        s.close()

if __name__ == '__main__':
    main()