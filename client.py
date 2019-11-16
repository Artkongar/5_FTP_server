import socket
import threading
import os

port = int(input('Port: '))
sock = socket.socket()
sock.connect(('localhost', port))


def get_size(way):
	total_size = 0
	for dirpath, dirnames, filenames in os.walk(way):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			total_
			size += os.path.getsize(fp)
	return total_size


def reader():
	while True:
		msg = sock.recv(1024).decode()
		if msg == 'Копирование файла клиенту ':
			sock.send('готов к записи'.encode())
			file_name = sock.recv(1024).decode()
			file_data = sock.recv(1024).decode()
			if file_data != 'file is clear':
				open(file_name, 'w').close()
				data = open(file_name, 'a') 
				data.write(file_data)
				data.close()
			else:
				open(file_name, 'w').close()
				data = open(file_name, 'a') 
				data.write('')
				data.close()
		elif msg == 'Можно загружать файлы':
			sock.send('готов загружать'.encode())
			req = sock.recv(1024).decode()
			try:
				data = open(os.path.join(os.getcwd(), ' '.join(req.split(' ')[1:])), 'r')
				sock.send('yest file in mai papka'.encode())
				file_size = os.path.getsize(os.path.join(os.getcwd(), ' '.join(req.split(' ')[1:])))
				size_msg = sock.recv(1024).decode()
				if size_msg == 'give me size':
					sock.send(str(file_size).encode()) #Отсылаю размер файла
					otvet = sock.recv(1024).decode()
					if otvet == 'есть место':
						sock.send('Данные'.encode())
						data_msg = sock.recv(1024).decode()
						if data_msg == 'give name':
							sock.send(' '.join(req.split(' ')[1:]).encode())
							data_str = ''
							for i in data:
								data_str += i
							if data_str != '':
								sock.send(data_str.encode())
							else:
								sock.send('file clear'.encode())
						else:
							sock.send('Нет данных'.encode())
					else:
						sock.send('Данные not'.encode())
			except FileNotFoundError:
				print('Такого файла нет')
		else:
			print(msg)


iswork = 0
login = input('Логин: ')
sock.send(login.encode())
login_cor = sock.recv(1024).decode()
if login_cor == 'Логин прошел':
	password = input('Пароль: ')
	sock.send(password.encode())
	password_cor = sock.recv(1024).decode()
	if password_cor == 'Пароль прошел':
		if login != '__admin__':
			print('Авторизация!')
		else:
			print('Привет, Админ')
		s1 = threading.Thread(target=reader)
		s1.setDaemon(True)
		s1.start()
		iswork = 1
	else:
		print(password_cor)
else:
	print(login_cor)
	choice = input()
	if choice == 'l':
		sock.send('add'.encode())
		password_cor = input('Введите новый пароль: ')
		sock.send(password_cor.encode())
		print('Авторизация!')
		s1 = threading.Thread(target=reader)
		s1.setDaemon(True)
		s1.start()
		iswork = 1

while iswork:
	msg = input()
	if msg == 'exit':
		sock.send(msg.encode())
		break
	else:
		sock.send(msg.encode())

sock.close()
