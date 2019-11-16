import socket
import os
import shutil
import random
import threading
import json
import re
import logging

stata = 'stata.json'


def get_size(way):
	total_size = 0
	for dirpath, dirnames, filenames in os.walk(way):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			total_size += os.path.getsize(fp)
	return total_size


def response(req, conn, lst, login, main_way, way_, data):
	if req == 'pwd':
		conn.send(os.path.join('server', main_way[len(os.path.split(way_)[0]):]).encode())
	elif req == 'ls':
		if main_way != os.path.split(way_)[0]:
			msg = '; '.join(os.listdir(main_way))
			if msg:
				conn.send(msg.encode())
			else:
				conn.send('Папка пуста'.encode())
		else:
			msg = '; '.join([i for i in os.listdir(main_way) if i != 'stata.json'  and i != 'server.py' and 'client.py' and i != 'sample.log'])
			if msg:
				conn.send(msg.encode())
			else:
				conn.send('Папка пуста'.encode())
	elif len(req.split(' ')) != 1 and req.split(' ')[0] == 'touch' and req.split(' ')[1] != '':
		if main_way != os.path.split(way_)[0]: 
			logging.info(login + ' создал файл ' + req.split(' ')[1])
			file_name = ' '.join(req.split(' ')[1:])
			open(os.path.join(main_way, file_name),  'w').close()
		else:
			conn.send('Нельзя создавать файлы'.encode())
	elif len(req.split(' ')) != 1 and req.split(' ')[0] == 'cat' and req.split(' ')[1] != '':
		file_name = ' '.join(req.split(' ')[1:])
		if os.path.isfile(os.path.join(main_way, file_name)):
			data = open(os.path.join(main_way, file_name), 'r')
			for i in data:
				conn.send(i.encode())
			data.close()
		else:
			conn.send('Такого файла нет'.encode())
	elif len(req.split(' ')) != 1 and req.split(' ')[0] == 'mkdir' and req.split(' ')[1] != '':
		way = main_way
		dirname = ' '.join(req.split(' ')[1:])
		succ = '''Папка "''' + dirname + '''" создана.'''
		if main_way != os.path.split(way_)[0]:
			try:
				os.mkdir(os.path.join(way, dirname))
				conn.send(succ.encode())
				logging.info(login + ' создал папку ' + dirname)
			except OSError:
				conn.send('Такая папка уже есть'.encode())
		else:
			conn.send('Нельзя создавать папки'.encode())
	elif len(req.split(' '))>=2 and req.split(' ')[0] == 'rm' and req.split(' ')[1] == '-R':
		req += ' '
		p = re.compile(r'rm[ ]-R[ ].+\s+$')
		dirname = ' '.join(req.split(' ')[2:][:-1])
		if p.match(req):
			if main_way != os.path.split(way_)[0]:
				try:
					shutil.rmtree(os.path.join(main_way ,dirname))
					logging.info(login + ' удалил папку ' + dirname)
				except:
					conn.send('Такой папки нет'.encode())
			else:
				conn.send('Вы не можете удалять папки на сервере'.encode())
		else:
			conn.send('Неправильный ввод'.encode())
	elif len(req.split(' ')) != 1 and req.split(' ')[0] == 'rm' and req.split(' ')[1] != '':
		file_name = os.path.join(main_way, ' '.join(req.split(' ')[1:]))
		if main_way != os.path.split(way_)[0]:
			if os.path.isfile(file_name):
				os.remove(file_name)
				logging.info(login + ' удалил файл ' + os.path.split(file_name)[1])
			else:
				conn.send('Такого файла нет'.encode())
		else:
			conn.send('Вы не можете удалять файлы на сервере'.encode())
	elif req.split(' ')[0] == 'mv':
		req += ' '
		result = re.split(r'"', req)
		p = re.compile(r'mv[ ]".+"[ ]".+"\s+$')
		if p.match(req):
			result = [result[i] for i in range(len(result)) if i%2 == 1]
			name = result[0]
			name_s = result[1]
			if os.path.isfile(os.path.join(main_way, name)):
				os.rename(os.path.join(main_way,name), os.path.join(main_way, name_s))
			else:
				conn.send('Такого файла нет'.encode())
		else:
			conn.send('Неправильный ввод'.encode())
	elif len(req.split(' ')) != 1 and req.split(' ')[0] == 'cp' and req.split(' ')[1] != '':
		file_name = ' '.join(req.split(' ')[1:])
		if main_way != os.path.split(way_)[0]:
			if os.path.isfile(os.path.join(main_way, file_name)):
				conn.send('Копирование файла клиенту '.encode())
				ready = conn.recv(1024).decode()
				if ready == 'готов к записи':
					conn.send(file_name.encode())
					data_str = ''
					data = open(os.path.join(main_way, file_name), 'r')
					for i in data:
						data_str += i
					data.close()
					if data_str != '':
						conn.send(data_str.encode())
					else:
						conn.send('file is clear'.encode())
			else:
				conn.send('Такого файла нет'.encode())
		else:
			conn.send('Нельзя копировать папки пользователей'.encode())
	elif req.split(' ')[0] == 'echo':
		req += ' '
		p = re.compile(r'echo[ ]".+"[ ]>>[ ]".+"\s+$')
		if p.match(req):
			result = re.split(r'"', req)
			result = [result[i] for i in range(len(result)) if i%2 == 1]
			if os.path.isfile(os.path.join(main_way, result[1])):
				space_max = data[os.path.split(way_)[1]][1]
				for i in result[0]:
					data = open(os.path.join(main_way, result[1]), 'a')
					space = get_size(way_)
					if space < space_max:
						data.write(i)
						data.close()
					else:
						data.close()
						conn.send('Не хватает места для полной записи'.encode())
						break
			else:
				conn.send('Такого файла нет'.encode())
		else:
			conn.send('Неправильный ввод'.encode())
	elif len(req.split(' ')) == 3 and req.split(' ')[0] == 'space' and (req.split(' ')[1] in data) and req.split(' ')[2] != '': 
		try:
			if login == '__admin__':
				if int(req.split(' ')[2]) >= 0:
					if int(req.split(' ')[2]) >= get_size(os.path.join(os.path.split(way_)[0], req.split(' ')[1])):
						data[req.split(' ')[1]][1] = int(req.split(' ')[2])
						with open('stata.json', 'w') as f:
							json.dump(data,f)
					else:
						conn.send('Размер папки превышает значение'.encode())
				else:
					conn.send('не может быть меньше 0'.encode())
			else:
				conn.send('Permission denied'.encode())
		except ValueError:
			conn.send('Wrong size'.encode())
	elif len(req.split(' ')) != 1 and req.split(' ')[0] == 'down' and req.split(' ')[1] != '':
		space_max = data[os.path.split(way_)[1]][1] 
		if main_way != os.path.split(way_)[0]:
			conn.send('Можно загружать файлы'.encode())
			ready = conn.recv(1024).decode()
			if ready == 'готов загружать':
				conn.send(req.encode())
				dobro = conn.recv(1024).decode()
				if dobro == 'yest file in mai papka':
					conn.send('give me size'.encode())
					file_size = conn.recv(1024).decode()
					bad_msg = 'Не хватает '+ str(file_size) +' байт в папке. (Свободно ' +str(get_size(way_))+'/'+str(space_max)+' байт)'
					if int(file_size) < space_max - get_size(way_):
						conn.send('есть место'.encode())
					else:
						conn.send('нет места'.encode())
					otvet = conn.recv(1024).decode()
					if otvet == 'Данные':
						conn.send('give name'.encode())
						file_name = conn.recv(1024).decode()
						file_data = conn.recv(1024).decode()
						if file_data != 'file clear':
							data = open(os.path.join(main_way, file_name), 'w')
							data.write(file_data)
							data.close()
						else:
							data = open(os.path.join(main_way, file_name), 'w')
							data.close()
					else:
						conn.send(bad_msg.encode())
				else:
					conn.send(dobro.encode())
		else:
			conn.send('Нельзя копировать загружать файлы на папку сервера'.encode())
	elif req == 'Нельзя опуститься ниже вашей домашней директории':
		conn.send(req.encode())
	elif req == 'Админ, нельзя опуститься ниже':
		conn.send(req.encode())
	elif req == 'Такой папки нет':
		conn.send(req.encode())
	else:
		conn.send('Неверная команда'.encode())
		#msg = req			#на случай если захочется дать возможность чата
		#for i in lst:
		#	if i != conn: 
		#		i.send(msg.encode())


def reader(conn,lst, data, login):
	main_way = os.path.join(os.getcwd(), login)
	way_ = main_way
	predel = main_way
	while True:
		msg = conn.recv(1024).decode()
		if msg == 'exit':
			logging.info('Пользователь '+ login +' вышел')
			lst.remove(conn)
			print(len(lst))
			break
		elif len(msg.split(' ')) != 0 and msg.split(' ')[0] == 'cd' and msg.split(' ')[1] != '':
			dirname = ' '.join(msg.split(' ')[1:])
			if dirname != '..':
				if main_way != os.path.split(way_)[0]:
					if os.path.isdir(os.path.join(main_way, dirname)):
						main_way = os.path.join(main_way, dirname)
					else:
						response('Такой папки нет', conn, lst, login, main_way, way_, data)
				else:
					if msg.split(' ')[1] in data:
						way_ = os.path.join(os.path.split(way_)[0], dirname)
						main_way = os.path.join(os.path.split(way_)[0], dirname)
					else:
						response('Такой папки нет', conn, lst, login, main_way, way_, data)
			else:
				if login != '__admin__':
					if main_way != predel:
						main_way = os.path.split(main_way)[0]
					else:
						response('Нельзя опуститься ниже вашей домашней директории', conn, lst, login, main_way, way_,data)
				else:
					if main_way != os.path.split(predel)[0]:
						main_way = os.path.split(main_way)[0]
					else:
						response('Админ, нельзя опуститься ниже', conn, lst, login, main_way, way_, data)
		else:
			response(msg, conn, lst, login, main_way, way_, data)
	conn.close()


def avtoriz(conn,lst, data):
	login = conn.recv(1024).decode()
	if login in data:
		conn.send('Логин прошел'.encode())
		password = conn.recv(1024).decode()
		if password == data[login][0]:
			conn.send('Пароль прошел'.encode())
			logging.info("Пользователь " + login + " подключился")
			print('connection succes')
			reader(conn,lst, data, login)
		else:
			logging.info('Пользователь '+ login + ' не смог подключился')
			conn.send('Пароль не прошел'.encode())
			lst.remove(conn)
			print(len(lst))
	else:
		conn.send('Логин не прошел, добавить? '.encode())
		choice = conn.recv(1024).decode()
		if choice == 'add':
			password_cor = conn.recv(1024).decode()
			data.update({login:[password_cor, 15]})
			with open(stata, 'w') as f:
				json.dump(data, f)
			way = os.getcwd()
			os.mkdir(os.path.join(way, login))
			reader(conn, lst, data, login)
		else:
			logging.info('Неудачная попытка подсоединения')
			lst.remove(conn)
			print(len(lst))


def main(lst, data):
	conn, addr = sock.accept()
	lst.append(conn)
	threading.Thread(target=avtoriz, args =(conn,lst, data)).start()
	print(len(lst))
	main(lst, data)


sock = socket.socket()
try:
	port = 8081
	sock.bind(('', port))
except:
	port = random.randint(8000, 8300)
	sock.bind(('localhost', port))
sock.listen()
print('Прослушивавется порт:', port)

lst = []

try:
	with open(stata, 'r') as f:
		data = json.load(f)
except:
	with open(stata, 'w') as f:
		json.dump({'__admin__': ['123', 15]}, f)
	way = os.getcwd()
	os.mkdir(os.path.join(way, '__admin__'))
	with open(stata, 'r') as f:
		data = json.load(f)
		
logging.basicConfig(filename="sample.log", level=logging.INFO)
main(lst, data)
