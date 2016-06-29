import pygame
import socket
import threading
from queue import Queue
import sys
import string
from pygame.locals import *

message_queue = Queue()
send_queue = Queue()
output_word = ''

class Chessboard:
	def __init__(self):
		self.grid_round = 3
		self.grid_count = 8
		self.grid_location = []
 
		self.game_over = False
		self.winner = None
		self.judge_win=0
		self.piece = 'b'
		self.black = 12
		self.white = 12
		self.grid = []
		self.restart_game()
		
	def restart_game(self):
		self.game_over = False
		self.winner = None
		self.judge_win=0
		self.piece = 'b'
		self.black = 12
		self.white = 12
		
		self.grid = []
		for i in range(self.grid_round):
			self.grid.append(list("." * self.grid_count))
		
		for i in range(self.grid_round):
			print ("->")
			for j in range(self.grid_count):
				print ("a"+ self.grid[i][j] + "~")
			print ("\n")
		# 可下子的位置 3x8 array
		self.grid_location = [[(60,60), (60, 350), (60, 640), (350, 640), (640, 640), (640, 350), (640, 60), (350, 60)], [(140, 140), (140, 350), (140, 560), (350, 560), (560, 560), (560, 350), (560, 140), (350, 140)], [(220, 220), (220, 350), (220, 480), (350, 480), (480, 480), (480, 350), (480, 220), (350, 220)]]
		
	def is_my_turn(self, my_piece):
		return my_piece == self.piece

	def set_piece(self, r, c):
		if self.can_set_piece(r, c):
			self.grid[r][c] = self.piece			
			return True
		return False
		
	def take_other_piece(self, r, c):
		if self.grid[r][c]==self.piece:
			self.grid[r][c] = '.'
			return True
			
	def turn_piece_color(self):
		# 轉換棋子顏色
		if self.piece == 'b':
			self.black = self.black-1
			self.piece = 'w'
		else:
			self.white = self.white-1
			self.piece = 'b'

	def can_set_piece(self, r, c):
		"""檢查是否能下子"""
		try:
			if self.game_over:
				return False
			elif (r==-1) and (c==-1):
				return False
			
			if self.piece == 'b':
				self.black = self.black-1
			else:
				self.white = self.white-1
			
			return self.grid[r][c] == '.'
		except IndexError:
			return False
		
	def can_get_piece(self, r, c):
		"""檢查是否能提子"""
		if self.piece == 'b':
			if self.grid[r][c] == 'w':
				self.grid[r][c] = '.'
				return True
		else:
			if self.grid[r][c] == 'b':
				self.grid[r][c] = '.'
				return True
			
	def get_three_count(self, r, c):
		# 三層連一條
		if self.grid[0][c]==self.piece and self.grid[1][c]==self.piece and self.grid[2][c]==self.piece:
			return True
		# 同層相連	
		if c==1 or c==3 or c==5 or c==7:
			if self.grid[r][c]==self.piece and self.grid[r][(c+1)%8]==self.piece and self.grid[r][c-1]==self.piece:
				return True
		else:
			if self.grid[r][c]==self.piece and self.grid[r][c+1]==self.piece and self.grid[r][(c+2)%8]==self.piece:
				return True
			if self.grid[r][c]==self.piece and self.grid[r][(c+7)%8]==self.piece and self.grid[r][(c+6)%8]==self.piece:
				return True
		
		return False

		
class ChessboardClient(Chessboard):

	def __init__(self):
		super().__init__()

		self.grid_size = 60
		self.start_x, self.start_y = 30, 50

	def is_in_area(self, x, y):
		for i in range(self.grid_round):
			for j in range(self.grid_count):
				locat_x = self.grid_location[i][j][0]
				locat_y = self.grid_location[i][j][1]
				if (x<locat_x+20 and x>locat_x-20) and (y<locat_y+20 and y>locat_y-20): 
					return True
		return False

	def get_r_c(self, x, y):
		# 得到下子座標轉成存取的位置
		r,c = -1,-1
		for i in range(self.grid_round):
			for j in range(self.grid_count):
				locat_x = self.grid_location[i][j][0]
				locat_y = self.grid_location[i][j][1]
				if (x<locat_x+20 and x>locat_x-20) and (y<locat_y+20 and y>locat_y-20): 
					r,c = i,j
		return r, c

	def draw(self, screen):
		# 棋盤底色
		pygame.draw.rect(screen, (185, 122, 87), [30,30,640,640], 0)

		pygame.draw.line(screen, (0, 0, 0), (60, 60), (60, 640), 3)
		pygame.draw.line(screen, (0, 0, 0), (60, 60), (640, 60), 3)
		pygame.draw.line(screen, (0, 0, 0), (640, 60), (640, 640), 3)
		pygame.draw.line(screen, (0, 0, 0), (60, 640), (640, 640), 3)
		
		pygame.draw.line(screen, (0, 0, 0), (140, 140), (560, 140), 3)
		pygame.draw.line(screen, (0, 0, 0), (140, 140), (140, 560), 3)
		pygame.draw.line(screen, (0, 0, 0), (560, 140), (560, 560), 3)
		pygame.draw.line(screen, (0, 0, 0), (140, 560), (560, 560), 3)
		
		pygame.draw.line(screen, (0, 0, 0), (220, 220), (480, 220), 3)
		pygame.draw.line(screen, (0, 0, 0), (220, 220), (220, 480), 3)
		pygame.draw.line(screen, (0, 0, 0), (220, 480), (480, 480), 3)
		pygame.draw.line(screen, (0, 0, 0), (480, 220), (480, 480), 3)

		pygame.draw.line(screen, (0, 0, 0), (350, 60), (350, 220), 3)
		pygame.draw.line(screen, (0, 0, 0), (350, 480), (350, 640), 3)
		pygame.draw.line(screen, (0, 0, 0), (60, 350), (220, 350), 3)
		pygame.draw.line(screen, (0, 0, 0), (480, 350), (640, 350), 3)
		
		for r in range(self.grid_round):
			for c in range(self.grid_count):
				piece = self.grid[r][c]
				if piece != '.':
					if piece == 'b':
						color = (0, 0, 0)
					else:
						color = (255, 255, 255)

					x = self.grid_location[r][c][0]
					y = self.grid_location[r][c][1]
					pygame.draw.circle(screen, color, [x, y], self.grid_size // 2)

def receive_message(server_socket):
	"""接收server傳送的訊息"""
	global output_word
	while True:
		message = server_socket.recv(1024)
		if message == b'':
			break

		print(message)
		message_queue.put(message)
		tmp = message.decode('utf-8', "replace")
		if tmp[0] == '9':
			output_word = message
			print(output_word)

def send_message(server_socket):
	while True:
		msg = send_queue.get()
		server_socket.send(str.encode(msg))


class GomokuClient:
	def __init__(self):
		pygame.init()

		self.screen = pygame.display.set_mode((700, 760))
		pygame.display.set_caption("雙人連線九子棋")
		self.clock = pygame.time.Clock()
		self.font = pygame.font.SysFont('Calibri', 25, True, False)
		self.going = True
		self.flag = 0
		self.word = ''
		self.piece = 'wait'

		self.chessboard = ChessboardClient()

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect(('127.0.0.1', 22004))
		self.csocket = s

		s.send(str.encode('join_game'))
		threading.Thread(target=receive_message, args=(s,)).start()
		threading.Thread(target=send_message, args=(s,)).start()

		# 遊戲狀態
		# start_connect: 開始連線
		# wait_connect: 連線中...
		# wait_game: 等待遊戲開始
		# gaming: 遊戲進行中
		# game_over: 遊戲結束
		self.status = "wait_connect"

	def loop(self):
		while self.going:
			self.update()
			self.draw()
			self.clock.tick(60)

		pygame.display.quit() 
		pygame.quit()
		try:
			sys.exit() # this always raises SystemExit
		except SystemExit as e :
			print(e)
		except:
			print("Something went horribly wrong") # some other exception got raised
			
			
	def update(self):
		current_string = []
		for e in pygame.event.get():
			#print(e.type)
			if e.type == pygame.QUIT:
				self.going = False
			elif e.type == pygame.MOUSEBUTTONDOWN:
				#self.handle_MOUSEBUTTONDOWN(e)
				if self.status == 'gaming':
					if not self.chessboard.is_in_area(e.pos[0], e.pos[1]):
						return
					if not self.chessboard.is_my_turn(self.piece):
						return
					print(e.pos[0],e.pos[1])
					r, c = self.chessboard.get_r_c(e.pos[0], e.pos[1])
					
					# 判斷可不可以下子
					if self.flag == 0:
						if not self.chessboard.can_set_piece(r, c):
							return
						# 送出封包
						send_queue.put('3{0},{1}'.format(r, c))
						
					else:
						if not self.chessboard.can_get_piece(r, c):
							return
						# 送出封包
						send_queue.put('4{0},{1}'.format(r, c))
			elif e.type == KEYUP:
				
				if e.key == 13:
					self.word = self.word[:]
					print (self.word)
					self.word = "9"+self.word
					self.csocket.send(str.encode(self.word))
					self.word = ''
				else:
					self.word = self.word + str(chr(e.key))
					
				#self.screen.blit(self.font.render('1111', True, (0, 0, 0)), (10, 600))
				
			#elif e.type == KEYDOWN:
			#	print (e.key)
			#	print (e.mod)
				
		'''
		event = pygame.event.poll()
		if event.type == KEYDOWN:
		return event.key		
		
		if (inkey = get_key())!='':
			if inkey == K_BACKSPACE:
				current_string = current_string[0:-1]
			#elif inkey == K_RETURN:
				#break
			elif inkey == K_MINUS:
				current_string.append("_")
			elif inkey <= 127:
				current_string.append(chr(inkey))
			display_box(self.screen, str.join("", current_string) + "_")
		'''
						
		# 檢查 Queue
		# 有的話取一個來處理
		if not message_queue.empty():
			job = message_queue.get()
			
			if job[0] == ord('0'):
				self.piece = job[1:].decode("utf-8")
				self.status = 'wait_game'
			elif job[0] == ord('1'):
				if job[1:] == b'game_start':
					self.status = 'gaming'
			elif job[0] == ord('3'):
				if self.status == 'gaming':
					pos_msg = job[1:].decode("utf-8")
					r, c = pos_msg.split(',')
					r = int(r)
					c = int(c)

					# 下子
					if self.chessboard.set_piece(r, c):
						if self.chessboard.get_three_count(r, c):
							self.flag = 1
							#print("True")
							# 傳送下子不換邊
							#send_queue.put('4{0},{1}'.format(r, c))
						
						else:
							#send_queue.put('3{0},{1}'.format(r, c))
						#轉換方
							self.chessboard.turn_piece_color()
			
			elif job[0]== ord('4'):
				if self.status == 'gaming':
					pos_msg = job[1:].decode("utf-8")
					r, c = pos_msg.split(',')
					r = int(r)
					c = int(c)
					
					self.chessboard.take_other_piece(r, c)
					self.chessboard.turn_piece_color()
					self.flag = 0
						

	'''		
	def take_piece_rc(self):
		print ("ffffffffff")
		for c in pygame.event.get():
			print (c)
			if c.type == pygame.QUIT:
				self.going = False
			elif c.type == pygame.MOUSEBUTTONDOWN:
				self.takehandle_MOUSEBUTTONDOWN(e)
	
	def takehandle_MOUSEBUTTONDOWN(self, e):
		# 判斷可不可以提子
		if not self.chessboard.can_get_piece(r, c):
			return
	'''
	
	def draw(self):
		self.screen.fill((255, 255, 255))
		# self.screen.blit(self.font.render("FPS: {0:.2F}".format(self.clock.get_fps()), True, (0, 0, 0)), (10, 10))
		
		if self.piece == 'b':
			self.screen.blit(self.font.render('Black', True, (0, 0, 0)), (100, 10))
		elif self.piece == 'w':
			self.screen.blit(self.font.render('White', True, (0, 0, 0)), (100, 10))
		else:
			self.screen.blit(self.font.render(self.piece, True, (0, 0, 0)), (100, 10))

		self.chessboard.draw(self.screen)
		if self.chessboard.game_over:
			self.screen.blit(
				self.font.render("{0} Win".format("Black" if self.chessboard.winner == 'b' else "White"), True,
								 (0, 0, 0)), (200, 10))

		status_text = self.status
		if self.status == 'wait_connect':
			status_text = 'wait_connect...'
		elif self.status == 'wait_game':
			status_text = 'wait_game'
		elif self.status == 'gaming':
			status_text = 'gaming'
		elif self.status == 'game_over':
			status_text = 'game_over'
		
		self.screen.blit(self.font.render(status_text, True, (0, 0, 0)), (400, 10))
		
		fontobject = pygame.font.SysFont('Microsoft JhengHei', 20, False, False)
		
		pygame.draw.rect(self.screen, (255, 255, 255), (30, 700, 640, 30), 0)
		pygame.draw.rect(self.screen, (128, 128, 128), (30, 700, 640, 30), 1)
		pygame.draw.rect(self.screen, (128, 128, 128), (30, 700, 45, 30), 0)
		self.screen.blit(fontobject.render("Send", 1, (255,255,255)), (35, 710))
		
		self.screen.blit(fontobject.render(self.word.encode('utf-8'), 1, (0, 0, 0)), (90, 710))

		self.screen.blit(fontobject.render(output_word, 1, (0, 0, 0)), (90, 740))
		pygame.display.update()


	def handle_MOUSEBUTTONDOWN(self, e):
		# 計算座標，檢查是否可以下子，在送出封包
		if self.status == 'gaming':
			if not self.chessboard.is_in_area(e.pos[0], e.pos[1]):
				return
			if not self.chessboard.is_my_turn(self.piece):
				return
			print(e.pos[0],e.pos[1])
			r, c = self.chessboard.get_r_c(e.pos[0], e.pos[1])
			
			# 判斷可不可以下子
			if not self.chessboard.can_set_piece(r, c):
				return

			# 送出封包
			# send_queue.put('3{0},{1}'.format(r, c))

def get_key():
	while 1:
		event = pygame.event.poll()
		if event.type == KEYDOWN:
			return event.key
		else:
			pass

def display_box(screen, message):
	fontobject = pygame.font.SysFont('Microsoft JhengHei', 20, False, False)
	if len(message) != 0:
		screen.blit(fontobject.render(message, 1, (0,0,0)), (80, 710))
		pygame.display.flip()

def ask(screen, question):
  #"ask(screen, question) -> answer"
	pygame.font.init()
	current_string = []
	
	display_box(screen, str.join("", current_string) + "_")
	while 1:
		inkey = get_key()
		if inkey == K_BACKSPACE:
			current_string = current_string[0:-1]
		elif inkey == K_RETURN:
			break
		elif inkey == K_MINUS:
			current_string.append("_")
		elif inkey <= 127:
			current_string.append(chr(inkey))
		display_box(screen, str.join("", current_string) + "_")
	return str.join("", current_string)

if __name__ == '__main__':
	print(pygame.QUIT)
	game = GomokuClient()
	game.loop()

