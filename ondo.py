from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from random import randrange
from urllib.parse import parse_qs, urlparse
import requests,pprint,json,time, prometheus_client, threading, time, os, random
from prometheus_client import start_http_server, Summary

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


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    global kami1, kami2, kami3, temp
    def do_GET(self):
        global kami1, kami2, kami3, temp
        parsed_path = urlparse(self.path)

        if parsed_path.path.endswith('/error'):
            raise Exception('Error')

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
        
        
        temp.labels('unit1').set(kami1)
        temp.labels('unit2').set(kami2)
        temp.labels('unit3').set(kami3)

        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(f'再収集 from {self.path} as GET'.encode('utf-8'))
        time.sleep(1)

if __name__ == '__main__':
    start_http_server(8000)

    with ThreadingHTTPServer(('0.0.0.0', 8001), MyHTTPRequestHandler) as server:
        print(f'[{datetime.now()}] Server startup.')
        server.serve_forever()
