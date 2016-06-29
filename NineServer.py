import socket
import threading
import time
from queue import Queue

message_queue = Queue()
status = None
players = []
"""
負責棋盤的邏輯處理
"""
class Chessboard:
	def __init__(self):
		self.grid_count = 19

		self.game_over = False
		self.winner = None
		self.piece = 'b'
		self.grid = []

		self.restart_game()

	def restart_game(self):
		self.game_over = False
		self.winner = None
		self.piece = 'b'

		self.grid = []
		for i in range(self.grid_count):
			self.grid.append(list("." * self.grid_count))

	def is_my_turn(self, my_piece):
		return my_piece == self.piece

	def choose_piece(self, r, c):
		if self.grid[r][c]==self.piece:
			self.grid[r][c] = 'r'
			return True
		return False
		
	def set_piece(self, r, c):
		for i in range(3):
			for j in range(8):
				if self.grid[i][j] == 'r':
					self.grid[i][j] = '.'
	
		if self.can_set_piece(r, c):
			self.grid[r][c] = self.piece
			
			return True
		return False
			
	def turn_piece(self):
		if self.piece == 'b':
			self.piece = 'w'
		else:
			self.piece = 'b'

	def clear_piece(self, r, c):
		if self.piece == self.grid[r][c]:
			return True
		return False
		
	def can_set_piece(self, r, c):
		"""檢查是否能下子"""
		if self.game_over:
			return False

		return self.grid[r][c] == '.'

	def take_other_piece(self, r, c):
		self.grid[r][c] = '.'
		return True
		
	def printboard(self):
		for j in range(8):
			print (self.grid[0][j] + "\t" + self.grid[1][j]  + "\t" + self.grid[2][j])
		
		
def receive_message(client_socket):
	"""接收玩家傳送的訊息"""
	while True:
		message = client_socket.recv(1024)
		if message == b'':
			break

		if status == 'game_start':
			print(message)
			message_queue.put(message)
			tmp = message.decode('utf-8', "replace")
			if tmp[0] == '9':
				print('message send to all player')
				players[0].send(message)
				players[1].send(message)

	# 向queue發送連00010線中斷通知
	# TODO


def main():
	global status

	# 初始化 server_socket
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind(('127.0.0.1', 26100))
	server_socket.listen(2)

	# 等待兩位玩家連線
	# 預設是0號玩家執黑子，1號玩家執白子

	while len(players) < 2:
		(client_socket, address) = server_socket.accept()

		# 告知玩家連線成功，並告訴玩家執哪一子
		msg = client_socket.recv(1024)
		if msg == b'join_game':
			players.append(client_socket)
			if len(players) == 1:
				client_socket.send(b'0b')
			else:
				client_socket.send(b'0w')
			time.sleep(5)
			threading.Thread(target=receive_message, args=(client_socket,)).start()

	# 初始化棋盤
	# 變更遊戲狀態 -> 對戰中
	# 告知玩家開始遊戲
	# TODO
	board = Chessboard()
	status = 'game_start'
	players[0].send(b'1game_start')
	players[1].send(b'1game_start')

	# 不斷從 Queue 接收玩家下子的要求
	# 並發出更新到所有玩家
	while True:
		job = message_queue.get()

		if job[0] == ord('3'):
			print (job)
			pos_msg = job[1:].decode("utf-8")
			if len(pos_msg.split(',')) == 2:
				r,c = pos_msg.split(',')
				r = int(r)
				c = int(c)

				if board.set_piece(r, c):
					players[0].send(job)
					players[1].send(job)
					board.turn_piece()
					board.printboard()
		
		elif job[0] == ord('4'):
			pos_msg = job[1:].decode("utf-8")
			if len(pos_msg.split(',')) == 2:
				r,c = pos_msg.split(',')
				r = int(r)
				c = int(c)
				
				if board.clear_piece(r, c):	
					players[0].send(job)
					players[1].send(job)
					board.take_other_piece(r, c)
					board.printboard()
					
		elif job[0] == ord('5'):
			pos_msg = job[1:].decode("utf-8")
			if len(pos_msg.split(',')) == 2:
				r,c = pos_msg.split(',')
				r = int(r)
				c = int(c)
				print("clear_piece:{}".format(board.clear_piece(r, c)))
				if board.clear_piece(r, c):	
					players[0].send(job)
					players[1].send(job)
					board.choose_piece(r, c)
					board.printboard()
			
if __name__ == '__main__':
	main()

