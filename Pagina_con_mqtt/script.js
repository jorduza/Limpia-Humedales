
let client = null
let isConnected = false
const brokerPort = 8884
const brokerIp = "48ef0ca4945340daaf3f5150626093e2.s1.eu.hivemq.cloud"

const url = `wss://${brokerIp}:${brokerPort}/mqtt`


const btnArriba = document.getElementById("adelante")
const btnAbajo = document.getElementById("atras")
const btnIzq = document.getElementById("izquierda")
const btnDer = document.getElementById("derecha")


let btnAVelocidad = 0;
let btnBVelocidad = 0;


const sliderVel = document.getElementById("sliderVel")
const bateriaNivel = document.getElementById("porcentaje")




sliderVel.addEventListener('input', ()=>{
    updateSpeed(sliderVel.value)
    setSpeed("B",sliderVel.value)
})



btnArriba.addEventListener('click', ()=>{

    toggle(btnArriba)
})

btnAbajo.addEventListener('click', ()=>{

    toggle(btnAbajo)
})
btnIzq.addEventListener('click', ()=>{

    toggle(btnIzq)
})
btnDer.addEventListener('click', ()=>{

    toggle(btnDer)
})

btnB.addEventListener('click', ()=>{
    
    Banda_toggle(btnB)
})




function toggle(btn) {
      if (btn.classList[0] === "off") {
        btnPrendido = document.querySelector(".on")
        if(btnPrendido != null){
            btnPrendido.className = "off";
        }
        btn.className = "on";
        sendCommand(btn.id);
      }
       else {
        btn.className = "off";
        sendCommand("detener");
      }
}


function Banda_toggle(btn) {
      if (btn.classList[0] === "off_B") {
        btn.className = "on_B";
        btn.innerText = "Apagar"
        sendCommandBanda("prender");
      }
       else {
        btn.className = "off_B";
        btn.innerText = "Prender"
        sendCommandBanda("apagar");
      }
}



function setSpeed(m, val) {
  document.getElementById('speed' + m + 'Val').innerText = val;
}



function connectMQTT() {      
    try {
        const options = {
            username: 'wetlandcare',
            password: 'Wetlandcare1',
            clean: true,
            connectTimeout: 4000,
            reconnectPeriod: 0 
        };

        client = mqtt.connect(url, options);

        client.on('connect', function () {
            console.log('Conectado al broker MQTT');
            isConnected = true;
            updateStatus('Conectado', 'connected');
            
            client.subscribe('vehiculo/info/nivel_bateria', function (err) {
                if (!err) {
                    console.log('Suscrito a bateria');
                }
            });
        });

        client.on('message', function (topic, message) {
            console.log('Mensaje recibido:', topic, message.toString());
            
            if (topic === 'vehiculo/info/nivel_bateria') {
                document.getElementById('porcentaje').textContent = message.toString();
            }
        });

        client.on('error', function (error) {
            console.error('Error MQTT:', error);
            updateStatus('Error de conexión', 'disconnected');
            isConnected = false;
        });

        client.on('close', function () {
            console.log('Desconectado del broker');
            updateStatus('Desconectado', 'disconnected');
            isConnected = false;
        });

    } catch (error) {
        console.error('Error al conectar:', error);
        alert('Error al conectar: ' + error.message);
    }
}

function sendCommand(command) {
    if (!isConnected || !client) { 
        alert('Primero conecta al broker MQTT');
        return;
    }

    console.log('Enviando comando:', command);
    client.publish('vehiculo/control', command);
    
}

function sendCommandBanda(command) {
    if (!isConnected || !client) {
        alert('Primero conecta al broker MQTT');
        return;
    }

    console.log('Enviando comando:', command);
    client.publish('vehiculo/banda', command);
    
}

function updateSpeed(speed) {
    if (isConnected && client) {
      console.log('Cambiando velocidad:', speed + '%');
      client.publish('vehiculo/velocidad', speed.toString());
    }
}

function readSensor() {
    if (!isConnected || !client) {
        alert('Primero conecta al broker MQTT');
        return;
    }

    console.log('Solicitando lectura del sensor');
    client.publish('vehiculo/info', '');
}


function updateStatus(message, className) {
    const statusElement = document.getElementById('status');
    statusElement.textContent = message;
    statusElement.className = 'status ' + className;
}



window.onload = function () {
    connectMQTT()
    console.log("Espera")
    setTimeout(solicitarBateria, 1000)
};

function solicitarBateria() {
    if (!isConnected || !client) {
        alert('Primero conecta al broker MQTT');
        return;
    }
    client.publish('vehiculo/info/solicitar', '');
    setInterval(() => {
      client.publish('vehiculo/info/solicitar', '');
      console.log("Se solicito bateria")}, 60000);

}

