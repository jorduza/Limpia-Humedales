#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h> 
#include <ArduinoJson.h>

// conexion wifi - configuracion 
const char* ssid = "Just-in";
const char* password = "12345678909";

// Conexion servidor mqtt - configuracion 
const char* mqtt_server = "48ef0ca4945340daaf3f5150626093e2.s1.eu.hivemq.cloud";
const int mqtt_port = 8883;

//credenciales mqtt
const char* mqtt_username = "wetlandcare";   
const char* mqtt_password = "Wetlandcare1";  


//Variables de velocidad 
int velocidadMotores = 2500;
int velocidadBanda = 4095;

//Almacena que tipo de movimiento esta actualmente
String movimientoActual = "detener";


//Motor A
const int motorA_pwm = 5;    
const int motorA1 = 20;   
const int motorA2 = 21;    

//Motor B
const int motorB_pwm =3 ;    
const int motorB1 = 1;    
const int motorB2 = 2;    

// Motores de la banda
const int motorBandaA_pwm = 4;    
const int motorBandaA1 = 7;    
const int motorBandaA2 = 8;  
const int motorBandaB_pwm = 6;    
const int motorBandaB1 = 9;    
const int motorBandaB2 = 10;  

// Variables globales
WiFiClientSecure espClient;
PubSubClient client(espClient);
unsigned long lastMsg = 0;
bool wifiConnected = false;
bool mqttConnected = false;


// Variable ADC para leer la bateria
const int bateriaPin = 0;

// funciones de movimiento

void moverAdelante() {
  Serial.println("Adelante");
  digitalWrite(motorA1, HIGH);
  digitalWrite(motorA2, LOW);
  digitalWrite(motorB1, HIGH);
  digitalWrite(motorB2, LOW);
  analogWrite(motorA_pwm, velocidadMotores);
  analogWrite(motorB_pwm, velocidadMotores);
  movimientoActual = "adelante";
}

void moverAtras() {
  Serial.println("Atras");
  digitalWrite(motorA1, LOW);
  digitalWrite(motorA2, HIGH);
  digitalWrite(motorB1, LOW);
  digitalWrite(motorB2, HIGH);
  analogWrite(motorA_pwm, velocidadMotores);
  analogWrite(motorB_pwm, velocidadMotores);
  movimientoActual = "atras";
}

void moverIzquierda() {
  Serial.println("Izquierda");
  digitalWrite(motorA1, LOW);
  digitalWrite(motorA2, HIGH);   
  digitalWrite(motorB1, HIGH);
  digitalWrite(motorB2, LOW);    
  analogWrite(motorA_pwm, velocidadMotores / 2);  
  analogWrite(motorB_pwm, velocidadMotores);      
  movimientoActual = "izquierda";
}

void moverDerecha() {
  Serial.println("Derecha");
  digitalWrite(motorA1, HIGH);
  digitalWrite(motorA2, LOW);    
  digitalWrite(motorB1, LOW);
  digitalWrite(motorB2, HIGH);   
  analogWrite(motorA_pwm, velocidadMotores);      
  analogWrite(motorB_pwm, velocidadMotores / 2);
  movimientoActual = "derecha";
}


void stopMotoresMovimiento() {
  analogWrite(motorA_pwm, 0);  
  analogWrite(motorB_pwm, 0);  
  
  digitalWrite(motorA1, LOW);
  digitalWrite(motorA2, LOW);
  digitalWrite(motorB1, LOW);
  digitalWrite(motorB2, LOW);
  movimientoActual = "detener";
  
}

// Motores de la banda funciones 
void prenderMotoresBanda(){
    analogWrite(motorBandaA_pwm, velocidadBanda);  
    analogWrite(motorBandaB_pwm, velocidadBanda);  
  
  digitalWrite(motorBandaA1, HIGH);
  digitalWrite(motorBandaA2, LOW);
  digitalWrite(motorBandaB1, HIGH);
  digitalWrite(motorBandaB2, LOW);
}

void stopMotoresBanda(){
    analogWrite(motorBandaA_pwm, 0);  
    analogWrite(motorBandaB_pwm, 0);  
  
  digitalWrite(motorBandaA1, LOW);
  digitalWrite(motorBandaA2, LOW);
  digitalWrite(motorBandaB1, LOW);
  digitalWrite(motorBandaB2, LOW);
}

// Cambiar la velocidad por porcentaje, 
void cambiarVelocidad(int porcentaje){
    velocidadMotores = (porcentaje * 4095) /100;
    Serial.print("La velocidad a cambiado a: ");
    Serial.print(velocidadMotores);
    
    if(movimientoActual != "detener"){
        Serial.println("Cambiando la velocidad del movimiento");
        aplicarCambios();
    }
}

//Si esta en movimiento cambia la velocidad actual de los motores a los nuevos
void aplicarCambios(){
    if (movimientoActual == "adelante") {
    moverAdelante();
    }
    else if (movimientoActual == "atras") {
        moverAtras();

    }
    else if (movimientoActual == "izquierda") {
        moverIzquierda();
    }
    else if (movimientoActual == "derecha") {
        moverDerecha();
    }
}

// Funcion para hacer el cambio en la banda
void cambiarEstadoBanda(String comando){
    Serial.print("Comando recibido para la banda: ");
    Serial.print(comando);

    if(comando == "prender"){
        prenderMotoresBanda();
    }else if(comando == "apagar"){
        stopMotoresBanda();
    }else {
    Serial.println("Comando desconocido: " + comando);
  }
}


//funcion leer bateria
int leerPorcentaje(){
    int valorSensor = analogRead(bateriaPin);
    int valorPorcentaje = (valorSensor * 100) / 4095;

    Serial.print("Bateria %");
    Serial.print(valorPorcentaje);
    return valorPorcentaje;
}



void setup() {
  Serial.begin(115200);
  
  // Configurar pines de motores
  setupMotores();

  espClient.setInsecure();

  // Conectar WiFi
  setup_wifi();
  
  // Configurar MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqtt_callback);
}

void setupMotores() {
  // setup de pines iniciales
  pinMode(motorA1, OUTPUT);
  pinMode(motorA2, OUTPUT);
  pinMode(motorB1, OUTPUT);
  pinMode(motorB2, OUTPUT);
  pinMode(motorBandaA1, OUTPUT);
  pinMode(motorBandaA2, OUTPUT);
  pinMode(motorBandaB1, OUTPUT);
  pinMode(motorBandaB2, OUTPUT);
  
  // setup de pines pwm
  pinMode(motorA_pwm, OUTPUT);
  pinMode(motorB_pwm, OUTPUT);
  pinMode(motorBandaA_pwm, OUTPUT);
  pinMode(motorBandaB_pwm, OUTPUT);
  
  // Parar motores inicialmente
  stopMotoresMovimiento();
}




// wifi setup
void setup_wifi() {
  Serial.println();
  Serial.print("Conectando a ");
  Serial.println(ssid);
  
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(250);
    delay(250);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    wifiConnected = true;
    Serial.println("");
    Serial.println("WiFi conectado!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("");
    Serial.println("Error: No se pudo conectar al WiFi");
  }
}

// Control de motores
void moverVehiculo(String comando) {
  Serial.print("Comando recibido: ");
  Serial.println(comando);
  
  if (comando == "adelante") {
    moverAdelante();
  }
  else if (comando == "atras") {
    moverAtras();
  }
  else if (comando == "izquierda") {
    moverIzquierda();
  }
  else if (comando == "derecha") {
    moverDerecha();
  }
  else if (comando == "detener") {
    stopMotoresMovimiento();
  }
  else {
    Serial.println("Comando desconocido: " + comando);
  }
}


// ==================== CALLBACK MQTT ====================
void mqtt_callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Mensaje recibido [");
  Serial.print(topic);
  Serial.print("]: ");
  
  String messageTemp;
  for (int i = 0; i < length; i++) {
    messageTemp += (char)payload[i];
  }
  Serial.println(messageTemp);
  
  if (String(topic) == "vehiculo/control") {
    moverVehiculo(messageTemp);
  }
  else if (String(topic) == "vehiculo/velocidad") {
    int porcentaje = messageTemp.toInt();
    cambiarVelocidad(porcentaje);
  }
  else if (String(topic) == "vehiculo/banda") {
    cambiarEstadoBanda(messageTemp);
  }
  else if (String(topic) == "vehiculo/info/solicitar") {
    int respuesta = leerPorcentaje();
    String valorBateria = String(respuesta);
    client.publish("vehiculo/info/nivel_bateria", valorBateria.c_str());
  }
  
  delay(100);
}

// ==================== RECONEXIÓN MQTT ====================
void reconnect() {
  while (!client.connected()) {
    Serial.print("Intentando conexión MQTT...");
    
    if (client.connect("ESP32C3_Vehiculo",mqtt_username,mqtt_password)) {
      Serial.println("conectado!");
      mqttConnected = true;
      
      client.subscribe("vehiculo/control");
      client.subscribe("vehiculo/velocidad");
      client.subscribe("vehiculo/banda");
      client.subscribe("vehiculo/info/solicitar");
      
      client.publish("vehiculo/estado", "ESP32-C3 conectado");
      
    } else {
      Serial.print("falló, rc=");
      Serial.print(client.state());
      Serial.println(" intentando en 5 segundos...");
      mqttConnected = false;
      delay(5000);
    }
  }
}


// ==================== LOOP PRINCIPAL ====================
void loop() {
  // Reconectar WiFi si se perdió
  if (WiFi.status() != WL_CONNECTED) {
    wifiConnected = false;
    Serial.println("WiFi perdido, reconectando...");
    setup_wifi();
  }
  
  // Reconectar MQTT si es necesario
  if (!client.connected()) {
    mqttConnected = false;
    reconnect();
  }
  client.loop();
  
  // Publicar estado periódicamente (opcional)
  unsigned long now = millis();
  if (now - lastMsg > 60000) { // Cada 10 segundos
    lastMsg = now;
    
    if (mqttConnected && wifiConnected) {
      String estado = "Conectado - IP: " + WiFi.localIP().toString();
      client.publish("vehiculo/estado", estado.c_str());
      Serial.println("Estado publicado: " + estado);
    }
  }
  
  delay(10);
}