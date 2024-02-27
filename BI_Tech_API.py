# -*- coding: utf-8 -*-
# @Time    : 2023/09/18 13:38
# @Author  : Sumiyoshi Lab D1 Chenyutong
# @FileName: BI_Tech_API.py
from flask import Flask, request, jsonify
import pymysql
import bcrypt
import os

app = Flask(__name__)

# MySQL
MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'default_password')
MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'BI_Tech')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if check_credentials(username, password):
        return jsonify({"status": "success", "message": "Login successful"})
    else:
        return jsonify({"status": "failure", "message": "Invalid username or password"}), 401

def check_credentials(username, password):
    connection = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        port=MYSQL_PORT
    )

    try:
        with connection.cursor() as cursor:
            sql = "SELECT password FROM raspberry_UserID WHERE username=%s"
            cursor.execute(sql, (username,))
            stored_password = cursor.fetchone()
            if stored_password and bcrypt.checkpw(password.encode('utf-8'), stored_password[0].encode('utf-8')):
                return True
            return False
    except Exception as e:
        print(f"Database error: {e}")
        return False
    finally:
        connection.close()

@app.route('/check_username', methods=['POST'])
def check_username():
    data = request.json
    username = data.get('username')

    connection = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        port=MYSQL_PORT
    )

    try:
        with connection.cursor() as cursor:
            sql = "SELECT 1 FROM raspberry_UserID WHERE username=%s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            if result:
                return jsonify({"status": "taken"})
            else:
                return jsonify({"status": "available"})
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection.close()

@app.route('/fetch_user_data', methods=['POST'])
def fetch_user_data():
    data = request.json
    username = data.get('username')

    user_data = get_user_data(username)
    if user_data:
        return jsonify({"status": "success", **user_data})
    else:
        return jsonify({"status": "failure", "message": "User not found"}), 404

def get_user_data(username):
    connection = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        port=MYSQL_PORT
    )

    user_data = {}
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM raspberry_UserID WHERE username=%s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            if result:
                user_data = {
                    'username': result[0],
                    'score': result[4]
                }
    except Exception as e:
        print(f"Database error: {e}")
    finally:
        connection.close()

    return user_data

@app.route('/get_rankings', methods=['GET'])
def get_rankings():
    connection = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        port=MYSQL_PORT
    )

    rankings = []
    try:
        with connection.cursor() as cursor:
            sql = "SELECT username, score FROM raspberry_UserID ORDER BY score DESC"
            cursor.execute(sql)
            results = cursor.fetchall()
            for result in results:
                rankings.append({"username": result[0], "score": result[1]})

    except Exception as e:
        print(f"Database error: {e}")
    finally:
        connection.close()

    return jsonify(rankings)

@app.route('/update_score', methods=['POST'])
def update_score():
    data = request.json
    username = data.get('username')
    score = data.get('score')

    connection = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        port=MYSQL_PORT
    )
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE raspberry_UserID SET score = score + %s WHERE username = %s"
            affected_rows = cursor.execute(sql, (score, username))
            connection.commit()
            if affected_rows:
                return jsonify({"status": "success", "message": "Score updated successfully"})
            else:
                return jsonify({"status": "failure", "message": "No rows updated"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection.close()

@app.route('/get_set_temperature', methods=['POST'])
def get_set_temperature():
    username = request.json.get('username')

    connection = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        port=MYSQL_PORT
    )

    try:
        with connection.cursor() as cursor:
            sql = "SELECT Set_point FROM raspberry/Set_point WHERE username=%s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            if result:
                return jsonify({"status": "success", "set_temperature": result[0]})
            else:
                return jsonify({"status": "failure", "message": "User not found or no set temperature available"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection.close()

@app.route('/get_data', methods=['POST'])
def get_data():
    table_name = request.json.get('table_name')

    if table_name not in ['raspberry/mqtt', 'raspberry/mqtt2', 'raspberry/mqtt3', 'raspberry/mqtt4', 'raspberry/mqtt5']:
        return jsonify({"status": "failure", "message": "Invalid table name"}), 400

    connection = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        port=MYSQL_PORT
    )

    data_columns = ["Time", 'Indoor_Temperature', "Globe_temperature", "Pressure", "Humidity",
                    "Mean_radiant_temperature", "Wind_Speed", "PMV", 'co2', 'pm25', 'pm10']

    try:
        with connection.cursor() as cursor:
            sql = f"SELECT {', '.join(data_columns)} FROM {table_name}"
            cursor.execute(sql)
            results = cursor.fetchall()
            data = []
            for result in results:
                data.append(dict(zip(data_columns, result)))

            return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        connection.close()

@app.route('/change_password', methods=['POST'])
def change_password():
    data = request.json
    username = data.get('username')
    new_password = data.get('new_password')

    if username and new_password:
        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

        connection = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            port=MYSQL_PORT
        )

        try:
            with connection.cursor() as cursor:
                sql = "UPDATE raspberry_UserID SET password=%s WHERE username=%s"
                affected_rows = cursor.execute(sql, (hashed_password.decode('utf-8'), username))
                connection.commit()

                if affected_rows:
                    return jsonify({"status": "success", "message": "Password updated successfully"})
                else:
                    return jsonify({"status": "failure", "message": "No rows updated"}), 400

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

        finally:
            connection.close()
    else:
        return jsonify({"status": "failure", "message": "Username and new password required"}), 400


