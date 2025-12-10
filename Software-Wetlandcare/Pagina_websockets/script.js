const socket = new WebSocket("ws://192.168.80.19:8000/ws/web_client/web_1");
const btnArriba = document.getElementById("btnArriba")
const btnAbajo = document.getElementById("btnAbajo")
const btnIzq = document.getElementById("btnIzquierda")
const btnDer = document.getElementById("btnDerecha")
const btnB = document.getElementById("btnB")


let btnAVelocidad = 0;
let btnBVelocidad = 0;


const sliderBtnA = document.getElementById("sliderBtnA")
const sliderBtnB = document.getElementById("sliderBtnB")

const speedAVal = document.getElementById("speedAVal")
const speedBVal = document.getElementById("speedBVal")

/**sliderBtnA.addEventListener('input', ()=>{
    enviarSeñales(JSON.stringify({
        motor: btnA.id,
        velocidad: sliderBtnA.value
    }))
    actualizarVelocidad("A",sliderBtnA.value)
})**/

sliderBtnB.addEventListener('input', ()=>{
     enviarSeñales(JSON.stringify({
        esp32_id: "esp32_c3_01",
        motor: btnB.id,
        velocidad: sliderBtnB.value
    }))
    actualizarVelocidad("B",sliderBtnB.value)
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
   toggle(btnB)
})


socket.onopen = ()=> {
    console.log("Conectado al WebSocket local");
    socket.send(JSON.stringify({data:"WebSocket conectado"}));
};

socket.onmessage = (event)=> {
    console.log("Confirmacion:", event.data);
};

socket.onclose = ()=> {
      console.log("Conexión cerrada");
    };

socket.onerror = (err)=> {
      console.error("Error WebSocket:", err);
      alert("Conexion con el servidor fallo, intentelo de nuevo")
      window.location.reload()
};



 function enviarSeñales(mensaje) {
      if (socket.readyState === WebSocket.OPEN) {
        socket.send(mensaje);
        console.log("Mensaje enviado:", mensaje);
      } else {
        console.log("WebSocket no está abierto");
      }
}

function actualizarVelocidad(btn, velocidad){
    if(btn == "A"){
        btnAVelocidad = velocidad
        speedAVal.innerText = velocidad

    }else{
        btnBVelocidad = velocidad
        speedBVal.innerText = velocidad
    }
}


function toggle(btn) {
      if (btn.classList[0] === "off") {
        btnPrendido = document.querySelector(".on")
        if(btnPrendido != null){
            btnPrendido.className = "off";
        }
        btn.className = "on";
        enviarSeñales(JSON.stringify({esp32_id: "esp32_c3_01",motor:btn.id,estado:"on"}));
      }
       else {
        btn.className = "off";
        enviarSeñales(JSON.stringify({esp32_id: "esp32_c3_01",motor:btn.id,estado:"off"}));
      }

}

function setSpeed(m, val) {
  document.getElementById('speed' + m + 'Val').innerText = val;
}