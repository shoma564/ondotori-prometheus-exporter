import requests,pprint,json,time, prometheus_client, threading, random, time, os, sys, socket
from prometheus_client import start_http_server, Summary
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
from random import randrange


url = "https://api.webstorage.jp/v1/devices/current"
kami1 = ""
kami2 = ""
kami3 = ""


temp = prometheus_client.Gauge('serverroom_temp','Hold current system resource usage',['device_name'])


api_key  = os.getenv('ONDO_APIKEY', '')
login_id = os.getenv('ONDO_LOGINID', '')
password = os.getenv('ONDO_PASSWORD', '')
paylord = {'api-key':api_key,"login-id":login_id,'login-pass':password}
header = {'Host':'api.webstrage.js:443','Content-Type': 'application/json','X-HTTP-Method-Override':'GET'}


def main():
        response = requests.post(url,json.dumps(paylord).encode('utf-8'),headers=header).json()
        global kami1, kami2, kami3
        print(response['devices'][0]['channel'][0]['value'], end='')
        print("℃: device1 室内(サーバー裏)")
        print(response['devices'][1]['channel'][0]['value'], end='')
        print("℃: device2 室内温度")
        print(response['devices'][2]['channel'][0]['value'], end='')
        print("℃: device3 外温度")
        kami1 = float(response['devices'][0]['channel'][0]['value'])
        kami2 = float(response['devices'][1]['channel'][0]['value'])
        kami3 = float(response['devices'][2]['channel'][0]['value'])




def server():
    global kami1,kami2,kami3, temp
    start_http_server(8000)
    with ThreadingHTTPServer(('0.0.0.0', 8080), MyHTTPRequestHandler) as server:
        print(f'[{datetime.now()}] Server startup.')
        temp.labels('unit1').set(kami1)
        temp.labels('unit2').set(kami2)
        temp.labels('unit3').set(kami3)

        server.serve_forever()


def tutu():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1',8080))
    if result == 0:
        print("Port is open")
    else:
        print("Port is not open")


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    global kami1,kami2,kami3,temp

    def do_GET(self):
        global kami1,kami2,kami3,temp
        parsed_path = urlparse(self.path)

        if parsed_path.path.endswith('/error'):
            raise Exception('Error')

        response = requests.post(url,json.dumps(paylord).encode('utf-8'),headers=header).json()
        global kami1, kami2, kami3
        kami1 = float(response['devices'][0]['channel'][0]['value'])
        kami2 = float(response['devices'][1]['channel'][0]['value'])
        kami3 = float(response['devices'][2]['channel'][0]['value'])


        self.send_response(200)
        self.end_headers()
        self.wfile.write(f'再収集 from {self.path} as GET'.encode('utf-8'))


if __name__ =="__main__":
    main()
    tutu()
    thread2 = threading.Thread(target=server)
    thread2.start()

    while True:
        time.sleep(15)
        tutu()
        main()