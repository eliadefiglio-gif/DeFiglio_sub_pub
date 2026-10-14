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
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', '--broker_ip', help='Broker IP address', default='127.0.0.1')
    parser.add_argument('-t', '--topic', help='Topic to subscribe to')
    args = parser.parse_args()
    if args.broker_ip and args.topic:
        pass
    else:
        logging.error('Broker IP address and topic are required')

if __name__ == '__main__':
    main()