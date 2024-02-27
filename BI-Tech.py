import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QPushButton, QSlider, QLineEdit, QFormLayout, \
    QDialog, QGridLayout, QScrollArea, QMainWindow, QMessageBox, QCheckBox, QComboBox, QTextEdit
from PyQt5.QtWidgets import QHBoxLayout, QInputDialog
from PyQt5.QtCore import Qt, QTimer , QSize
from PyQt5.QtCore import pyqtSignal
import paho.mqtt.client as mqtt
import psutil
import threading
from datetime import datetime
import csv
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import QCoreApplication , QPropertyAnimation, pyqtProperty
from PyQt5.QtGui import QPixmap,QIcon , QMovie, QFont, QPalette,  QColor
import json
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import requests
import time
from pynput import mouse, keyboard
import os
import win32api
from pycaw.pycaw import AudioUtilities
from paho.mqtt import client as mqtt_client
from plyer import notification
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pymysql



class GlowingLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._color = QColor(255, 255, 255)
        self.animation = QPropertyAnimation(self, b'color', self)
        self.animation.setStartValue(QColor(255, 255, 255))
        self.animation.setEndValue(QColor(255, 0, 0))
        self.animation.setDuration(5000)
        self.animation.setLoopCount(-1)  # 循环无限次
        self.animation.start()

    @pyqtProperty(QColor)
    def color(self):
        return self._color

    @color.setter
    def color(self, color):
        self._color = color
        palette = self.palette()
        palette.setColor(QPalette.WindowText, self._color)
        self.setPalette(palette)

class InfoModule(QWidget):
    def __init__(self, main_program, label_name, gradient_start, gradient_end):
        super().__init__()
        self.main_program = main_program  # 保存 main_program 作为属性
        self.label_name = label_name

        self.title = label_name
        self.value = QLabel()

        self.gradient_start = gradient_start
        self.gradient_end = gradient_end

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setStyleSheet(f"""
            QLabel {{
                font-family: UD デジタル 教科書体 NK-R;
                font-size: 18px;
                border-radius: 10px;
                color:white;
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {self.gradient_start}, stop:1 {self.gradient_end});
                padding: 10px;
            }}
        """)

        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)  # Center align the text
        self.value = QLabel()
        self.value.setAlignment(Qt.AlignCenter)  # Center align the text

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.value)
        self.setLayout(self.layout)

    def update_value(self, new_value):
        self.value.setText(new_value)

    def mousePressEvent(self, event):
        # 当 InfoModule 被点击时，调用 main_program 的 show_trend_chart 函数
        self.main_program.show_trend_chart(self.label_name)
        super().mousePressEvent(event)

# 日本语
# LABEL_TO_DB_COLUMN_MAPPING = {
#     '室内温度': 'Indoor_Temperature',
#     '黒球温度': 'Globe_temperature',
#     '気圧': 'Pressure',
#     '湿度': 'Humidity',
#     '平均放射温度': 'Mean_radiant_temperature',
#     '気流': 'Wind_Speed',
#     'PMV': 'PMV',
#     '二酸化炭素': 'co2',
#     '空調の設定温度': 'Set_Point',  # 需要你确认并提供实际列名
#     '空調消費量予測': 'HVAC_Consumption',  # 需要你确认并提供实际列名
#     'PM2.5': 'pm25',
#     'PM10': 'pm10',
# }
LABEL_TO_DB_COLUMN_MAPPING = {
    'Indoor Air Temperature': 'Indoor_Temperature',
    'Globe Temperature': 'Globe_temperature',
    'Pressure': 'Pressure',
    'Relative Humidity': 'Humidity',
    'Mean Radiant Temperature': 'Mean_radiant_temperature',
    'Wind Speed': 'Wind_Speed',
    'PMV': 'PMV',
    'CO2': 'co2',
    'AC set temperature': 'Set_Point',  # 需要你确认并提供实际列名
    'Energy Consumption Prediction': 'HVAC_Consumption',  # 需要你确认并提供实际列名
    'PM2.5': 'pm25',
    'PM10': 'pm10',
}
from matplotlib.dates import DateFormatter, HourLocator

class TrendDialog(QDialog):
    def __init__(self, label_name):
        super().__init__()
        self.setWindowIcon(QIcon('Fig/B.ico'))
        self.setStyleSheet("""
                            QDialog {
                                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d5eded, stop:1 #E0B0FF);
                            }
                        """)
        self.label_name = label_name
        self.db_column_name = LABEL_TO_DB_COLUMN_MAPPING.get(label_name, label_name)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Creating a figure and setting up the canvas for plotting
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Fetch and plot data from the database
        self.fetch_and_plot_data()

        self.setLayout(layout)

    def fetch_and_plot_data(self):
        data = self.get_label_data(self.label_name)

        # 将字符串时间戳转换为datetime对象
        timestamps = [datetime.strptime(item['timestamp'], "%Y/%m/%d %H:%M:%S") for item in data]
        values = [item['value'] for item in data]

        # Plotting the data
        self.ax.plot(timestamps, values)

        # 设置X轴的刻度和标签
        self.ax.xaxis.set_major_locator(HourLocator())
        self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))

        self.ax.set_title(f"Trend for {self.db_column_name} in the last 24 hours")
        self.ax.set_xlabel('Time (hours)')
        self.ax.set_ylabel('Value')

        # 为了更好的显示，您可以选择旋转X轴的标签
        plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45)

        self.canvas.draw()

    def get_label_data(self, label_name):  # 注意这里我们添加了 self 参数
        connection = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            port=MYSQL_PORT
        )
        db_column_name = LABEL_TO_DB_COLUMN_MAPPING.get(label_name, label_name)
        label_data = []
        try:
            with connection.cursor() as cursor:
                # 确保此查询是针对正确的表进行的，并且选择了正确的列
                sql = f"SELECT Time, {db_column_name} FROM raspberry_mqtt5 WHERE Time >= NOW() - INTERVAL 1 DAY"
                cursor.execute(sql)
                result = cursor.fetchall()
                for row in result:
                    label_data.append({"timestamp": str(row[0]), "value": row[1]})
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            connection.close()

        return label_data


class GifDialog(QDialog):
    def __init__(self, parent=None):
        super(GifDialog, self).__init__(parent)
        self.setWindowTitle("BI-Tech Networkconnecting")
        # Set up the GIF label
        self.gif_label = QLabel(self)
        gif_movie = QMovie('Fig/Networkconnecting.gif')  # Add the path to your GIF here
        self.gif_label.setMovie(gif_movie)
        gif_movie.start()

        layout = QVBoxLayout()
        layout.addWidget(self.gif_label)
        self.setLayout(layout)

        # Set up a timer to close the dialog after 10 seconds
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close)
        self.timer.start(10000)  # 10 seconds in milliseconds

class ImageDialog(QDialog):
    def __init__(self, parent=None):
        super(ImageDialog, self).__init__(parent)
        self.setWindowTitle("システムの位置")
        # Set up the image label
        self.image_label = QLabel(self)
        pixmap = QPixmap('Fig/background_6.png')  # Add the path to your image here
        self.image_label.setPixmap(pixmap)

        # Close button
        self.close_button = QPushButton("Close", self)
        self.close_button.setFont(QtGui.QFont('UD デジタル 教科書体 N-B', 15))
        self.close_button.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.close_button)

        self.setLayout(layout)


MYSQL_USER = 'root'
MYSQL_PASSWORD = 'chenyutong'
MYSQL_HOST = '127.0.0.1'
MYSQL_DATABASE = 'BI_Tech'
MYSQL_PORT = 3306


class LoginDialog(QDialog):
    def __init__(self, main_program=None, username=None):
        super().__init__()
        self.main_program = main_program
        self.username = username
        self.setWindowIcon(QIcon('Fig/B.ico'))
        self.setStyleSheet("""
                    QDialog {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d5eded, stop:1 #E0B0FF);
                    }
                """)
        self.initUI()
        self.selected_topic = None

    def initUI(self):
        self.layout = QVBoxLayout()

        self.title = QLabel("ようこそ<br>BI-Tech システムへ")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QtGui.QFont('UD デジタル 教科書体 N-B', 30))

        # BI-Tech logo
        self.logo1 = QLabel()
        movie = QMovie('Fig/BI-Tech.gif')
        movie.setScaledSize(QtCore.QSize(200, 200))  # Set the size of the movie
        self.logo1.setMovie(movie)
        movie.start()

        # Header layout (title and logo)
        self.header_layout = QHBoxLayout()
        self.header_layout.addWidget(self.title)
        self.header_layout.addWidget(self.logo1)

        # Add spacers to center the header layout
        self.header_layout.insertStretch(0)
        self.header_layout.insertStretch(4)

        # Add header layout to main layout
        self.layout.addLayout(self.header_layout)

        # Form layout for the username and password fields
        self.form_layout = QFormLayout()
        self.form_font = QtGui.QFont('Arial', 15)

        # 用户名输入框
        self.entry_username = QLineEdit()
        self.entry_username.setFont(self.form_font)
        username_label = QLabel("アカウント")
        username_label.setFont(QtGui.QFont('UD デジタル 教科書体 N-B', 15))

        password_label = QLabel("パスワード")
        password_label.setFont(QtGui.QFont('UD デジタル 教科書体 N-B', 15))

        self.form_layout.addRow( username_label, self.entry_username)

        # 密码输入框
        self.entry_password = QLineEdit()
        self.entry_password.setEchoMode(QLineEdit.Password)
        self.entry_password.setFont(self.form_font)
        self.form_layout.addRow(password_label, self.entry_password)

        self.layout.addLayout(self.form_layout)

        # Create the notion label
        self.Notion_label = QLabel("***システム番号と位置は作成ページを参照 2023 Sumiyoshi Lab. All Rights Reserved*** ")
        self.Notion_label.setFont(QtGui.QFont('UD デジタル 教科書体 N-B', 10))
        self.Notion_label.setAlignment(Qt.AlignCenter)

        # Create a layout for the notion label (in case you want to add more widgets alongside it in the future)
        self.notion_layout = QHBoxLayout()
        self.notion_layout.addWidget(self.Notion_label)

        # Add the notion layout to the main layout
        self.layout.addLayout(self.notion_layout)

        # 登录按钮
        self.login_button = QPushButton("登録")
        button_font = QFont('UD デジタル 教科書体 N-B', 15)

        button_font.setBold(True)
        self.login_button.setFont(button_font)
        self.login_button.clicked.connect(self.login)

        # 注册按钮
        self.signin_button = QPushButton("アカウントを作る")
        self.signin_button.setFont(button_font)
        self.signin_button.clicked.connect(self.signin)

        # 创建一个水平布局并将两个按钮添加到布局中
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.signin_button)

        # 将按钮布局添加到主布局中
        self.layout.addLayout(button_layout)
        self.system_position_combobox = QComboBox()
        positions = ['部屋番号をご選んでください',"位置1", "位置2", "位置3", "位置4",'位置5']  # 可以替换为您想要的系统位置
        self.system_position_combobox.addItems(positions)
        self.system_position_combobox.setFont(QtGui.QFont('UD デジタル 教科書体 N-B', 15))
        self.layout.addWidget(self.system_position_combobox)
        # 将布局设置为窗口的主布局
        self.setLayout(self.layout)

    def login(self):
        username = self.entry_username.text()
        password = self.entry_password.text()

        # Check if the selected position is '部屋番号'
        position = self.system_position_combobox.currentText()
        if position == '部屋番号をご選んでください':
            msg = QMessageBox(self)
            msg.setWindowTitle("部屋番号エラー")
            msg.setText("正しい部屋番号を選択してください。")
            msg.setFont(QtGui.QFont('UD デジタル 教科書体 N-B', 15))
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        if self.check_credentials(username, password):
            self.username = username
            if self.main_program:  # Ensure main_program instance is available
                self.main_program.username = self.username
            # Determine the topic based on user's chosen position
            if position == '位置1':
                topic_to_set = 'raspberry/mqtt'
            else:
                # Extract the number from the position string
                position_number = ''.join([ch for ch in position if ch.isdigit()])
                topic_to_set = f'raspberry/mqtt{position_number}'
            self.main_program.set_current_topic(topic_to_set)
            self.accept()
            self.show_gif_and_proceed()
            report_dialog = behavior_report(username=username)  # Use the logged-in username to initialize
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password", QMessageBox.Ok)

    def check_credentials(self, username, password):
        API_ENDPOINT = "https://bitech.loca.lt/login"
        API_ENDPOINT = "http://192.168.83.6:5022/login"
        # Send the username and password to the API for verification
        data = {
            "username": username,
            "password": password
        }

        try:
            response = requests.post(API_ENDPOINT, json=data)
            response.raise_for_status()

            # Check the "status" key in the response
            result = response.json()
            if result.get("status") == "success":
                return True
            else:
                return False

        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"There was an error connecting to the API: {e}", QMessageBox.Ok)
            return False

    def signin(self):
        self.hide()
        self.register_dialog = RegisterDialog(self)
        self.register_dialog.exec_()

    def show_gif_and_proceed(self):
        # Show the GIF dialog
        self.gif_dialog = GifDialog(self)
        self.gif_dialog.exec_()

class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_program = MainProgram
        self.setWindowIcon(QIcon('Fig/B.ico'))
        self.setStyleSheet("""
                    QDialog {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d5eded, stop:1 #E0B0FF);
                    }
                """)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.title = QLabel("アカウントを作成")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QtGui.QFont('UD デジタル 教科書体 N-B', 30))

        self.layout.addWidget(self.title)

        self.form_layout = QFormLayout()
        self.form_font = QtGui.QFont('Arial', 15)

        self.entry_username = QLineEdit()
        self.entry_username.setFont(self.form_font)
        username_label = QLabel("ニックネーム")
        username_label.setFont(QtGui.QFont('UD デジタル 教科書体 N-B', 15))

        self.entry_password = QLineEdit()
        self.entry_password.setEchoMode(QLineEdit.Password)
        self.entry_password.setFont(self.form_font)
        password_label = QLabel("パスワード")
        password_label.setFont(QtGui.QFont('UD デジタル 教科書体 N-B', 15))

        self.entry_email = QLineEdit()
        self.entry_email.setFont(self.form_font)
        email_label = QLabel("メール")
        email_label.setFont(QtGui.QFont('UD デジタル 教科書体 N-B', 15))

        self.form_layout.addRow(username_label, self.entry_username)
        self.form_layout.addRow(password_label, self.entry_password)
        self.form_layout.addRow(email_label, self.entry_email)

        self.layout.addLayout(self.form_layout)

        # 添加图片对话框按钮
        self.image_button = QPushButton("システムの位置")
        self.image_button.setFont(QtGui.QFont('UD デジタル 教科書体 N-B', 15))
        self.image_button.clicked.connect(self.show_image_dialog)
        self.layout.addWidget(self.image_button)

        # 添加系统位置选择
        self.system_position_combobox = QComboBox()
        positions = ["位置1", "位置2", "位置3", "位置4",'位置5']  # 可以替换为您想要的系统位置
        self.system_position_combobox.addItems(positions)
        self.system_position_combobox.setFont(QtGui.QFont('UD デジタル 教科書体 N-B', 15))
        self.layout.addWidget(self.system_position_combobox)

        self.register_button = QPushButton("作成")
        button_font = QFont('UD デジタル 教科書体 N-B', 15)
        button_font.setBold(True)
        self.register_button.setFont(button_font)
        self.register_button.clicked.connect(self.register_user)

        self.layout.addWidget(self.register_button)

        self.setLayout(self.layout)
        self.back_to_login_button = QPushButton("ログインに戻る")
        self.back_to_login_button.setFont(QtGui.QFont('UD デジタル 教科書体 N-B', 15))
        self.back_to_login_button.clicked.connect(self.back_to_login)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.back_to_login_button)

        self.layout.addLayout(button_layout)
        self.setLayout(self.layout)

    def show_image_dialog(self):
        self.image_dialog = ImageDialog(self)
        self.image_dialog.exec_()

    def register_user(self):
        username = self.entry_username.text()
        password = self.entry_password.text()  # In reality, hash this!
        email = self.entry_email.text()
        system_position = self.system_position_combobox.currentText()

        # Check if the username is available
        if not self.is_username_available(username):
            msg = QMessageBox(self)
            msg.setWindowTitle("ユーザー名が取られています")
            msg.setText("このユーザー名はすでに取られています。別のものを選んでください。")
            msg.setFont(QtGui.QFont('UD デジタル 教科書体 N-B', 15))
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        # Example payload (you'd probably want something more complex/encrypted)
        payload = f"{username},{password},{email},{system_position}"

        # Send to MQTT server
        broker_address = "broker.emqx.io"
        broker_address = "broker.hivemq.com"
        client = mqtt_client.Client("chenyutong")  # 使用一个唯一的客户端ID
        client.username_pw_set("emqx", "public")  # 设置MQTT的用户名和密码
        client.connect(broker_address, 1883)  # 通常MQTT使用1883端口
        client.publish("raspberry/UserID", payload)
        time.sleep(2)  # wait for 2 seconds to ensure message is published
        client.disconnect()  # Disconnect from the MQTT broker

        self.accept()
        self.close()

        # 重新启动应用程序
        os.execv(sys.executable, ['BI-Tech.py'] + sys.argv)
        # 重新启动应用程序
        # os.startfile('BI-Tech.exe')
        os._exit(0)

    def back_to_login(self):
        self.hide()
        login_dialog = LoginDialog()
        login_dialog.exec_()
        self.close()

    def is_username_available(self, username):
        API_ENDPOINT = "https://bitech.loca.lt/check_username"
        API_ENDPOINT = "http://192.168.83.6:5022/check_username"

        try:
            response = requests.post(API_ENDPOINT, json={"username": username})
            response.raise_for_status()

            result = response.json()
            if result.get("status") == "available":
                return True
            else:
                return False

        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"There was an error connecting to the API: {e}", QMessageBox.Ok)
            return False

class ProfileDialog(QDialog):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.initUI()
        self.setWindowIcon(QIcon('Fig/B.ico'))
        self.setStyleSheet("""
                    QDialog {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d5eded, stop:1 #E0B0FF);
                    }
                """)

    def initUI(self):
        self.setWindowTitle("個人情報")
        self.layout = QVBoxLayout()
        self.logo_label = QLabel()
        pixmap = QPixmap('Fig/profile.png')
        self.logo_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.logo_label)

        # Fetch user data
        user_data = self.fetch_user_data()

        # Assuming user_data is a dictionary with keys 'username', 'score', etc.
        self.time_label = QLabel(f"アカウント作成時間: {user_data.get('Time', 'N/A')}")
        self.username_label = QLabel(f"ユーザーネーム: {user_data.get('username', 'N/A')}")
        self.score_label = QLabel(f"省エネポイント: {user_data.get('score', 'N/A')}")
        self.username_label.setFont(QFont("UD デジタル 教科書体 N-B", 15))
        self.score_label.setFont(QFont("UD デジタル 教科書体 N-B", 15))
        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.score_label)

        button_layout = QHBoxLayout()
        self.changepasswd = QPushButton("パスワードを修正")
        self.changepasswd.setFont(QFont("UD デジタル 教科書体 N-B", 15))
        self.changepasswd.clicked.connect(self.change_password)
        self.back_button = QPushButton("ホームページに戻る")
        self.back_button.setFont(QFont("UD デジタル 教科書体 N-B", 15))
        self.back_button.clicked.connect(self.reject)

        button_layout.addWidget(self.changepasswd)
        button_layout.addWidget(self.back_button)

        self.layout.addLayout(button_layout)  # Use self.layout
        self.setLayout(self.layout)

    def fetch_user_data(self):
        API_ENDPOINT = "https://bitech.loca.lt/fetch_user_data"
        API_ENDPOINT = "http://192.168.83.6:5022/fetch_user_data"


        data = {
            "username": self.username
        }

        user_data = {}
        try:
            response = requests.post(API_ENDPOINT, json=data)
            response.raise_for_status()

            result = response.json()

            if result.get("status") == "success":
                user_data = {
                    'username': result.get('username'),
                    'score': result.get('score')
                    # Add more fields as needed
                }
        except requests.RequestException as e:
            print(f"API error: {e}")

        return user_data

    def change_password(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('パスワードを修正')
        layout = QVBoxLayout()
        font = QFont("UD デジタル 教科書体 N-B", 15)

        label = QLabel('新しいパスワードを入力してください:')
        label.setFont(font)

        lineEdit = QLineEdit()
        lineEdit.setFont(font)

        button_layout = QHBoxLayout()

        okButton = QPushButton('はい')
        okButton.setFont(font)
        okButton.clicked.connect(dialog.accept)

        cancelButton = QPushButton('キャンセル')
        cancelButton.setFont(font)
        cancelButton.clicked.connect(dialog.reject)

        layout.addWidget(label)
        layout.addWidget(lineEdit)
        button_layout.addWidget(okButton)
        button_layout.addWidget(cancelButton)

        dialog.setLayout(layout)

        result = dialog.exec_()

        if result == QDialog.Accepted:
            new_password = lineEdit.text()

            # Call API to change password
            API_ENDPOINT = "https://bitech.loca.lt/change_password"
            API_ENDPOINT = "http://192.168.83.6:5022/change_password"

            data = {
                "username": self.username,
                "new_password": new_password
            }

            try:
                response = requests.post(API_ENDPOINT, json=data)
                response.raise_for_status()

                result = response.json()

                if result.get("status") == "success":
                    QMessageBox.information(self, '成功', 'パスワードが正常に更新されました')
                else:
                    QMessageBox.warning(self, '失敗', 'パスワードの更新に失敗しました')

            except requests.RequestException as e:
                QMessageBox.critical(self, 'エラー', f"APIエラー: {e}")

        elif result == QDialog.Rejected:
            QMessageBox.warning(self, '失敗', 'パスワードは空にできません')


class VoteDialog(QWidget):
    def __init__(self, main_program, username):
        super().__init__()
        self.main_program = main_program
        self.username = username

        self.setWindowIcon(QIcon('B.ico'))
        self.vote_timer = QTimer(self)
        self.main_program = main_program
        self.layout = QVBoxLayout()
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d5eded, stop:1 #E0B0FF);
            }
        """)
        self.vote_label = QLabel("😊 How do you feel about the current thermal comfort? 😊")
        self.vote_label.setFont(QtGui.QFont('Comic Sans MS', 20))
        self.vote_slider = QSlider(Qt.Horizontal)
        self.vote_slider.setRange(-3, 3)
        self.vote_slider.setTickInterval(1)
        self.vote_slider.setTickPosition(QSlider.TicksBelow)
        self.vote_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 10px;
                background: #efefef;
            }
            QSlider::handle:horizontal {
                width: 20px;
                background: pink;
                margin: -5px 0;
                border-radius: 10px;
            }
        """)
        # Cold Label
        self.vote_label_cold = QLabel("🥶 Cold 🥶")
        self.vote_label_cold.setFont(QtGui.QFont('Comic Sans MS', 16))

        # Hot Label
        self.vote_label_hot = QLabel("🔥 Hot 🔥")
        self.vote_label_hot.setFont(QtGui.QFont('Comic Sans MS', 16))

        # Slider for voting
        self.vote_slider = QSlider(Qt.Horizontal)
        self.vote_slider.setRange(-3, 3)
        self.vote_slider.setValue(0)
        self.vote_slider.setTickPosition(QSlider.TicksBelow)  # Adding ticks
        self.vote_slider.setTickInterval(1)  # Interval for the ticks
        self.vote_slider.valueChanged.connect(self.update_explanation_label)  # Update explanation on change
        self.vote_slider.setMinimumWidth(200)  # Set a minimum width for the slider

        # Explanation Label
        self.explanation_label = QLabel()
        self.explanation_label.setFont(QtGui.QFont('Comic Sans MS', 16))  # Set font size for the explanation label
        self.update_explanation_label()  # Initialize the label with the current value

        # Layout for slider and labels
        self.slider_layout = QGridLayout()
        self.slider_layout.addWidget(self.vote_label_cold, 0, 0)
        self.slider_layout.addWidget(self.vote_slider, 0, 1)
        self.slider_layout.addWidget(self.vote_label_hot, 0, 2)
        self.slider_layout.addWidget(self.explanation_label, 1, 1, 1, 2)

        # Vote Button
        self.vote_button = QPushButton("🌟 Vote 🌟")
        self.vote_button.setFont(QtGui.QFont('Comic Sans MS', 16))
        self.vote_button.clicked.connect(self.vote)
        self.vote_checkbox = QCheckBox("1時間ごとに投票ダイアログを表示する")
        self.vote_checkbox.setFont(QtGui.QFont('UD デジタル 教科書体 N-B', 16))
        self.vote_checkbox.stateChanged.connect(self.toggle_vote_dialog)
        # Main Layout
        self.layout = QVBoxLayout()
        self.layout.addLayout(self.slider_layout)
        self.layout.addWidget(self.vote_button)
        self.layout.addWidget(self.vote_checkbox)
        self.layout.setAlignment(self.vote_checkbox, Qt.AlignCenter)
        self.setLayout(self.layout)
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.show_vote_reminder)
        self.reminder_timer.start(86400 * 1000)

    def update_explanation_label(self):
        vote_value = self.vote_slider.value()
        if vote_value  == 3:
            explanation = "非常に暑い"
        elif vote_value  == 2:
            explanation = "暑い"
        elif vote_value  == 1:
            explanation = "やや暑い"
        elif vote_value  == 0:
            explanation = "どちらでもない"
        elif vote_value  == -1:
            explanation = "やや寒い"
        elif vote_value  == -2:
            explanation = "寒い"
        elif vote_value  == -3:
            explanation = "非常に寒い"
        else:
            explanation = "未知の値"
        self.explanation_label.setText(f"Selected: {vote_value} - {explanation}")

    def vote(self):

        vote_value = self.vote_slider.value()
        explanation = self.explanation_label.text().split('-')[-1].strip()
        print(f"Vote submitted: {vote_value} - {explanation}")

        vote_value = self.vote_slider.value()
        vote_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Prepare the data
        data = {
            # Use the username from the login dialog
            'vote_time': vote_time,
            'vote_value': vote_value
        }
        # Publish the data
        broker_address = "broker.emqx.io"
        broker_address = "broker.hivemq.com"
        ClientID = 'chenyutong'
        user = 'emqx'
        password = 'public'
        port = 1883
        topic = f'raspberry/mqtt/vote1'  # Use the username from the login dialog

        client = mqtt.Client(ClientID)
        client.username_pw_set(user, password)
        client.connect(broker_address, port=port)

        client.publish(topic, json.dumps(data))

        print(f"Vote recorded: {vote_value} at {vote_time}")
        print(f"Data published to topic: {topic}")

        # Show a thank you message
        # 创建消息框
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("ありがとうございます！")
        msg_box.setText("投票していただきありがとうございます！")

        # 设置消息框的字体
        font = QtGui.QFont('UD デジタル 教科書体 NK-R', 15)
        msg_box.setFont(font)

        # 显示消息框
        msg_box.exec_()

        # Close the voting window
        self.close()

    def show_vote_reminder(self):
        # 发送通知
        notification.notify(
            title="快適性はどうですか",
            message="BI-Techに快適性を投票しましょう！",
            app_icon="Fig/B.ico",
            timeout=5,
        )

    def toggle_vote_dialog(self, state):
        if state == Qt.Checked:
            # Start the timer to show the VoteDialog every hour
            self.vote_timer.start(3600000)
        else:
            # Stop the timer
            self.vote_timer.stop()



class LabelSelectorDialog(QDialog):
    labelSelected = pyqtSignal()

    def __init__(self, main_program, username):
        super().__init__()
        self.main_program = main_program
        self.username = username
        self.setWindowIcon(QIcon('Fig/B.ico'))
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d5eded, stop:1 #E0B0FF);
            }
        """)

        self.setWindowTitle("展示するタグを選択してください")
        self.layout = QVBoxLayout()
        self.Notion2_label = QLabel(
            "ご希望の室内環境の指標をお選びください <br> ***後ほど設定から変更や追加、削除の調整も可能です*** ")
        self.Notion2_label.setFont(QtGui.QFont('UD デジタル 教科書体 N-B', 15))
        self.Notion2_label.setAlignment(Qt.AlignCenter)
        self.notion2_layout = QHBoxLayout()
        self.notion2_layout.addWidget(self.Notion2_label)
        self.layout.addLayout(self.notion2_layout)

        category_font = QFont("UD デジタル 教科書体 N-B", 20, QFont.Bold)
        category_font.setBold(True)
        category_font.setUnderline(True)


        # Initialize a QFont for the checkboxes
        checkbox_font = QFont("UD デジタル 教科書体 N-B", 15)

        # List of labels for each category
        environment_labels = ['Indoor Air Temperature', 'Globe Temperature', 'Air Pressure', 'Relative Humidity', 'Mean Radiant Temperature', 'Wind Speed', 'PMV']
        air_quality_labels = ['CO2', 'PM2.5', 'PM10']
        energy_consumption_labels = ['AC set temperature', 'Energy Consumption Prediction']

        # Create a dictionary to group the labels
        label_groups = {
            '環境情報': environment_labels,
            '空気質': air_quality_labels,
            'エネルギー消費': energy_consumption_labels
        }

        # Create checkboxes for each category
        self.checkbox_dict = {}
        for category, labels in label_groups.items():
            # Add a category label
            category_label = QLabel(category)
            category_label.setFont(category_font)
            category_label.setAlignment(Qt.AlignCenter)
            category_label.setStyleSheet("color: blue;")

            # Set tooltips for each category
            if category == '環境情報':
                category_label.setToolTip(
                    "このカテゴリは、部屋や建物の内部環境を示すさまざまなパラメータに関連しています。<br>室内温度、放射温度、湿度などの要因は、人間の快適さや健康に大きく影響します。")
            elif category == '空気質':
                category_label.setToolTip(
                    "空気の質は、健康と快適さにとって非常に重要です。<br>このカテゴリは、二酸化炭素や微粒子（PM2.5、PM10）など、呼吸器の健康に悪影響を及ぼす可能性がある空気中の汚染物質の濃度に焦点を当てています。")
            elif category == 'エネルギー消費':
                category_label.setToolTip(
                    "エネルギー消費の指標は、家電製品やシステムが使用しているエネルギーの量に関する洞察を提供します。<br>これらを監視することで、エネルギー効率と持続可能性を実現するのに役立ちます。")

            # Add the category_label to the layout AFTER setting the tooltip
            self.layout.addWidget(category_label)

            for label_name in labels:
                checkbox = QCheckBox(label_name)
                checkbox.setChecked(True)
                checkbox.setFont(checkbox_font)
                self.checkbox_dict[label_name] = checkbox
                self.layout.addWidget(checkbox)
                checkbox.stateChanged.connect(self.toggle_info_module)

        # 确定和取消按钮
        self.buttons_layout = QHBoxLayout()
        self.profile_logout_button_layout = QHBoxLayout()
        self.ok_button = QPushButton("はい")
        self.ok_button.setFont(QFont("UD デジタル 教科書体 N-B", 15))
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("いいえ")
        self.cancel_button.setFont(QFont("UD デジタル 教科書体 N-B", 15))
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button.clicked.connect(self.on_ok_clicked)
        self.register_dialog = RegisterDialog()
        # self.profile_button = QPushButton("プロフィール")
        # self.profile_button.setFont(QFont("UD デジタル 教科書体 N-B", 15))
        # self.profile_button.clicked.connect(self.show_profile)
        self.profile_button = QPushButton()
        # Set the image as an icon
        icon1 = QIcon('Fig/p.png')
        self.profile_button.setIcon(icon1)
        # Set the size of the icon (You can adjust these values as needed)
        self.profile_button.setIconSize(QSize(20, 20))  # Example size
        # Connec the button's clicked signal
        self.profile_button.clicked.connect(self.show_profile)
          # Connect to the show_login_dialog method of the main program
        # Set the image as an icon
        self.logout_button = QPushButton()
        icon2 = QIcon('Fig/logout.png')
        self.logout_button.setIcon(icon2)
        # Set the size of the icon (You can adjust these values as needed)
        self.logout_button.setIconSize(QSize(20, 20))  # Example size
        # Connec the button's clicked signal
        self.logout_button.clicked.connect(self.main_program.show_login_dialog)
        # For the profile_button
        self.profile_button.setStyleSheet("background: transparent; border: black;")

        # For the logout_button
        self.logout_button.setStyleSheet("background: transparent; border: black;")

        # self.logout_button = QPushButton("ログアウト")
        # self.logout_button.setFont(QFont("UD デジタル 教科書体 N-B", 15))
        # self.logout_button.clicked.connect(
        #     self.main_program.show_login_dialog)
        self.buttons_layout.addWidget(self.ok_button)
        self.buttons_layout.addWidget(self.cancel_button)
        self.profile_logout_button_layout.addWidget(self.profile_button)
        self.profile_logout_button_layout.addWidget(self.logout_button)
        self.layout.addLayout(self.buttons_layout)
        self.layout.addLayout(self.profile_logout_button_layout)
        self.setLayout(self.layout)

    def toggle_info_module(self):
        # 根据选择框的状态更新主窗口的info_modules的可见性
        for label_name, checkbox in self.checkbox_dict.items():
            self.main_program.info_modules[label_name].setVisible(checkbox.isChecked())

    def on_ok_clicked(self):
        self.main_program.store_checkbox_dict(self.checkbox_dict)
        self.labelSelected.emit()
        self.accept()

    def signin(self):
        self.hide()
        self.register_dialog = RegisterDialog(self)
        self.register_dialog.exec_()

    def show_profile(self):
        profile_dialog = ProfileDialog(self.username)
        profile_dialog.exec_()
        self.show()  # Show the LabelSelectorDialog again after closing the ProfileDialog


from PyQt5.QtCore import QObject, pyqtSignal, QTimer


class ScreenReminder(QObject):
    userAwaySignal = pyqtSignal(str)
    reminderSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()  # Fixed the typo here from __int__ to __init__

        # Initialize member variables
        self.last_active_time = time.time()
        self.last_wake_time = time.time() - (win32api.GetTickCount() / 1000.0)
        self.max_idle_seconds = 15*60
        self.reminder_threshold = 1800
        self.user_away_time = 0

        # Start listeners for mouse and keyboard activities
        self.mouse_listener = mouse.Listener(on_move=self.on_move, on_click=self.on_click, on_scroll=self.on_scroll)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.mouse_listener.start()
        self.keyboard_listener.start()

        # Start the QTimer to check user activity periodically
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_activity)
        self.timer.start(1000)

    def on_move(self, x, y):
        self.last_active_time = time.time()
        self.user_away_time = 0

    def on_click(self, x, y, button, pressed):
        self.last_active_time = time.time()
        self.user_away_time = 0

    def on_scroll(self, x, y, dx, dy):
        self.last_active_time = time.time()
        self.user_away_time = 0

    def on_key_press(self, key):
        self.last_active_time = time.time()
        self.user_away_time = 0

    def get_system_uptime(self):
        return win32api.GetTickCount() / 1000.0

    def check_audio_playing(self):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            volume = session.SimpleAudioVolume
            if volume.GetMute() == 0 and volume.GetMasterVolume() > 0:
                return True
        return False

    def check_activity(self):
        current_time = time.time()
        idle_time = current_time - self.last_active_time

        if idle_time > self.max_idle_seconds:
            self.user_away_time += 1
            if self.user_away_time >= self.max_idle_seconds:
                self.userAwaySignal.emit("席を離れてから10分が経過しました。\nエネルギーの節約のため、画面をスリープモードにするかシャットダウンをご検討ください。"
                                        )
            if self.user_away_time > self.reminder_threshold:
                self.reminderSignal.emit(
                    f"席を離れてから30分が経過しました")
            # if self.user_away_time > self.reminder_threshold:
            #     self.reminderSignal.emit(
            #         f"Screen has not been in use for: {time.strftime('%H:%M:%S', time.gmtime(self.user_away_time))}")



class behavior_report(QDialog):
    def __init__(self,username):
        super().__init__()
        self.username = username
        print(self.username)
        self.setWindowIcon(QIcon('Fig/B.ico'))
        self.setStyleSheet("""
                       QDialog {
                           background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #d5eded, stop:1 #E0B0FF);
                       }
                   """)
        self.total_score = 0  # Initialize total_score before calling initUI
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Energ-saving behavior report")
        self.layout = QVBoxLayout()
        self.grid_layout = QGridLayout()

        # Create 18 buttons and add them to the grid
        self.image_buttons = []
        for i in range(18):
            btn = QPushButton()
            btn.setIcon(QIcon(f"report/{i + 1}.png"))  # Assuming the images are named 1.png, 2.png, ...
            btn.setIconSize(QtCore.QSize(120, 120))  # Set the size of the icon
            btn.clicked.connect(self.add_score)  # Connect the button click to the add_score function
            self.image_buttons.append(btn)
            row = i // 6
            col = i % 6
            self.grid_layout.addWidget(btn, row, col)

        self.layout.addLayout(self.grid_layout)

        # Display total score
        self.score_label = QLabel(f"Point: {self.total_score}")
        self.score_label.setFont(QFont("UD デジタル 教科書体 N-B", 15))
        self.layout.addWidget(self.score_label)

        # Add a button for final reporting
        self.report_button = QPushButton("Report")
        self.report_button.setFont(QFont("UD デジタル 教科書体 N-B", 15))
        self.ranking_button = QPushButton("Points Ranking!")
        self.ranking_button.setFont(QFont("UD デジタル 教科書体 N-B", 15))
        self.report_button.clicked.connect(self.report_score)
        self.ranking_button.clicked.connect(self.display_rankings)
        self.layout.addWidget(self.report_button)
        self.layout.addWidget(self.ranking_button)

        self.setLayout(self.layout)

    def add_score(self):
        sender = self.sender()
        if sender in self.image_buttons:
            self.total_score += 1  # Add a score of 1 each time
            self.score_label.setText(f"Total Score: {self.total_score}")
        print(f"After add_score, username: {self.username}")

    def show_cherry_blossom(self):
        # List all files in the "cherry" directory
        gif_files = [f for f in os.listdir('cherry') if f.endswith('.gif')]

        if gif_files:
            chosen_gif = random.choice(gif_files)
            self.display_gif(os.path.join('cherry', chosen_gif))
        else:
            QMessageBox.warning(self, "Warning", "No GIF files found in the cherry folder.")

    def display_gif(self, gif_path):
        self.gif_dialog = QDialog(self)
        self.gif_dialog.setWindowTitle("Cherry Blossom")
        self.gif_dialog.setFixedSize(500, 500)

        layout = QVBoxLayout()

        gif_label = QLabel(self.gif_dialog)
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        gif_label.setAlignment(Qt.AlignCenter)

        # Keeping the QMovie object alive by making it a class attribute
        self.movie = QMovie(gif_path)
        self.movie.setScaledSize(QSize(480, 480))  # Adjust this value if needed
        self.movie.setCacheMode(QMovie.CacheAll)
        self.movie.setSpeed(100)
        gif_label.setMovie(self.movie)
        self.movie.start()

        congratulation = QLabel("Thank you so much！", self.gif_dialog)
        congratulation.setFont(QFont('UD デジタル 教科書体 NK-R', 15, QFont.Bold))
        congratulation.setStyleSheet("color: darkred; background-color: rgba(0, 0, 0, 0);")  # Transparent background
        congratulation.setAlignment(Qt.AlignCenter)

        report_message = QLabel(f" Your points are {self.total_score} ", self.gif_dialog)
        report_message.setFont(QFont('UD デジタル 教科書体 NK-R', 15))
        report_message.setAlignment(Qt.AlignCenter)

        layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        layout.addWidget(congratulation, alignment=Qt.AlignCenter)
        layout.addWidget(report_message, alignment=Qt.AlignCenter)

        self.gif_dialog.setLayout(layout)
        self.gif_dialog.show()


    def report_score(self):
        print(f"Beginning of report_score, username: {self.username}")
        if self.total_score >= 3:
            self.show_cherry_blossom()
        self.update_score_in_database()

    def update_score_in_database(self):
        print(f"Beginning of update_score_in_database, username: {self.username}")

        API_ENDPOINT = "https://bitech.loca.lt/update_score"
        API_ENDPOINT = "http://192.168.83.6:5022/update_score"
        data = {
            "username": self.username,
            "score": self.total_score
        }

        try:
            response = requests.post(API_ENDPOINT, json=data)
            response.raise_for_status()

            # Assuming your API returns a JSON response with a "status" key
            result = response.json()
            if result.get("status") == "success":
                print(f"Score updated successfully for username: {self.username}")
            else:
                print(f"Failed to update score for username: {self.username}. Message: {result.get('message')}")

        except requests.RequestException:
            print("There was an error connecting to the API.")

    def display_rankings(self):
        # Set font for the rankings text
        font = QFont("UD デジタル 教科書体 N-B", 20)  # Increase font size to 20
        QApplication.instance().setFont(font)

        # Create a custom QDialog for displaying the rankings
        rankings_dialog = QDialog(self)
        rankings_dialog.setWindowTitle("Points Ranking!")
        rankings_dialog.setFixedSize(600, 800)  # Increase the dialog size
        layout = QVBoxLayout()

        # Add the centered image at the top
        logo_label = QLabel()
        pixmap = QPixmap('Fig/ranking.png')
        logo_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
        logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo_label)

        rankings_text = QTextEdit()
        rankings_text.setReadOnly(True)
        layout.addWidget(rankings_text)

        API_ENDPOINT = "https://bitech.loca.lt/get_rankings"
        API_ENDPOINT = "http://192.168.83.6:5022/get_rankings"
        try:
            response = requests.get(API_ENDPOINT)
            response.raise_for_status()

            rankings = response.json()

            rankings_message = "Ranking:\n"
            for rank in rankings:
                rankings_message += f"User: {rank['username']}, Score: {rank['score']}\n"

            rankings_text.setText(rankings_message)

        except requests.RequestException as e:
            print(f"API error: {e}")

        rankings_dialog.setLayout(layout)
        rankings_dialog.exec_()


class MainProgram(QWidget):
    new_mqtt_message = pyqtSignal(dict)
    def __init__(self):
        super().__init__()
        self.current_topic = None
        self.mqtt_client=None
        self.timer = QTimer(self)
        self.font = QtGui.QFont('UD デジタル 教科書体 NK-R', 15)  # you can adjust the size as needed
        self.setFont(self.font)

        # Define the input features and target variable
        self.input_features = ['Ta', 'Tg', 'P', 'RH', 'MRT', 'Vair', 'PMV', 'Set-Point', 'Tout']
        self.target_variable = 'W(Outdoor)'

        # Load the dataset
        df = pd.read_csv('ML/ML.csv')

        # Splitting the data into training and testing sets
        X_train, _, y_train, _ = train_test_split(
            df[self.input_features], df[self.target_variable], test_size=0.2, random_state=42
        )

        # Scaling the features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)

        # Initializing and training the Random Forest model with best parameters
        self.rf_model = RandomForestRegressor(
            n_estimators=200, max_depth=15, max_features='sqrt', min_samples_leaf=1, min_samples_split=2,
            random_state=42
        )
        self.rf_model.fit(X_train_scaled, y_train)

        self.info_modules = {}
        self.username = None
        self.mqtt_thread = None
        position = None
        self.vote_dialog = VoteDialog(self,position)  # Use VoteDialog instead of VoteWidget
        self.new_mqtt_message.connect(self.update_info)
        self.initUI()

        # Show login dialog on startup
        self.show_login_dialog()

        #
        # # Create vote button and checkbox
        # self.vote_button = QPushButton("快適度に投票しましょう")
        # self.vote_button.setFont(QFont("UD デジタル 教科書体 N-B", 15))
        # self.vote_button.clicked.connect(self.show_vote_dialog)
        # self.vote_checkbox = QCheckBox("1時間ごとに投票ダイアログを表示する")
        # self.vote_checkbox.stateChanged.connect(self.toggle_vote_dialog)

        # 创建一个水平布局以保持复选框和图像标签
        grid = QGridLayout()

        # 将 setting_button 加入到第0行、第0列
        self.setting_button = QPushButton()
        self.setting_button.setIcon(QIcon("Fig/background_3.png"))
        self.setting_button.setIconSize(QSize(25, 25))
        self.setting_button.clicked.connect(self.show_label_selector)
        grid.addWidget(self.setting_button, 0, 0)

        # 将 time 标签加入到第0行、第1列
        self.time = QtWidgets.QLabel("Time")
        self.time.setFont(QtGui.QFont('Arial', 15))
        self.time.setAlignment(Qt.AlignCenter)
        grid.addWidget(self.time, 0, 1)

        # 将 image_label 加入到第0行、第2列
        image_label = QLabel()
        pixmap3 = QPixmap("Fig/background_4.png")
        image_label.setPixmap(pixmap3.scaled(280, 280, Qt.KeepAspectRatio))
        grid.addWidget(image_label, 0, 2)

        # 将网格布局添加到主布局中
        self.layout.addLayout(grid)


        # Start a timer to update the time every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.vote_timer = QTimer()
        self.vote_timer.timeout.connect(self.show_vote_dialog)

        self.screen_reminder = ScreenReminder()
        self.screen_reminder.userAwaySignal.connect(self.handleUserAway)
        self.screen_reminder.reminderSignal.connect(self.handleReminderSignal)
        self.show()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setStyleSheet("""
            QLabel {{
                font-family: Arial;
                font-size: 16px;
                border-radius: 10px;
                color:white;
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f754f7, stop:1 #000000);
                padding: 10px;
            }}
        """)
        # Title and time
        self.title = QtWidgets.QLabel("       BI-Tech<br>          Behavioral Insight X Technology")
        self.title.setFont(QtGui.QFont('STHupo', 26))
        self.title.setAlignment(QtCore.Qt.AlignCenter)  # Center align the text
        self.title.setStyleSheet("color:#F9AA33;")

          # Center align the text

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.title)
        # layout.addWidget(self.time)

        # BI-Tech logos
        # self.logo1 = QLabel()
        # pixmap2 = QPixmap('Fig/background_1.png')  # Use your second image file
        # self.logo1.setPixmap(pixmap2.scaled(100, 100, QtCore.Qt.KeepAspectRatio))
        #
        # self.logo2 = QLabel()
        # pixmap2 = QPixmap('Fig/background_2.png')  # Use your second image file
        # self.logo2.setPixmap(pixmap2.scaled(100, 100, QtCore.Qt.KeepAspectRatio))
        #
        # # Header layout (title and logos)
        self.header_layout = QHBoxLayout()
        # self.header_layout.addWidget(self.logo1)
        self.header_layout.addWidget(self.title)
        # self.header_layout.addStretch(1)  # Add stretchable space
        # self.header_layout.addWidget(self.logo2)
        #
        # # Add header layout to main layout
        self.layout.addLayout(self.header_layout)

        # self.layout.addWidget(self.time)

        # Layout for the InfoModules
        self.info_layout = QGridLayout()  # Change QHBoxLayout to QGridLayout

        # Add InfoModules to the grid layout
        # Use lighter gradient colors in MainProgram
        # gradient_colors = [
        #     ("#e1bee7", "#ffffff"), ("#d1c4e9", "#f3e5f5"), ("#c5cae9", "#e8eaf6"),
        #     ("#bbdefb", "#e3f2fd"), ("#b2ebf2", "#e0f7fa"), ("#b2dfdb", "#e0f2f1"),
        #     ("#c8e6c9", "#f1f8e9"), ("#f0f4c3", "#fff9c4"), ("#ffe0b2", "#fff3e0"),
        #     ("#ffe0b2", "#fff3e0"),  # Add another color for Set_Point
        #     ("#f8bbd0", "#f48fb1"), ("#a7ffeb", "#d0f8ce"),  # Turquoise shades
        #     ("#f4ff81", "#ffff8d"),  # Bright yellow shades
        #     ("#ff9e80", "#ff6e40"),  # Salmon shades
        #     ("#8d6e63", "#a1887f")
        # ]
        #
        # # Define the font to be used
        # font = QtGui.QFont('UD デジタル 教科書体 NK-R', 15)
        gradient_colors = [
            ("#778899", "#778899"), ("#778899", "#778899"), ("#778899", "#778899"),
            ("#778899", "#778899"), ("#778899", "#778899"), ("#778899", "#778899"),
            ("#778899", "#778899"),   # Add another color for Set_Point
            ("#008b8b", "#008b8b"), ("#008b8b", "#008b8b"),  # Turquoise shades
            ("#008b8b", "#008b8b"),  # Bright yellow shades
            ("#1e90ff", "#1e90ff"),  # Salmon shades
            ("#1e90ff", "#1e90ff")
        ]

        # Define the font to be used
        font = QtGui.QFont('UD デジタル 教科書体 NK-R', 15)

        for i, (label_name, (gradient_start, gradient_end)) in enumerate(
                zip(['Indoor Air Temperature', 'Globe Temperature', 'Air Pressure', 'Relative Humidity', 'Mean Radiant Temperature', 'Wind Speed', 'PMV', 'CO2', 'PM2.5', 'PM10'
                     ,'AC set temperature', 'Energy Consumption Prediction'],
                    gradient_colors)):
            # Create InfoModule and set font
            self.info_modules[label_name] = InfoModule(self, label_name, gradient_start, gradient_end)

            self.info_modules[label_name].setFont(font)

            row, col = divmod(i, 2)
            self.info_layout.addWidget(self.info_modules[label_name], row, col)

        self.layout.addLayout(self.info_layout)
        # Create and configure energy-saving label
        # self.energy_saving_label = GlowingLabel('節エネのために、設定温度を1度上げていただけますか？')
        self.energy_saving_label = GlowingLabel('Up AC Temperature 1 C decreasing 8.25g CO2 emission!')
        self.energy_saving_label.setFont(QtGui.QFont('UD デジタル 教科書体 NK-R', 20))
        self.energy_saving_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.energy_saving_label)

        # # Set gradient background
        # gradient_start, gradient_end = gradient_colors[-1]
        # energy_saving_label.setStyleSheet(
        #     f"background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 {gradient_start}, stop: 1 {gradient_end});"
        # )

        # Add the energy-saving label to your desired layout or widget.
        # For example, if you want to add it to the `info_layout` grid:
        # self.info_layout.addWidget(energy_saving_label, row + 1, 0, 1, 2)  # spans both columns
        #
        # # Optional: Set a fixed height
        # energy_saving_label.setFixedHeight(40)

        # self.pmv_explanation_label1 = QLabel("PMV is a measure of thermal comfort.")
        self.pmv_explanation_label2 = QLabel("PMV Explanation")
        # self.pmv_explanation_label1.setAlignment(Qt.AlignCenter)
        # self.pmv_explanation_label1.setFont(QtGui.QFont('Comic Sans MS', 10))
        self.pmv_explanation_label2.setAlignment(Qt.AlignCenter)
        self.pmv_explanation_label2.setFont(QtGui.QFont('Comic Sans MS', 15))
        # self.layout.addWidget(self.pmv_explanation_label1)
        self.layout.addWidget(self.pmv_explanation_label2)

        # self.Screen_Using_Reminder_label = QLabel('Screen Using Reminder')
        # self.layout.addWidget(self.Screen_Using_Reminder_label)
        # self.Screen_Using_Reminder_label .setText

        self.setLayout(self.layout)

        self.bottom_layout = QHBoxLayout()

        # Create the vote button
        #self.vote_button = QPushButton("快適度に投票しましょう")
        self.vote_button = QPushButton("Thermal Comfort Voting")
        self.vote_button.setFont(QFont("UD デジタル 教科書体 N-B", 15))
        # self.vote_butto.setStyleSheet("color:#F9AA33;")
        self.vote_button.clicked.connect(self.show_vote_dialog)

        # ログアウトボタンを作成する
        # self.logout_button = QPushButton("⾏動申告")
        self.logout_button = QPushButton("Reporing Energy-saving Activity")
        self.logout_button.setFont(QFont("UD デジタル 教科書体 N-B", 15))
        # self.vote_button.setStyleSheet("color:#F9AA33;")
        self.logout_button.clicked.connect(self.report)

        # Add vote button and logout button to the bottom layout
        self.bottom_layout.addWidget(self.vote_button)
        self.bottom_layout.addWidget(self.logout_button)

        # Add bottom layout to the main layout
        self.layout.addLayout(self.bottom_layout)

    def store_checkbox_dict(self, checkbox_dict):
        self.checkbox_dict = checkbox_dict

    def show_trend_chart(self, label_name):
        trend_dialog = TrendDialog(label_name)
        trend_dialog.exec_()

    def rearrange_info_modules(self):
        # 清除当前的布局内容
        for i in reversed(range(self.info_layout.count())):
            widget = self.info_layout.itemAt(i).widget()
            if widget is not None:
                self.info_layout.removeWidget(widget)
                widget.hide()  # 隐藏此控件

        # 获取所有选中的InfoModule，并添加到一个列表中
        selected_modules = [module for label_name, module in self.info_modules.items() if
                            self.checkbox_dict[label_name].isChecked()]

        # 按照网格布局重新排列选中的InfoModule
        row, col = 0, 0
        for module in selected_modules:
            self.info_layout.addWidget(module, row, col)
            module.show()  # 显示此控件
            col += 1
            if col > 1:
                col = 0
                row += 1

    def show_vote_dialog(self):
        self.vote_dialog.show()

    def toggle_vote_dialog(self, state):
        if state == Qt.Checked:
            # Start the timer to show the VoteDialog every hour
            self.vote_timer.start(3600000)
        else:
            # Stop the timer
            self.vote_timer.stop()

    def update_time(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time.setText(current_time)
        self.time.setStyleSheet("color: white;")

    def set_current_topic(self, topic):
        self.current_topic = topic

    def mqttmain_loop(self, topic):  # Accept `topic` as a parameter
        broker_address = "broker.emqx.io"
        broker_address = "broker.hivemq.com"
        client = 'chenyutong'
        user = 'emqx'
        password = 'public'
        port = 1883
        # client = mqtt.Client()
        self.mqtt_client = client
        def on_message(client, userdata, message):
            payload_str = message.payload.decode('utf-8')
            data = json.loads(payload_str)

            if isinstance(data, list):
                data_dict = {
                    'timestamp': data[0],
                    'Ta': data[1],
                    'Tg': data[2],
                    'Pressure': data[3],
                    'Humidity': data[4],
                    'MRT': data[5],
                    'Windspeed': data[6],
                    'PMV': data[7],
                    'CO2': data[8],
                    'PM2.5':data[9],
                    'PM10': data[10]
                }
            elif isinstance(data, dict):
                data_dict = data  # If the data is a dictionary, use it directly

            print("Received message: ", message.topic, message.payload.decode("utf-8"))
            self.new_mqtt_message.emit(data_dict)

        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_message = on_message
        self.mqtt_client.connect(broker_address, port=port)
        self.mqtt_client.subscribe(topic)
        self.mqtt_client.loop_forever()

    def mqttmain(self, topic=None):
        if topic is None:
            topic = self.current_topic  # Use the current topic if no topic is provided

        if hasattr(self, 'mqtt_client') and self.mqtt_client:  # Check if mqtt_client is initialized
            self.mqtt_client.unsubscribe(self.current_topic)

        if self.mqtt_thread is not None and self.mqtt_thread.is_alive():
            self.mqtt_thread.stop()

        self.mqtt_thread = StoppableThread(target=self.mqttmain_loop, args=(topic,))
        self.mqtt_thread.start()

    def update_info(self, data):
        if 'Ta' in data:
            self.info_modules['Indoor Air Temperature'].update_value('{:.1f}'.format(float(data['Ta'])) + "°C")
            self.info_modules['Indoor Air Temperature'].setFont(self.font)

        if 'Tg' in data:
            self.info_modules['Globe Temperature'].update_value('{0:.1f}'.format(int(float(data['Tg']))) + "°C")
            self.info_modules['Globe Temperature'].setFont(self.font)

        if 'Pressure' in data:
            self.info_modules['Air Pressure'].update_value(str(data['Pressure']) + "kpa")
            self.info_modules['Air Pressure'].setFont(self.font)

        if 'Humidity' in data:
            self.info_modules['Relative Humidity'].update_value(str(data['Humidity']) + "%")
            self.info_modules['Relative Humidity'].setFont(self.font)
        if 'MRT' in data:
            self.info_modules['Mean Radiant Temperature'].update_value(str(data['MRT']) + "°C")
            self.info_modules['Mean Radiant Temperature'].setFont(self.font)
        if 'Windspeed' in data:
            self.info_modules['Wind Speed'].update_value('{0:.2f}'.format(float(data['Windspeed'])) + "m/s")
            self.info_modules['Wind Speed'].setFont(self.font)
        # if 'PMV' in data:
        #     self.info_modules['PMV'].update_value('{:.2f}'.format(float(data['PMV'])))
        #     self.info_modules['PMV'].setFont(self.font)
        #     pmv_value = float(data['PMV'])
        #     self.pmv_explanation_label2.setFont(self.font)
        #     if -3 <= pmv_value <= -2:
        #         self.pmv_explanation_label2.setText("PMV: -3~-2 - 非常に寒い: 体感温度が非常に低く、厚手の服が必要です。")
        #     elif -2 <= pmv_value < -1:
        #         self.pmv_explanation_label2.setText("PMV: -2~-1 - 寒い: 寒さを感じ、セーターやジャケットが必要です。")
        #     elif -1 <= pmv_value < 0:
        #         self.pmv_explanation_label2.setText("PMV: -1~0 - やや寒い: 少し寒さを感じるかもしれません。軽いカーディガンが役立ちます。")
        #     elif 0 <= pmv_value < 1:
        #         self.pmv_explanation_label2.setText("PMV: 0~1 - どちらでもない: 体感温度は快適で、特に追加の服装は必要ありません。")
        #     elif 1 <= pmv_value < 2:
        #         self.pmv_explanation_label2.setText("PMV: 1~2 - やや暑い: 少し暑く感じるかもしれません。涼しい場所や風を求めるかもしれません。")
        #     elif 2 <= pmv_value < 3:
        #         self.pmv_explanation_label2.setText("PMV: 2~3 - 暑い: 熱さを感じ、扇風機やエアコンが必要です。")
        #     elif pmv_value >= 3:
        #         self.pmv_explanation_label2.setText("PMV:　3以上 - 非常に暑い: 体感温度が非常に高く、冷房や涼しい飲み物が必要です。")
        #     else:
        #         self.pmv_explanation_label2.setText("中立: 快適な気分であるはずです。")
        if 'PMV' in data:
            self.info_modules['PMV'].update_value('{:.2f}'.format(float(data['PMV'])))
            self.info_modules['PMV'].setFont(self.font)
            pmv_value = float(data['PMV'])
            self.pmv_explanation_label2.setFont(self.font)
            self.pmv_explanation_label2.setStyleSheet("color: #F9AA33; font-weight: bold;")  # Set the font color to #F9AA33

            if -3 <= pmv_value <= -2:
                self.pmv_explanation_label2.setText(
                    "PMV: -3~-2 - Very Cold: The perceived temperature is very low, requiring heavy clothing.")
            elif -2 <= pmv_value < -1:
                self.pmv_explanation_label2.setText("PMV: -2~-1 - Cold: Feels cold, necessitating a sweater or jacket.")
            elif -1 <= pmv_value < 0:
                self.pmv_explanation_label2.setText(
                    "PMV: -1~0 - Slightly Cold: Might feel a bit chilly, a light cardigan could help.")
            elif 0 <= pmv_value < 1:
                self.pmv_explanation_label2.setText(
                    "PMV: 0~1 - Neutral: Comfortable temperature, no additional clothing needed.")
            elif 1 <= pmv_value < 2:
                self.pmv_explanation_label2.setText(
                    "PMV: 1~2 - Slightly Warm: Might feel a bit warm, might seek a cooler place or breeze.")
            elif 2 <= pmv_value < 3:
                self.pmv_explanation_label2.setText("PMV: 2~3 - Hot: Feels hot, fan or air conditioning needed.")
            elif pmv_value >= 3:
                self.pmv_explanation_label2.setText(
                    "PMV: 3 or more - Very Hot: The perceived temperature is very high, requiring air conditioning or cool drinks.")
            else:
                self.pmv_explanation_label2.setText("Neutral: Should feel comfortable.")

        # if 'CO2' in data:
        #     co2_level = int(str(data['CO2'])) # 获取 CO2 的标签
        #     if co2_level < 600:
        #         self.info_modules['CO2'].update_value(str(data['CO2']) + "ppm" + '  すばらしい空気の質')
        #
        #     elif co2_level < 1000:
        #         self.info_modules['CO2'].update_value(str(data['CO2']) + "ppm" + '  良い空気の質')
        #
        #     elif co2_level < 2500:
        #         self.info_modules['CO2'].update_value(str(data['CO2']) + "ppm" + '  換気を検討してください')
        #
        #     else:
        #         self.info_modules['CO2'].update_value(str(data['CO2']) + "ppm" + '  換気が必要')
        if 'CO2' in data:
            co2_level = int(str(data['CO2']))  # Get CO2 level
            if co2_level < 600:
                self.info_modules['CO2'].update_value(str(data['CO2']) + "ppm - Excellent Air Quality")

            elif co2_level < 1000:
                self.info_modules['CO2'].update_value(str(data['CO2']) + "ppm - Good Air Quality")

            elif co2_level < 2500:
                self.info_modules['CO2'].update_value(str(data['CO2']) + "ppm - Consider Ventilating")

            else:
                self.info_modules['CO2'].update_value(str(data['CO2']) + "ppm - Ventilation Needed ")

        if 'PM2.5' in data:
            self.info_modules['PM2.5'].update_value(str(data['PM2.5']) + "μg/m³")
            self.info_modules['PM2.5'].setFont(self.font)

        if 'PM10' in data:
            self.info_modules['PM10'].update_value(str(data['PM10']) + "μg/m³")
            self.info_modules['PM10'].setFont(self.font)

        #Outdoor Temperature
        api_url = "https://api.open-meteo.com/v1/jma?latitude=33.60&longitude=130.42&hourly=temperature_2m,relativehumidity_2m,dewpoint_2m,weathercode,windspeed_10m&timezone=Asia%2FTokyo"
        # Request to the API and get the response
        response = requests.get(api_url)
        if response.status_code == 200:
            weather_data = response.json()
        else:
            print("APIリクエストが失敗しました。ステータスコード:", response.status_code)
            return  # Exit if the request failed

        # Prediction part
        Tout = weather_data['hourly']['temperature_2m'][0]

        # Check if all required features are present in data
        required_features = ['Ta', 'Tg', 'Pressure', 'Humidity', 'MRT', 'Windspeed', 'PMV']
        if all(feature in data for feature in required_features):
            features_for_prediction = [float(data[feature]) for feature in required_features]
            features_for_prediction.append(Tout)  # Add Tout to the features

            set_point_values = [25]
            self.info_modules['AC set temperature'].update_value("/".join(map(str, set_point_values)) + "°C")

            predictions = []
            for set_point_value in set_point_values:
                input_data = np.array([features_for_prediction + [set_point_value]])  # Add Set-Point to the features
                scaled_input = self.scaler.transform(input_data)
                predicted_consumption = self.rf_model.predict(scaled_input)[0]
                predictions.append(f"{predicted_consumption:.2f} ")
            self.info_modules['Energy Consumption Prediction'].update_value(" / ".join(predictions) +"kWh/min"
                                                            )

    def show_login_dialog(self):
        self.login_dialog = LoginDialog(main_program=self)  # Ensure you pass the main_program reference
        if self.login_dialog.exec_() == QDialog.Accepted:
            position = self.login_dialog.system_position_combobox.currentText()[-1]
            topic = f"raspberry/mqtt{position}" if position != '1' else "raspberry/mqtt"

            if self.mqtt_thread is not None and self.mqtt_thread.is_alive():
                self.mqtt_thread.stop()
            self.mqtt_thread = StoppableThread(target=self.mqttmain, args=(topic,))
            self.mqtt_thread.start()

            self.show_label_selector()
            self.rearrange_info_modules()

    def show_signin_dialog(self):
        self.login_dialog = signinDialog()
        pass

    def handleUserAway(self, message):
        # Handle the userAwaySignal
        self.last_away_message = message
        # 在此处处理 message，例如显示一个QMessageBox
        # 创建消息框
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Notification")
        msg_box.setText(message)

        # 设置消息框的字体
        font = QtGui.QFont('UD デジタル 教科書体 NK-R', 15)
        msg_box.setFont(font)

        # 显示消息框
        # msg_box.exec_()

        notification.notify(
            title="Message from BI-Tech",
            message=self.last_away_message,
            app_icon="Fig/B.ico",
            timeout=5
        )

    def handleReminderSignal(self, message):
        # Handle the reminderSignal
        self.last_away_message = message
        QMessageBox.warning(self, "Reminder", message)
        # self.screen_reminder
        notification.notify(
            title="Message from BI-Tech",
            message=self.last_away_message,
            app_icon="Fig/B.ico",
            timeout=5
        )

    def show_label_selector(self):
        self.label_selector = LabelSelectorDialog(self, self.username)
        self.label_selector.exec_()  # 这会显示标签选择器并等待用户关闭它

    def toggle_vote_dialog(self, state):
        if state == Qt.Checked:
            self.vote_timer.start(3600000)
        else:
            self.vote_timer.stop()

    def logout(self):
        # Hide the main program
        self.hide()

        # Show the login dialog
        self.show_login_dialog()

        # Show the main program again when login is successful
        self.show()

    def report(self):
        self.hide()
        self.report_dialog = behavior_report(username=self.username)  # Pass the username when creating the instance
        self.report_dialog.exec_()
        self.show()



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.main_program = MainProgram()
        self.setCentralWidget(self.main_program)

        self.setWindowIcon(QIcon('Fig/B.ico'))

        # Set the background color of the window
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #344955, stop:1 #4A6572);
            }
        """)

class StoppableThread(threading.Thread):
    def __init__(self, target=None, args=()):
        super().__init__(target=target, args=args)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    QCoreApplication.setApplicationName('Behavioral Insight X Tech')
    main_program = MainWindow()  # Change this to MainWindow
    main_program.show()
    sys.exit(app.exec_())







