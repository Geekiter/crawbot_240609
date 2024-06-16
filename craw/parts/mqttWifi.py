# from micropyserver import MicroPyServer
import json
import socket
import time

import machine
import network
import utils
import utime
from micropyserver import MicroPyServer
from umqtt.simple import MQTTClient


class wifiConnect():
    def __init__(self, wifiName, wifiPassword, clientID, serverIP, port, myTopic, machineId, MsgOK, debug=False):
        self.debug = debug
        self.wifi_wait_time = 0
        self.wifi_connect = False
        self.wifiName = wifiName
        self.wifiPassword = wifiPassword
        self.MsgOK = MsgOK
        self.clientID = clientID
        self.port = port
        self.serverIP = serverIP
        self.myTopic = myTopic
        self.machineId = machineId
        self.mqtt_client = 0
        self.run = False
        self.server = 0
        self.state_value = 0
        self.mqtt_client = 1

    # set up WIFI and MQTT functions
    def log(self, message, level="INFO"):
        timestamp = utime.localtime(utime.time())
        formatted_time = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
            *timestamp)
        print("[{}] [{}] {}".format(formatted_time, level, message))

    def release_wifi(self):
        sta_if = network.WLAN(network.STA_IF)

        if sta_if.isconnected():
            # if it is connected, first disconnect
            sta_if.disconnect()
            self.log("Disconnected from Wi-Fi network.", "INFO")

        # deactive STA
        sta_if.active(False)
        self.log("STA interface disabled. Wi-Fi cache released.", "INFO")

    def do_connect(self):
        # global wifi_wait_time, wifi_connect

        # release wifi cache
        self.release_wifi()

        sta_if = network.WLAN(network.STA_IF)

        if not sta_if.isconnected():
            try:
                self.log('Connecting to network...', 'INFO')
                sta_if.active(True)
                sta_if.connect(self.wifiName, self.wifiPassword)
                while not sta_if.isconnected():
                    utime.sleep(1)
                    self.wifi_wait_time += 1
                    if self.wifi_wait_time >= 10:
                        raise Exception("Connection timeout")
                self.wifi_connect = True
                self.log('Connected to network successfully', 'INFO')
                self.log(str(sta_if.ifconfig()), 'INFO')
            except Exception as e:
                self.log("Connection error: " + str(e), 'ERROR')
        else:
            self.log(str(sta_if.ifconfig()), 'INFO')
            self.wifi_connect = True

    def monitor_wifi_connection(self):
        # global wifi_connect

        sta_if = network.WLAN(network.STA_IF)
        if sta_if.isconnected():
            self.log("WiFi status: connected")
            self.log("Signal Strength: " + str(sta_if.status('rssi')))
            r, msg = self.test_connectivity()
            self.log(msg)
            if r == False:
                self.wifi_connect = False
        else:
            self.log("WiFi status: not connected")
            self.wifi_connect = False

    def test_connectivity(self):
        sta_if = network.WLAN(network.STA_IF)

        try:
            if sta_if.isconnected():
                addr_info = socket.getaddrinfo(sta_if.ifconfig()[2], 80)
                addr = addr_info[0][-1]

                s = socket.socket()
                s.settimeout(5)
                s.connect(addr)
                s.close()
                return True, "Successfully connected to LAN!"
            else:
                return False, "WIFI can't connected!"
        except OSError as e:
            return False, "Unable to connect to LAN:" + str(e)

    def restart_and_reconnect(self):
        print('Failed to connect to MQTT broker. Reconnecting...')
        time.sleep(10)
        machine.reset()

    def connect_and_subscribe(self):
        try:
            client = MQTTClient(client_id=self.clientID,
                                server=self.serverIP, port=self.port, keepalive=6000)
            client.set_callback(self.MsgOK)
            client.connect()
            client.subscribe(self.myTopic)
            self.log("Connected to MQTT server at {}:{}".format(self.serverIP, self.port), 'INFO')
            return client
        except Exception as e:
            self.log("Failed to connect to MQTT server: " + str(e), 'ERROR')
            self.restart_and_reconnect()

    def connect_show_params(self, client, request):
        ''' request handler '''
        params = utils.get_request_query_params(request)
        print(params)
        ips = params['mqtt_ip'].split(":")
        self.serverIP = ips[0]
        self.port = ips[1]
        ''' will return {"param_one": "one", "param_two": "two"} '''
        self.server.send(client, "HTTP/1.0 200 OK\r\n")
        self.server.send(client, "Content-Type: text/html\r\n\r\n")
        if self.machineId != params['machineid']:
            return self.server.send(client, "Not this car")
        if self.run == True:
            return self.server.send(client, "mqtt is connected!")
        try:
            self.mqtt_client = self.connect_and_subscribe()
            self.server.send(client, "ok")
            self.run = True
            self.state_value = 12
            # server.stop()
        except OSError as e:
            print(e)
            self.server.send(client, "failed")

    def stop_show_params(self, client, request):
        # request handler
        params = utils.get_request_query_params(request)
        print(params)
        self.server.send(client, "HTTP/1.0 200 OK\r\n")
        self.server.send(client, "Content-Type: text/html\r\n\r\n")
        if self.machineId != params['machineid']:
            return self.server.send(client, "Not this car")
        if self.run != True:
            return self.server.send(client, "No mqtt connected!")
        try:
            self.mqtt_client.disconnect()
            self.server.send(client, "ok")
            self.run = False
        except OSError as e:
            self.server.send(client, "failed")

    def status_show_params(self, client, request):
        ''' request handler '''
        params = utils.get_request_query_params(request)
        print(params)
        if self.machineId != params['machineid']:
            self.server.send(client, "HTTP/1.0 200 OK\r\n")
            self.server.send(client, "Content-Type: text/html\r\n\r\n")
            return self.server.send(client, "Not this car")
        json_str = json.dumps(
            {"run": self.run, "mqtt_ip": "{}:{}".format(self.serverIP, self.port)})
        self.server.send(client, "HTTP/1.0 200 OK\r\n")
        self.server.send(client, "Content-Type: application/json\r\n\r\n")
        self.server.send(client, json_str)

    def setup(self):
        self.server = MicroPyServer()
        self.server.add_route("/connect", self.connect_show_params)
        self.server.add_route("/stop", self.stop_show_params)
        self.server.add_route("/status", self.status_show_params)
        self.server.add_route("/test", static_test)
        self.server.start()

    def loop(self):
        self.server.loop()


def static_test(client, request):
    ''' request handler '''
    print("static test")
