import os
from flask import Flask,  request, jsonify
from flask_cors import CORS, cross_origin
from flask_mysqldb import MySQL
from Config import  MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
import datetime

app = Flask(__name__)

origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "https://127.0.0.1:8000",
    "https://192.168.100.6:8000"
]
CORS(app, resources={r"/*": {"origins": origins}}, supports_credentials=True)

@app.after_request
def apply_cors(response):
    origin = request.headers.get('Origin')
    if origin in origins:
        response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS, PUT, DELETE"
    response.headers["Access-Control-Allow-Headers"] = "Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization"
    return response


# Configuración de la base de datos
app.config['MYSQL_HOST'] = MYSQL_HOST
app.config['MYSQL_USER'] = MYSQL_USER
app.config['MYSQL_PASSWORD'] = MYSQL_PASSWORD
app.config['MYSQL_DB'] = MYSQL_DB
mysql = MySQL(app)


@app.route("/")
def hello():
    return "¡Hola, mundo!"

@app.route('/users', methods=['GET'])
@cross_origin()
def listar_usuarios():
    try:
        cursor = mysql.connection.cursor()
        sql = """SELECT
            u.Matricula,
            u.Nombre,
            u.ApellidoPaterno,
            u.ApellidoMaterno,
            u.Genero,
            u.PlanAlimenticio_Codigo,
            u.Estatura,
            u.Peso,
            u.IMC,
            p.Codigo AS PlanCodigo,
            p.Proteina,
            p.Carbohidrato,
            p.Grasa
        FROM users u
        INNER JOIN planAlimenticio p
        ON u.PlanAlimenticio_Codigo = p.Codigo"""
        cursor.execute(sql)
        datos = cursor.fetchall()

        usuarios = []
        for fila in datos:
            usuario = {
                'Matricula': fila[0],
                'Nombre': fila[1],
                'ApellidoPaterno': fila[2],
                'ApellidoMaterno': fila[3],
                'Genero': fila[4],
                'PlanAlimenticio_Codigo': fila[5],
                'Estatura': fila[6],
                'Peso': fila[7],
                'IMC': fila[8],
                'Plan': {
                    'Codigo': fila[9],
                    'Proteina': fila[10],
                    'Carbohidrato': fila[11],
                    'Grasa': fila[12]
                }
            }
            usuarios.append(usuario)

        cursor.close()

        return jsonify(usuarios), 200

    except Exception as ex:
        return jsonify({'mensaje': f"Error al listar usuarios: {str(ex)}"}), 500


# Ruta para calcular consumo energético
@app.route('/consumo_energetico', methods=['POST', 'GET'])
def calcular_consumo():
    if request.method == 'POST':
        try:
            data = request.json
            matricula = data.get("matricula")

            if not matricula:
                return jsonify({"mensaje": "La matrícula es requerida"}), 400

            # Código para manejar POST
            cursor = mysql.connection.cursor()

            # Obtener el plan alimenticio del usuario
            sql = """SELECT Proteina, Carbohidrato, Grasa 
                     FROM planAlimenticio 
                     WHERE Codigo = (SELECT PlanAlimenticio_codigo FROM users WHERE matricula = %s)"""
            cursor.execute(sql, (matricula,))
            plan = cursor.fetchone()

            if not plan:
                return jsonify({"mensaje": "El usuario no tiene un plan asignado"}), 404

            P, C, G = plan  # Proteína, Carbohidrato y Grasa

            # Calcular el consumo energético con derivadas parciales
            E = (4 * P) + (4 * C) + (9 * G)
            dE_dP, dE_dC, dE_dG = 4, 4, 9

            # Guardar el consumo energético en la base de datos con el mes actual
            mes_actual = datetime.datetime.now().strftime("%Y-%m")
            sql_insert = """INSERT INTO consumo_energetico (matricula, mes, consumo) 
                            VALUES (%s, %s, %s)"""
            cursor.execute(sql_insert, (matricula, mes_actual, E))
            mysql.connection.commit()
            cursor.close()

            return jsonify({
                "matricula": matricula,
                "nutrientes": {"Proteina": P, "Carbohidrato": C, "Grasa": G},
                "derivadas_parciales": {"dE_dP": dE_dP, "dE_dC": dE_dC, "dE_dG": dE_dG},
                "energia_total": E
            }), 200

        except Exception as ex:
            return jsonify({"mensaje": f"Error al calcular consumo energético: {str(ex)}"}), 500

    elif request.method == 'GET':
        try:
            # Obtener datos desde la base de datos
            cursor = mysql.connection.cursor()

            # Obtener el plan alimenticio del usuario
            sql = """SELECT Proteina, Carbohidrato, Grasa 
                     FROM planAlimenticio 
                     WHERE Codigo = (SELECT PlanAlimenticio_codigo FROM users WHERE matricula = 1)"""
            cursor.execute(sql)
            plan = cursor.fetchone()

            if not plan:
                return jsonify({"mensaje": "El usuario no tiene un plan asignado"}), 404

            P, C, G = plan  # Proteína, Carbohidrato y Grasa

            # Calcular el consumo energético con derivadas parciales
            E = (4 * P) + (4 * C) + (9 * G)
            dE_dP, dE_dC, dE_dG = 4, 4, 9

            # Guardar el consumo energético en la base de datos con el mes actual
            mes_actual = datetime.datetime.now().strftime("%Y-%m")
            sql_insert = """INSERT INTO consumo_energetico (matricula, mes, consumo) 
                            VALUES (%s, %s, %s)"""
            cursor.execute(sql_insert, ('A001', mes_actual, E))
            mysql.connection.commit()
            cursor.close()

            return jsonify({
                "matricula": 'A001',
                "nutrientes": {"Proteina": P, "Carbohidrato": C, "Grasa": G},
                "derivadas_parciales": {"dE_dP": dE_dP, "dE_dC": dE_dC, "dE_dG": dE_dG},
                "energia_total": E
            }), 200

        except Exception as ex:
            return jsonify({"mensaje": f"Error al calcular consumo energético: {str(ex)}"}), 500


@app.route('/tasa_cambio/<int:matricula>', methods=['GET'])
@cross_origin()
def obtener_tasa_cambio(matricula):
    try:
        cursor = mysql.connection.cursor()
        
        # Obtener los últimos 2 meses de consumo
        sql = """SELECT mes, consumo FROM consumo_energetico 
                 WHERE matricula = %s 
                 ORDER BY mes DESC LIMIT 2"""
        cursor.execute(sql, (matricula,))
        datos = cursor.fetchall()

        if len(datos) < 2:
            return jsonify({"mensaje": "No hay suficientes datos para calcular la tasa de cambio"}), 400

        mes_actual, consumo_actual = datos[0]
        mes_anterior, consumo_anterior = datos[1]

        # Calcular tasa de cambio
        tasa_cambio = ((consumo_actual - consumo_anterior) / consumo_anterior) * 100

        return jsonify({
            "matricula": matricula,
            "mes_anterior": mes_anterior,
            "consumo_anterior": consumo_anterior,
            "mes_actual": mes_actual,
            "consumo_actual": consumo_actual,
            "tasa_cambio": tasa_cambio
        }), 200

    except Exception as ex:
        return jsonify({"mensaje": f"Error al obtener la tasa de cambio: {str(ex)}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
