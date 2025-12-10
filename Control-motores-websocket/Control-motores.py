import uwebsockets.client
import os
import network
import time
from machine import Pin, PWM
import ujson as json


#Variables 

SSID = "wifi_id"
PASSWORD = "wifi_password"
# 

velocidad = 32768; 
velocidad_banda = 20000;


#Motores de la Banda
#L293-N 
MOTOR_BANDA_A1 = Pin(1, Pin.OUT)#Motores A
MOTOR_BANDA_A2 = Pin(2, Pin.OUT)
PWM_Banda_A = PWM(Pin(3))
PWM_Banda_A.freq(1000)
PWM_Banda_A.duty_u16(0)
MOTOR_BANDA_B1 = Pin(20, Pin.OUT)#Motores B
MOTOR_BANDA_B2 = Pin(21, Pin.OUT)
PWM_Banda_B = PWM(Pin(0))
PWM_Banda_B.freq(1000)
PWM_Banda_B.duty_u16(0)


#Motores de propulcion del wetlandcare
MOTOR_A1 = Pin(9, Pin.OUT)#Motores A
MOTOR_A2 = Pin(10, Pin.OUT)
PWM_A = PWM(Pin(6))
PWM_A.freq(1000)
PWM_A.duty_u16(0)
MOTOR_B1 = Pin(7, Pin.OUT)#Motores B
MOTOR_B2 = Pin(8, Pin.OUT)
PWM_B = PWM(Pin(5))
PWM_B.freq(1000)
PWM_B.duty_u16(0)


def connect_wifi():

    wlan = network.WLAN(network.STA_IF) # 
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print("Conectando a WiFi", end="")
    while not wlan.isconnected():
        time.sleep(1)
        print(".", end="")
    print("\nWiFi conectado!")
    print("IP:", wlan.ifconfig()[0])
    return wlan.ifconfig()[0]


def adelante():

    MOTOR_A1.on()
    MOTOR_B2.on()
    PWM_A.duty_u16(velocidad)
    PWM_B.duty_u16(velocidad)
    MOTOR_A2.off()
    MOTOR_B1.off()


def apagado():

    MOTOR_A1.off()
    MOTOR_B2.off()
    PWM_A.duty_u16(0)
    PWM_B.duty_u16(0)
    MOTOR_A2.off()
    MOTOR_B1.off()

    

def reversa():

    MOTOR_A1.off()
    MOTOR_B2.off()
    PWM_A.duty_u16(velocidad)
    PWM_B.duty_u16(velocidad)
    MOTOR_A2.on()
    MOTOR_B1.on()


def derecha():

    MOTOR_A1.off()
    MOTOR_B2.on()
    PWM_A.duty_u16(velocidad)
    PWM_B.duty_u16(velocidad)
    MOTOR_A2.on()
    MOTOR_B1.off()

    

def izquierda():

    MOTOR_A1.on()
    MOTOR_B2.off()
    PWM_A.duty_u16(velocidad)
    PWM_B.duty_u16(velocidad)
    MOTOR_A2.off()
    MOTOR_B1.on()


def Banda_Prendido():

    MOTOR_BANDA_A1.on()
    MOTOR_BANDA_A2.off()
    PWM_Banda_A.duty_u16(velocidad_banda)
    PWM_Banda_B.duty_u16(velocidad_banda)
    MOTOR_BANDA_B1.on()
    MOTOR_BANDA_B2.off()


def Banda_Apagado():

    MOTOR_BANDA_A1.off()
    MOTOR_BANDA_A2.off()
    PWM_Banda_A.duty_u16(0)
    PWM_Banda_B.duty_u16(0)
    MOTOR_BANDA_B1.off()
    MOTOR_BANDA_B2.off()

    

    

def cambiar_velocidad(vel):

    global velocidad
    velocidad = int(vel* 655.35) 
    PWM_A.duty_u16(velocidad)
    PWM_B.duty_u16(velocidad)

    

    

def hello():
    print("Entra a Hello")
    with uwebsockets.client.connect('ws://169.254.123.99:8000/ws/web_client/web_1') as websocket:
        websocket.send("Hola desde ESP32!")

        while websocket.open:
            data = websocket.recv() 
            if data:
                print("Mensaje del servidor:", data)
                try:
                    if "estado" in data: #{me conecte}
                        info = json.loads(data)
                        if info["estado"] == "on":
                            if info["motor"] == "btnArriba":  
                                adelante()
                                print("funciono 1")

                            elif info["motor"] == "btnAbajo":
                                reversa()
                                print("funciono 2")

                            elif info["motor"] == "btnDerecha":
                                derecha()
                                print("funciono 3")

                            elif info["motor"] == "btnIzquierda":
                                izquierda()

                            elif info["motor"] == "btnB":
                                Banda_Prendido()
                                print("funciono 4 ")

                        elif info["estado"] == "off":
                            if info["motor"] == "btnB":
                                Banda_Apagado()

                            else:
                                apagado()
                                print("apago")

                    if "velocidad" in data:                      
                        info = json.loads(data)
                        print (info)
                        cambiar_velocidad(int(info["velocidad"]))                       


                except Exception as e:
                    print("JSON inválido:", data)
                    return


            time.sleep(1)


ip = connect_wifi()

hello() 