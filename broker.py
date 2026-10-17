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
                    pass

                if command[:3] == 'sub':
                    topic_name = command[4:].strip()
                    client_address = (self.addr[0], self.addr[1])

                    with self.topics_lock:
                        if topic_name not in self.topics:
                            self.topics[topic_name] = [client_address]
                            logging.debug(f"Created new topic '{topic_name}' from {client_address}")
                        else:
                            if client_address not in self.topics[topic_name]:
                                self.topics[topic_name].append(client_address)
                                logging.debug(f"Client {client_address} added to topic '{topic_name}'")
                        self.sock.sendall("OK\n".encode())

        except ConnectionError:
            logging.warning("Client disconnected")
        finally:
            client_identity = (self.addr[0], self.addr[1])

            with self.topics_lock:
                for topic in list(self.topics):
                    if client_identity in self.topics[topic]:
                        logging.info(f"Client {client_identity} removed from topic '{topic}'")
                        self.topics[topic].remove(client_identity)
                    if not self.topics[topic]:
                        del self.topics[topic]

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
            broker = Broker(conn, addr)
            broker.daemon = True
            broker.start()
    except KeyboardInterrupt:
        logging.info("Stopping broker")
        s.close()

if __name__ == '__main__':
    main()