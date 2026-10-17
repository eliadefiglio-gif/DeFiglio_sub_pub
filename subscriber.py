#!/usr/bin/env python3
import socket
import argparse
import logging

logging.basicConfig(
        level=logging.DEBUG,
        format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
        datefmt='%H:%M:%S'
    )

def main():
    host = '127.0.0.1'
    port = 6767

    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', '--broker_ip', help='Broker IP address', default='127.0.0.1')
    parser.add_argument('-t', '--topic', help='Topic to subscribe to')
    args = parser.parse_args()
    if args.broker_ip and args.topic:

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))

        sock.sendall(f'sub:{args.topic}\n'.encode())
        logging.info(f"Sent 'sub:{args.topic}' to broker {args.broker_ip}")
        data = b''
        while b'\n' not in data:
            data += sock.recv(1024)
        if data and data.decode().strip() == 'OK':
            logging.info(f"Successfully subscribed to {args.broker_ip}. Now listening...")
            data = b''
            try:
                while True:
                    data = sock.recv(1024)
                    if data:
                        print(data.decode())
                        data = b''
            except KeyboardInterrupt:
                logging.info("Closing broker connection")
                sock.close()
        else:
            logging.warning("Didn't receive data from broker")
    else:
        logging.error('Broker IP address/topic are required')

if __name__ == '__main__':
    main()