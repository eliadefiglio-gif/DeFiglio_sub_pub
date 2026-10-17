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
    parser.add_argument('-m', '--message', help='Message to send')
    args = parser.parse_args()
    if args.broker_ip and args.topic and args.message:

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))

        sock.sendall(f'pub:{args.topic}:{args.message}\n'.encode())
        logging.info(f"Sent 'pub:{args.topic}:{args.message}\n' to broker {args.broker_ip}")
        data = b''
        while b'\n' not in data:
            data += sock.recv(1024)
        if data and data.decode().strip() == 'OK':
            logging.info(f"Successfully sent '{args.message}' to topic '{args.topic}'")
        elif data and data.decode().strip() == 'NOTFOUND':
            logging.warning(f"Failed to send '{args.message}'. '{args.topic}' topic doesn't exist")
        else:
            logging.warning("Didn't receive data from broker")
    else:
        logging.error('Broker IP address/topic/message are required')

if __name__ == '__main__':
    main()