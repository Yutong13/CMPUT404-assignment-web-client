#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it
# Modified by Yutong Liu at 2022/10/8th
import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse as parser

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        return int(data[0].split(" ")[1])

    def get_headers(self,data):
        headers_in_list = data.split("\r\n"*2)[0].split("\r\n")
        headers_in_dictionary = {}
        for i in range(len(headers_in_list)):
            headers_in_list[i] = headers_in_list[i].strip(" ")
            if ":"in headers_in_list[i]:
                header_key = headers_in_list[i].split(":")[0].lower()
                header_value = headers_in_list[i].split(":")[1:]
                headers_in_dictionary[header_key] = (":".join(header_value)).strip().lower()
        return headers_in_dictionary

    def get_body(self, data):
        return None
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    def parser(self, url):
        parsed_url = parser.urlparse(url)
        port = parsed_url.port
        if not parsed_url.port:
            port = 80
        
        host = parsed_url.hostname
        
        return host, port

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        receive = False
        while not done:
            try:
                part = sock.recv(1024)
                if (part):
                    buffer.extend(part)
                    receive = True
                elif receive:
                    buffer.extend(part)
                    done = not part
            except TimeoutError:
                break
        sock.shutdown(socket.SHUT_WR)
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        host, port = self.parser(url)
        

        self.connect(host, int(port))
        self.socket.settimeout(1)
        self.sendall(f'GET {url} HTTP/1.1\r\nHost: {host}\r\nContent-Type: text/html\r\n\r\n')
        result = self.recvall(self.socket)
        self.close()

        
        # parsing
        code = self.get_code(result.split("\r\n"))
        body = result.split("\r\n\r\n")[1].strip()
        
        return HTTPResponse(code, str(body))

    def POST(self, url, args=None):
        host, port = self.parser(url)

        self.connect(host, int(port))
        self.socket.settimeout(1)
        if args:
            length = len(str(args))
        else:
            length = 0
            args = "" # if there's no arg
        
        body = args
        if type(args) == dict:
            body = ""
            for key, value in args.items():
                body += f'{key}={value}&'
            if body:
                body = body[:-1]
        body.replace(" ", "%20")
        self.sendall(f'POST {url} HTTP/1.1\r\nHost: {host}\r\nContent-Length: {len(body)}\r\nContent-Type: application/x-www-form-urlencoded\r\n\r\n{body}\r\n')
        result = self.recvall(self.socket)
        self.close()

        code = self.get_code(result.split("\r\n"))
        
        body = result.split("\r\n\r\n")[1].strip()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
