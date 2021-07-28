from datetime import datetime
from flask import Flask, app, jsonify
from flask.globals import request
from pymongo import MongoClient
import smtplib

# variable que instancia la cadena de conexion de mongo db
url = "mongodb+srv://admin:admin12345@cluster0.p2zgi.mongodb.net/ChatMedic?retryWrites=true&w=majority"

# Se carga en una variable la ejecucion de la conexion con la base de datos
conexion = MongoClient(url)

# se carga en una variable las propiedades de la base de datos chatmedic
db = conexion.ChatMedic

app = Flask(__name__)

# Servicio para la consulta de medicamentos por descipcion
@app.route('/consultarmedicamentos/<descripcion>', methods=["GET"])
def consultarMedicamentos(descripcion): 
    try:
        # valida si el medicamento existe en la base de datos
        if(db.medicamentos.find({"descripcion":descripcion}).count() > 0):
            # si existe recupera el registro del medicamento de la base de datos
            data = db.medicamentos.find_one({"descripcion": descripcion}) 
            
            # crea el objeto json de respuesta con los tags correspondientes a los datos del medicamento
            respuesta = {
                "exitoso": True,
                "descripcion": data["descripcion"], 
                "cantidad": data["cantidad"],
                "disponible": data["disponible"],
                "observacion": data["observacion"]
            }

            # retorna la respuesta 
            return jsonify(respuesta)
        else: 
            # crea y retorna el objeto json de respuesta con indicacion de que el medicamento no existe
            return {
                "exitoso": False,
                "mensaje": "No se encontró el medicamento " + descripcion
            } 
    except:  
        # crea y retorna el objeto json de respuesta con indicacion de que ocurrio un error en la consulta 
         return {
                "exitoso": False,
                "mensaje": "Ha ocurrido un error en la consulta"
            } 

# Servicio para la consulta de medicamentos disponibles en la base de datos
@app.route('/consultarmedicamentosdisponibles', methods=["GET"])
def consultarmedicamentosdisponibles():
    respuesta = {}
    try:
        list_datos = []
        # crea objeto con el creiterio de busqueda para la consulta a la base de datos
        myquery = { "disponible": True }

        # valida si existen medicamentos con el criterio de busqueda
        if(db.medicamentos.find(myquery).count() > 0): 

            # recupera en una variable los datos de la consulta      
            data = db.medicamentos.find(myquery) 

            # itera los datos de la consulta y los agrega a una lista
            for x in data:
                datos = {
                    "descripcion": x["descripcion"], 
                    "cantidad": x["cantidad"],
                    "disponible": x["disponible"],
                    "observacion": x["observacion"]
                }
                list_datos.append(datos)

            # crea el objeto json de respuesta con el listado de medicamentos disponibles
            respuesta = {
                "exitoso": True,
                "data": list_datos
            }

            # retorna la respuesta 
            return jsonify(respuesta)
        else:
            # crea y retorna el objeto json de respuesta con indicacion de que no hay medicamentos disponibles
            return {
                "exitoso": False,
                "mensaje": "No se encontró medicamentos disponibles"
            } 
    except:
        # crea y retorna el objeto json de respuesta con indicacion de que ocurrio un error en la consulta 
        return {
                "exitoso": False,
                "mensaje": "Ha ocurrido un error consultando los medicamentos disponibles"
            } 

# Servicio para el envio de correos electronicos
@app.route('/enviaremail', methods=["POST"])
def enviaremail():
    try:
        # asigna a variables los valores de asunto mensaje, destinatario
        sender_email = "chatmedic2021@gmail.com"
        password = "Diplomado2021"
        body = request.get_json()
        asunto = body["asunto"]
        message = body["mensaje"]
        message = 'Subject: {}\n\n{}'.format(asunto, message)    
        destinatario = body["destinatario"]

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, destinatario, message)

        # crea el objeto json de respuesta con la indicacion que el email fue enviado correctamente
        respuesta = {
            "exitoso": True,
            "mensaje": "Se ha enviado el email correctamente"
        }        
        server.quit()  
    except:
        print("ha ocurrido un error")

    # retorna la respuesta json de la api
    return jsonify(respuesta)

# Servicio para crear el log de los emails enviados
@app.route('/guardarlogemail', methods=["POST"])
def guardarlogemail():
    try:
        sender_email = "chatmedic2021@gmail.com"

        # asigna a una variable el body request de la peticion
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
    
    # retorna la respuesta json de la api
    return jsonify(respuesta)

# Servicio para crear la solicitud de medicamentos
@app.route('/guardarsolicitudmedicamento', methods=["POST"])
def guardarsolicitudmedicamento():  
    respuesta = {}
    disponible = True
    try:
        # asigna a una variable el body request recibido en la peticion
        body = request.get_json()

        # crea la solicitud con el request de la solicitud
        x = db.solicitudes.insert_one(body) 

        # actualiza el stock de medicamentos y su disponibilidad
        # consulta si existe el medicamento para actualizar
        existente = db.medicamentos.find_one({"descripcion": body["medicamento"]}) 

        # valida si la cantidad del stock es mayor a 0 para seguir restando el stock
        if(existente["cantidad"] > 0):
            cantidad = existente["cantidad"] - 1

            # si la cantidad del stock es 0 reasigna el valor de disponible a false
            if(cantidad == 0):
                disponible = False

            myquery = { "_id": existente["_id"] }
            newvalues = { "$set": { "cantidad": cantidad, "disponible": disponible } }

            # hace la actualizacion del registro del medicamento
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
    
    # retorna la respuesta json del api
    return jsonify(respuesta)

# Servicio para crear un medicamento
@app.route('/crearmedicamento', methods=["POST"])
def crearmedicamento():  
    respuesta = {}
    try:
        # asigna a una variable el body request de la peticion
        body = request.get_json()
        # Consulta si el medicamento ya existe si no existe lo crea
        if(db.medicamentos.find({"descripcion" :body["descripcion"]}).count() > 0):            
            # asigna a un objeto json la respuesta de que el medicamento ya esta creado
            respuesta = {
                "exitoso": False,
                "mensaje": "El medicamento: " + body["descripcion"] + ", ya se encuentra creado en la base de datos"
            }
        else:
            # crea el medicamento
            x = db.medicamentos.insert_one(body)     

             # asigna a un objeto json la respuesta de que se creo correctamente el medicamento
            respuesta = {
                "exitoso": True,
                "mensaje": "Se ha creado el medicamento correctamente"
            }
    except:
        respuesta = {
            "exitoso": False,
            "mensaje": "Ha ocurrido un error guardando el medicamento"
        }  
    # retorna la respuesta json del api 
    return jsonify(respuesta)

# Servicio para actualizar los datos de un medicamento
@app.route('/actualizarmedicamento', methods=["PUT"])
def actualizarmedicamento():  
    respuesta = {}
    try:
        body = request.get_json()
        # Consulta si el medicamento ya existe para actualizarlo si no indica que no existe
        if(db.medicamentos.find({"descripcion": body["descripcion"]}).count() > 0):
            # recupera de la base de datos el registro del medicamento
            existente = db.medicamentos.find_one({"descripcion": body["descripcion"]}) 
            myquery = { "_id": existente["_id"] }

            # asigna a un objeto json la actualizacion de los campos y valores del medicamento
            newvalues = { "$set":
                            { 
                                "disponible": body["disponible"], 
                                "cantidad": body["cantidad"], 
                                "observacion": body["observacion"], 
                            }
                        }
            
            # actualiza el registro en la base de datos
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

    # retorna la respuesta json de la api 
    return jsonify(respuesta)

if __name__ == "__main__":
    app.run(debug=True)
