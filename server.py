import random
import socket
from tabnanny import check
import threading
import time

version = "2.0.7"
HOST = "127.0.0.1" #กำหนดค่า HOST ที่เชื่อมต่อ #127.0.0.1 Local Host
PORT = 63453 #กำหนดค่าพอร์ตในการสื่อสาร #ช่วงพอร์ต 49152-65535
ADDR = (HOST, PORT) #รวม HOST กับ PORT เข้าเป็น tuple เดียวกัน

conn_list = []
user_point = 0

def ranking():
	while True:
		rank_name = []
		rank_wpm = []

		file = open("ranking.txt", "r")

		# read file follow line
		lines = file.readlines()

		# loop for used for get word in lines to append to vocabulary_play
		for line in lines:

			# clear \n
			line = line.replace("\n", "")
			x = line.split(" ")
			if x[0] in rank_name:
				index_name = rank_name.index(x[0])
				check = rank_wpm[index_name]
				index_num =rank_wpm.index(check)
				if float(x[1]) > float(rank_wpm[int(index_num)]):
					rank_wpm.remove(rank_wpm[int(index_num)])
					rank_name.remove(x[0])
					rank_name.append(x[0])
					rank_wpm.append(float(x[1]))

			else:	
				rank_name.append(x[0])
				rank_wpm.append(float(x[1]))

		file.close()
		file = open("ranking.txt", "w")
		for i in range(len(rank_name)):
			file.write(f'{rank_name[i]} {rank_wpm[i]}\n')


		sort_rank_wpm = rank_wpm.copy()
		sort_rank_wpm.sort()
		index_name_1 = rank_wpm.index(sort_rank_wpm[-1])
		index_name_2 = rank_wpm.index(sort_rank_wpm[-2])
		index_name_3 = rank_wpm.index(sort_rank_wpm[-3])
		file = open("top_3.txt", "w")
		file.write(f'{rank_name[index_name_1]} {sort_rank_wpm[-1]}\n')
		file.write(f'{rank_name[index_name_2]} {sort_rank_wpm[-2]}\n')
		file.write(f'{rank_name[index_name_3]} {sort_rank_wpm[-3]}\n')
		file.close()

		print(f'\nTOP 3')
		print(f'{rank_name[index_name_1]} {sort_rank_wpm[-1]}')
		print(f'{rank_name[index_name_2]} {sort_rank_wpm[-2]}')
		print(f'{rank_name[index_name_3]} {sort_rank_wpm[-3]}')
		time.sleep(10)

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def game():
	global user_point
	POINT = user_point
	conn = conn_list[POINT]

	# define vocab_forPlay used for read word in file for play
	def vocab_forPlay():

		# open file to use for play
		file = open("word.txt", "r")

		# read file follow line
		lines = file.readlines()

		# loop for used for get word in lines to append to vocabulary_play
		for line in lines:

			# clear \n
			line = line.replace("\n", "")

			# append word to vocabulary_play
			vocabulary_play.append(line)
	
	def getWord():
		# value i will random number between 0 to len of vocabulary_play
		i = random.randint(0, len(vocabulary_play)-1) 
		
		# data will use value i to select word in vocabulary_play
		data = vocabulary_play[i]

		return data

	count_turn = 0

	# vocabulary_play used for vocab_forplay
	vocabulary_play = []

	# vocab play used for read word in file and append to vocabulary_play
	vocab_forPlay()

	# loop while used for send word and check word
	while True:

		# count_vocab used for receive data from client
		message_from_client = conn.recv(1024).decode()
		if "Ranking" in message_from_client :
			message_from_client = conn.recv(1024).decode()
			file = open("ranking.txt", "a")
			file.write(f'{message_from_client}')
			file.close()
		
		else:
			# loop while used for check count_vocab and count_turn
			while True:

				if int(message_from_client) == 0:
					# count_turn used for check
					count_turn = -1

					data = getWord()

					# data_send will encode himself for send data to client
					data_send = data.encode()

					# send data_send to client for play game
					conn.sendall(data_send)

					#remove word in vocabulary_play
					vocabulary_play.remove(data)

					#count_turn + 1
					count_turn += 1


					# break loop while
					break

				# if count_vocab != count_turn
				elif int(message_from_client) != count_turn:

					data = getWord()
							
					# data_send will encode yourself for send data to client
					data_send = data.encode()

					# send data_send to client for play game
					conn.sendall(data_send)

					#remove word in vocabulary_play
					vocabulary_play.remove(data)

					#count_turn + 1
					count_turn += 1

					# break loop while
					break

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def server():
	# Server
	# AF_INET Address Family ประเภทของ Socket
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server: #สร้าง object ในการเชื่อมต่อ socket
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.bind(ADDR) #เชื่อมต่อ
		server.listen(2) #2 เป็นจำนวนสูงสุดของการเชื่อมต่อคิวที่เราจะอนุญาต

		global user_point

		while True:
			conn, addr = server.accept() #รับข้อมูลการเชื่อมต่อขาเข้า
			conn_list.append(conn)
			print(f'\n[STARTING] SERVER')
			print(f'[LISTENING] Server is listening on IP->{HOST} PORT->{PORT}')
			print(f'[Start] User {user_point+1} {addr}')
			thread = threading.Thread(target=game, args=())
			thread.start()
			time.sleep(1)
			user_point += 1

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def main():
	thr_1 = threading.Thread(target=server)
	thr_1.start()
	thr_2 = threading.Thread(target=ranking)
	thr_2.start()


