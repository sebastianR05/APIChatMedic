from datetime import datetime
from flask import Flask, app, jsonify
from flask.globals import request
from pymongo import MongoClient
import smtplib

url = "mongodb+srv://admin:admin12345@cluster0.p2zgi.mongodb.net/ChatMedic?retryWrites=true&w=majority"

conexion = MongoClient(url)
db = conexion.ChatMedic

app = Flask(__name__)

@app.route('/consultarmedicamentos/<descripcion>')
def consultarMedicamentos(descripcion):    
    if(db.medicamentos.find({"descripcion":descripcion}).count() > 0):
        data = db.medicamentos.find_one({"descripcion": descripcion}) 
        respuesta = {
            "exitoso": True,
            "descripcion": data["descripcion"], 
            "cantidad": data["cantidad"],
            "disponible": data["disponible"],
            "observacion": data["observacion"]
        }
        return jsonify(respuesta)
    else: 
        return {
            "exitoso": False,
            "mensaje": "No se encontró el medicamento " + descripcion
        } 

@app.route('/consultarmedicamentosdisponibles')
def consultarmedicamentosdisponibles():
    respuesta = {}
    list_datos = []
    myquery = { "disponible": True }
    if(db.medicamentos.find(myquery).count() > 0):        
        data = db.medicamentos.find(myquery) 
        for x in data:
            datos = {
                "descripcion": x["descripcion"], 
                "cantidad": x["cantidad"],
                "disponible": x["disponible"],
                "observacion": x["observacion"]
            }
            list_datos.append(datos)
        respuesta = {
            "exitoso": True,
            "data": list_datos
        }
        return jsonify(respuesta)
    else:
        return {
            "exitoso": False,
            "mensaje": "No se encontró medicamentos disponibles"
        } 

@app.route('/enviaremail', methods=["POST"])
def enviaremail():
    try:
        sender_email = "chatmedic2021@gmail.com"
        password = "Diplomado2021"
        body = request.get_json()
        asunto = body["asunto"]
        mensaje = body["mensaje"]
        message = body["mensaje"]
        message = 'Subject: {}\n\n{}'.format(asunto, message)    
        destinatario = body["destinatario"]

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, destinatario, message)

        respuesta = {
            "exitoso": True,
            "mensaje": "Se ha enviado el email correctamente"
        }        
        server.quit()  
    except:
        print("ha ocurrido un error")
    return jsonify(respuesta)
    
@app.route('/guardarlogemail', methods=["POST"])
def guardarlogemail():
    sender_email = "chatmedic2021@gmail.com"
    body = request.get_json()

    # Crea el objeto de log email para almacenar en la base de datos
    nuevo_log = {
        "asunto": body["asunto"],
        "mensaje": body["mensaje"],
        "destinatario": body["destinatario"],
        "remitente": sender_email,
        "fecha_envio": str(datetime.now())
    }

    # guarda el registro del log de envio del email en la base de datos
    x = db.log_email.insert_one(nuevo_log) 

    respuesta = {
        "exitoso": True,
        "mensaje": "Se ha guardado el log del email correctamente"
    }        
    return jsonify(respuesta)

@app.route('/guardarsolicitudmedicamento', methods=["POST"])
def guardarsolicitudmedicamento():  
    respuesta = {}
    body = request.get_json()
    x = db.solicitudes.insert_one(body)     
    respuesta = {
        "exitoso": True,
        "mensaje": "Se ha creado la solicitud correctamente"
    }
   
    return jsonify(respuesta)

if __name__ == "__main__":
    app.run(debug=True)
