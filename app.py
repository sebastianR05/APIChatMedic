from datetime import datetime
from flask import Flask, app, jsonify
from flask.globals import request
from pymongo import MongoClient
import smtplib

url = "mongodb+srv://admin:admin12345@cluster0.p2zgi.mongodb.net/ChatMedic?retryWrites=true&w=majority"

conexion = MongoClient(url)
db = conexion.ChatMedic

app = Flask(__name__)

@app.route('/consultarmedicamentos/<descripcion>', methods=["GET"])
def consultarMedicamentos(descripcion): 
    try:
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
    except:   
         return {
                "exitoso": False,
                "mensaje": "Ha ocurrido un error en la consulta"
            } 

@app.route('/consultarmedicamentosdisponibles', methods=["GET"])
def consultarmedicamentosdisponibles():
    respuesta = {}
    try:
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
    except:
        return {
                "exitoso": False,
                "mensaje": "Ha ocurrido un error consultando los medicamentos disponibles"
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
    try:
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
    except:
        respuesta = {
            "exitoso": False,
            "mensaje": "Ha ocurrido un error guardando el log del email"
        }
    return jsonify(respuesta)

@app.route('/guardarsolicitudmedicamento', methods=["POST"])
def guardarsolicitudmedicamento():  
    respuesta = {}
    disponible = True
    try:
        body = request.get_json()
        x = db.solicitudes.insert_one(body) 

        # actualiza el stock de medicamentos y su disponibilidad
        existente = db.medicamentos.find_one({"descripcion": body["medicamento"]}) 
        print(existente)
        if(existente["cantidad"] > 0):
            cantidad = existente["cantidad"] - 1
            if(cantidad == 0):
                disponible = False

            myquery = { "_id": existente["_id"] }
            newvalues = { "$set": { "cantidad": cantidad, "disponible": disponible } }
            db.medicamentos.update_one(myquery, newvalues)

        respuesta = {
            "exitoso": True,
            "mensaje": "Se ha creado la solicitud correctamente"
        }
    except:
        respuesta = {
            "exitoso": False,
            "mensaje": "Ha ocurrido un error guardando la solicitud del medicamento"
        }   
    return jsonify(respuesta)

@app.route('/crearmedicamento', methods=["POST"])
def crearmedicamento():  
    respuesta = {}
    try:
        body = request.get_json()
        # Consulta si el medicamento ya existe
        if(db.medicamentos.find({"descripcion" :body["descripcion"]}).count() > 0):
            respuesta = {
                "exitoso": False,
                "mensaje": "El medicamento: " + body["descripcion"] + ", ya se encuentra creado en la base de datos"
            }
        else:
            x = db.medicamentos.insert_one(body)     
            respuesta = {
                "exitoso": True,
                "mensaje": "Se ha creado el medicamento correctamente"
            }
    except:
        respuesta = {
            "exitoso": False,
            "mensaje": "Ha ocurrido un error guardando el medicamento"
        }   
    return jsonify(respuesta)

@app.route('/actualizarmedicamento', methods=["PUT"])
def actualizarmedicamento():  
    respuesta = {}
    try:
        body = request.get_json()
        # Consulta si el medicamento ya existe
        if(db.medicamentos.find({"descripcion": body["descripcion"]}).count() > 0):
            existente = db.medicamentos.find_one({"descripcion": body["descripcion"]}) 
            myquery = { "_id": existente["_id"] }
            newvalues = { "$set":
                            { 
                                "disponible": body["disponible"], 
                                "cantidad": body["cantidad"], 
                                "observacion": body["observacion"], 
                            }
                        }
            db.medicamentos.update_one(myquery, newvalues)

            respuesta = {
                "exitoso": True,
                "mensaje": "Se ha actualizado la data correctamente"
            }
        else:   
            respuesta = {
                "exitoso": False,
                "mensaje": "El medicamento: " + body["descripcion"] + ", no se encuentra registrado en la base de datos"
            }
    except:
        respuesta = {
            "exitoso": False,
            "mensaje": "Ha ocurrido un error actualizando el medicamento"
        }   
    return jsonify(respuesta)

if __name__ == "__main__":
    app.run(debug=True)
