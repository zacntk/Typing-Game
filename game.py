# define game_client for Thread
import random
import socket
import threading
import time
import pygame
import button

version = "2.0.8"
IP = "127.0.0.1" #กำหนดค่า IP ที่เชื่อมต่อ
PORT = 63453 #กำหนดค่าพอร์ตในการสื่อสาร #ช่วงพอร์ต 49152-65535
ADDR = (IP, PORT) #รวม HOST กับ PORT เข้าเป็น tuple เดียวกัน

time_real = 0
wpm_cal = 0
wpm = 0
count_round = 0
count_character = 0
tutorial = False
inputName = False
name_player = ""
wpm_real = 0

count_key_up = 2
count_key_down = 2
count_key_left = 1
count_key_right = 1
count_key_a = 1
count_key_b = 1
word_press = ['','','','']

def game_client():

	# define game_play for play
	def game_play():
		pygame.init()

		clock = pygame.time.Clock()

		# frame rate per seconds
		fps = 120

		# game window size
		BOTTM_PANEL = 185
		SCREEN_WIDTH = 800
		SCREEN_HEIGHT = 550

		# set screen size
		screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

		#set name of game
		pygame.display.set_caption('GAME AJARN PAO')

		# define game variables
		action_cooldown = 0
		action_wait_time = 90
		potion = False
		game_over = 0
		count_vocab = 0
		level_bandit = 1

		POSION_EFFECT = 25
		HP_KNIGHT = 500
		HP_BANDIT = 20
		DAMAGE_KNIGHT = 200
		DAMAGE_BANDIT = 5

		# define fonts
		font = pygame.font.SysFont('Fixedsys', 25)

		# define colours
		red = (255, 0, 0)
		green = (0, 255, 0)
		yellow = (255, 255, 0)

		# load images
		
		# background image
		BACKGROUND_IMG = pygame.image.load(
			'img/Background/bg.png').convert_alpha()
		BACKGROUND_IMG = pygame.transform.scale(BACKGROUND_IMG, (800, 400))

		# icon image
		ICON_IMG = pygame.image.load('img/Icons/logo.png').convert_alpha()
		pygame.display.set_icon(ICON_IMG)

		# panel image
		PANEL_IMG = pygame.image.load('img/Icons/panel.png').convert_alpha()
		
		# panel text image
		PANEL_TEXT_IMG = pygame.image.load(
			'img/Icons/panel_text.png').convert_alpha()
		
		PANEL_NAME = pygame.image.load(
			'img/Icons/panel_name.png').convert_alpha()

		# button images
		POSION_IMG = pygame.image.load('img/Icons/potion.png').convert_alpha()
		RESTART_IMG = pygame.image.load(
			'img/Icons/restart.png').convert_alpha()
		
		# load victory and defeat images
		VICTORY_IMG = pygame.image.load(
			'img/Icons/victory.png').convert_alpha()

		DEFEAT_IMG = pygame.image.load('img/Icons/defeat.png').convert_alpha()
		
		FASTEST_IMG = pygame.image.load('img/Icons/wpm.png').convert_alpha()

		#Load Tutorial image
		TUTORIAL_IMG =  pygame.image.load('img/Icons/how-to-play.png').convert_alpha()
		# load Sound
		ATTACK_SOUND = pygame.mixer.Sound("music/attack.wav")
		BACKGROUND_SOUND = pygame.mixer.Sound('music/bg_music.wav')
		DEFEAT_SOUND = pygame.mixer.Sound('music/defeat.wav')
		HURT_SOUND = pygame.mixer.Sound('music/hurt.wav')
		NEXT_LEVEL_SOUND = pygame.mixer.Sound('music/newlevel.wav')
		VICTORY_SOUND = pygame.mixer.Sound('music/win.wav')
		POSION_SOUND = pygame.mixer.Sound('music/potion.wav')
		
		# set Volume
		POSION_SOUND.set_volume(0.5)
		ATTACK_SOUND.set_volume(0.5)
		HURT_SOUND.set_volume(0.5)
		NEXT_LEVEL_SOUND.set_volume(0.5)
		DEFEAT_SOUND.set_volume(0.1)
		VICTORY_SOUND.set_volume(0.1)
		BACKGROUND_SOUND.set_volume(0.05)
		BACKGROUND_SOUND.play(loops = 10)

		def draw_text(text, font, text_col, x, y):
			img = font.render(text, True, text_col)
			screen.blit(img, (x, y))

		def draw_bg():
			screen.blit(BACKGROUND_IMG, (0, 0))

		def draw_panel():
			# draw panel rectangle
			screen.blit(PANEL_IMG, (0, SCREEN_HEIGHT - BOTTM_PANEL))
			# show knight stats
			draw_text(f'                 HP: {knight.hp}', font,
					  yellow, 100, SCREEN_HEIGHT - 150 + 20)
			for count, i in enumerate(bandit_list):
				# show name and health
				draw_text(f'ALIEN HP: {i.hp}', font, yellow, 550,
						  (SCREEN_HEIGHT - 150 + 20) + count * 60)

		def bandit_attack():
			number = 0
			while count_round != 1:
				time.sleep(5)
				if level_bandit != 6 and game_over == 0 and count_round != 1:
					number %= 2
					if bandit_list[number].alive == True:
						bandit_list[number].attack(knight)
						number += 1
					else:
						bandit_list[(number+1) % 2].attack(knight)
						number += 1
				else:
					break
		
		def wordPerMinute():
			time.sleep(2)
			global wpm
			global count_round
			while count_round != 1:
				wpm = wpm_cal/(time_real/60)
				wpm_out = str(format(wpm,'.1f')) + " wpm"
				font_typing = pygame.font.Font(None, 25)
				text = font_typing.render(wpm_out, True, (255, 255, 0))
				text_rect = text.get_rect(center=(50, 50))
				screen.blit(text, text_rect)

		def time_count():
			global time_real
			global count_round
			while count_round != 1:
				time.sleep(1)
				time_real += 1

		def draw_panel_text():
			# draw panel rectangle
			screen.blit(PANEL_TEXT_IMG, (45, 100))

		def draw_panel_fast():
			# draw panel rectangle
			screen.blit(FASTEST_IMG, (625, 40))

		def select_word(count_vocab):
			count_vocab_str = str(count_vocab)
			client.send(count_vocab_str.encode())
			data = client.recv(1024).decode()
			word_list = data
			return word_list

		def cut_head_char(word):
			return word[1:]

		def is_empty_word(word):
			return not word
		
		# fighter class
		class Fighter():
			def __init__(self, x, y, name, max_hp, strength, potions):
				self.name = name
				self.max_hp = max_hp
				self.hp = max_hp
				self.strength = strength
				self.start_potions = potions
				self.potions = potions
				self.alive = True
				self.animation_list = []
				self.frame_index = 0
				self.action = 0  # 0:idle, 1:attack, 2:hurt, 3:dead
				self.update_time = pygame.time.get_ticks()
				if self.name == "Bandit":
					temp_list = []
					# load Walk images
					for i in range(4):
						img = pygame.image.load(
							f'img/{self.name}/Walk/{i}.png')
						img = pygame.transform.scale(
							img, (img.get_width()/3, img.get_height()/3))
						temp_list.append(img)
					self.animation_list.append(temp_list)
					# load idle images
					temp_list = []
					for i in range(11):
						img = pygame.image.load(
							f'img/{self.name}/Idle/{i}.png')
						img = pygame.transform.scale(
							img, (img.get_width()/3, img.get_height()/3))
						temp_list.append(img)
					self.animation_list.append(temp_list)
					# load attack images
					temp_list = []
					for i in range(11):
						img = pygame.image.load(
							f'img/{self.name}/Attack/{i}.png')
						img = pygame.transform.scale(
							img, (img.get_width()/3, img.get_height()/3))
						temp_list.append(img)
					self.animation_list.append(temp_list)
					# load hurt images
					temp_list = []
					for i in range(6):
						img = pygame.image.load(
							f'img/{self.name}/Hurt/{i}.png')
						img = pygame.transform.scale(
							img, (img.get_width()/3, img.get_height()/3))
						temp_list.append(img)
					self.animation_list.append(temp_list)
					# load death images
					temp_list = []
					for i in range(7):
						img = pygame.image.load(
							f'img/{self.name}/Death/{i}.png')
						img = pygame.transform.scale(
							img, (img.get_width()/3, img.get_height()/3))
						temp_list.append(img)
					self.animation_list.append(temp_list)
					self.image = self.animation_list[self.action][self.frame_index]
					self.rect = self.image.get_rect()
					self.rect.center = (x, y)
				else:
					# load idle images
					temp_list = []
					for i in range(12):
						img = pygame.image.load(
							f'img/{self.name}/Idle/{i}.png')
						img = pygame.transform.scale(
							img, (img.get_width()/3, img.get_height()/3))
						temp_list.append(img)
					self.animation_list.append(temp_list)
					# load attack images
					temp_list = []
					for i in range(6):
						img = pygame.image.load(
							f'img/{self.name}/Attack/{i}.png')
						img = pygame.transform.scale(
							img, (img.get_width()/3, img.get_height()/3))
						temp_list.append(img)
					self.animation_list.append(temp_list)
					# load hurt images
					temp_list = []
					for i in range(6):
						img = pygame.image.load(
							f'img/{self.name}/Hurt/{i}.png')
						img = pygame.transform.scale(
							img, (img.get_width()/3, img.get_height()/3))
						temp_list.append(img)
					self.animation_list.append(temp_list)
					# load death images
					temp_list = []
					for i in range(6):
						img = pygame.image.load(
							f'img/{self.name}/Death/{i}.png')
						img = pygame.transform.scale(
							img, (img.get_width()/3, img.get_height()/3))
						temp_list.append(img)
					self.animation_list.append(temp_list)
					self.image = self.animation_list[self.action][self.frame_index]
					self.rect = self.image.get_rect()
					self.rect.center = (x, y)

			def update(self):
				animation_cooldown = 120
				# handle animation
				# update image
				self.image = self.animation_list[self.action][self.frame_index]
				# check if enough time has passed since the last update
				if pygame.time.get_ticks() - self.update_time > animation_cooldown:
					self.update_time = pygame.time.get_ticks()
					self.frame_index += 1
				# if the animation has run out then reset back to the start
				if self.frame_index >= len(self.animation_list[self.action]):
					if self.action == 4:
						self.frame_index = len(
							self.animation_list[self.action]) - 1
					else:
						self.idle()

			def walk(self):
				# set variables to idle animation
				self.action = 0
				self.frame_index = 0
				self.update_time = pygame.time.get_ticks()

			def idle(self):
				# set variables to idle animation
				if self.name == "Knight":
					self.action = 0
					self.frame_index = 0
					self.update_time = pygame.time.get_ticks()
				else:
					self.action = 1
					self.frame_index = 0
					self.update_time = pygame.time.get_ticks()

			def attack(self, target):
				#damage bonus
				damage_bonus = [0, 0, 0, 0, 5, 5, 10, -5, 999, 6, 0, -20, 0, 0, 10, 5, -5, -5, 0, 6, 6, 0, -20, 0, 0, 10, -5, -5, -5, 0, 6]
				# deal damage to enemy
				if self.name == "Knight":
					damage = self.strength + damage_bonus[random.randint(0,len(damage_bonus)- 1)]
				else:
					damage = self.strength
				target.hp -= damage
				ATTACK_SOUND.play()
				# run enemy hurt animation
				target.hurt()
				# check if target has died
				if target.hp < 1:
					target.hp = 0
					target.alive = False
					target.death()
				if damage == 0:
					damage_text = DamageText(
						target.rect.centerx, target.rect.y, str("MISS"), red)
					damage_text_group.add(damage_text)
				elif damage > 999:
					damage_text = DamageText(
						target.rect.centerx, target.rect.y, str("CRITICAL DAMAGE"), red)
					damage_text_group.add(damage_text)
				else:
					damage_text = DamageText(
						target.rect.centerx, target.rect.y, str(damage), red)
					damage_text_group.add(damage_text)
				# set variables to attack animation
				if self.name == "Knight":
					self.action = 1
					self.frame_index = 0
					self.update_time = pygame.time.get_ticks()
				else:
					self.action = 2
					self.frame_index = 0
					self.update_time = pygame.time.get_ticks()

			def hurt(self):
				# set variables to hurt animation
				HURT_SOUND.play()
				if self.name == "Knight":
					self.action = 2
					self.frame_index = 0
					self.update_time = pygame.time.get_ticks()
				else:
					self.action = 3
					self.frame_index = 0
					self.update_time = pygame.time.get_ticks()

			def death(self):
				# set variables to death animation
				if self.name == "Knight":
					self.action = 3
					self.frame_index = 0
					self.update_time = pygame.time.get_ticks()
				else:
					self.action = 4
					self.frame_index = 0
					self.update_time = pygame.time.get_ticks()

			def reset(self):
				self.alive = True
				self.potions = self.start_potions
				self.hp = self.max_hp
				self.frame_index = 0
				self.action = 0
				self.update_time = pygame.time.get_ticks()

			def draw(self):
				screen.blit(self.image, self.rect)

		class HealthBar():
			def __init__(self, x, y, hp, max_hp):
				self.x = x
				self.y = y
				self.hp = hp
				self.max_hp = max_hp

			def draw(self, hp):
				# update with new health
				self.hp = hp
				# calculate health ratio
				ratio = self.hp / self.max_hp
				pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))
				pygame.draw.rect(
					screen, green, (self.x, self.y, 150 * ratio, 20))

		class DamageText(pygame.sprite.Sprite):
			def __init__(self, x, y, damage, colour):
				pygame.sprite.Sprite.__init__(self)
				self.image = font.render(damage, True, colour)
				self.rect = self.image.get_rect()
				self.rect.center = (x, y)
				self.counter = 0

			def update(self):
				# move damage text up
				self.rect.y -= 1
				# delete the text after a few seconds
				self.counter += 1
				if self.counter > 30:
					self.kill()

		damage_text_group = pygame.sprite.Group()

		word = "start"
		
		knight = Fighter(200, 300, 'Knight', HP_KNIGHT, DAMAGE_KNIGHT, 5)

		global time_real
		global wpm_cal
		global wpm
		global count_round
		global count_character
		global tutorial
		global name_player
		global inputName
		global wpm_real
		global count_key_up
		global count_key_down
		global count_key_left
		global count_key_right
		global count_key_a
		global count_key_b
		global word_press	
 		
		while level_bandit != 6:
			clock.tick(fps)

			run = True
			damage = int((level_bandit**2)//1.5)
			bandit1 = Fighter(640, 280, 'Bandit', HP_BANDIT *
								  level_bandit, DAMAGE_BANDIT + damage, 0)
			bandit2 = Fighter(730, 300, 'Bandit', HP_BANDIT *
								  level_bandit, DAMAGE_BANDIT + damage, 0)

			bandit_list = []
			bandit_list.append(bandit1)
			bandit_list.append(bandit2)

			knight_health_bar = HealthBar(
				100, SCREEN_HEIGHT - 150 + 40, knight.hp, knight.max_hp)
			bandit1_health_bar = HealthBar(
				550, SCREEN_HEIGHT - 150 + 40, bandit1.hp, bandit1.max_hp)
			bandit2_health_bar = HealthBar(
				550, SCREEN_HEIGHT - 150 + 100, bandit2.hp, bandit2.max_hp)

			# create buttons
			potion_button = button.Button(
				screen, 100, SCREEN_HEIGHT - 150 + 70, POSION_IMG, 64, 64)
			restart_button = button.Button(
				screen, 340, 290, RESTART_IMG, 120, 30)
						
			while run:
				file = open("wpmfastest.txt", "r")

				# read file follow line
				lines = file.readlines()

				wpm_fastest = float(lines[0])

				file.close()

				# draw background
				draw_bg()
				
				# draw panel
				draw_panel()
				knight_health_bar.draw(knight.hp)
				bandit1_health_bar.draw(bandit1.hp)
				bandit2_health_bar.draw(bandit2.hp)
				draw_panel_text()
				# # draw fighters
				knight.update()
				knight.draw()
				for bandit in bandit_list:
					bandit.update()
					bandit.draw()

				# draw the damage text
				damage_text_group.update()
				damage_text_group.draw(screen)

				# control player actions
				# reset action variables
				attack = False
				potion = False
				target = None

				draw_panel_fast()
				font_typing = pygame.font.Font(None, 20)
				wpm_fastest = round(wpm_fastest, 1)
				text = font_typing.render(("Fasttest : " + str(wpm_fastest)).upper(), True, yellow)
				text_rect = text.get_rect(center=(700, 60))
				screen.blit(text, text_rect)

				font_typing = pygame.font.Font(None, 80)
				text = font_typing.render(word.upper(), True, (255, 255, 0))
				text_rect = text.get_rect(center=(SCREEN_WIDTH/2, 155))
				screen.blit(text, text_rect)
				
				mins, secs = divmod(time_real, 60)
				timer = '{:02d}:{:02d}'.format(mins, secs)
				timer = str(timer)
				font_typing = pygame.font.Font(None, 80)
				text = font_typing.render(timer, True, (255, 255, 0))
				text_rect = text.get_rect(center=(SCREEN_WIDTH/2, 300))
				screen.blit(text, text_rect)

				level_bandit_str = "LEVEL: "
				font_typing = pygame.font.Font(None, 30)
				text = font_typing.render(level_bandit_str, True, (255, 255, 0))
				text_rect = text.get_rect(center=(470, 470))
				screen.blit(text, text_rect)

				level_bandit_num = str(level_bandit)
				font_typing = pygame.font.Font(None, 30)
				text = font_typing.render(level_bandit_num, True, (255, 255, 0))
				text_rect = text.get_rect(center=(510, 470))
				screen.blit(text, text_rect)

				for event in pygame.event.get():
					if event.type == pygame.QUIT:
						client.close()
						pygame.quit()
					if event.type == pygame.KEYDOWN:
						if inputName == False and event.type == pygame.KEYDOWN and event.type != pygame.K_RETURN:
							name_player += chr(event.key)	
						if event.type == pygame.KEYDOWN:
							if event.key == pygame.K_RETURN and inputName == False:
								inputName = True
								name_player = name_player[:-1]
						if (event.key == pygame.K_UP and count_key_down == 2) or (event.key == pygame.K_UP and count_key_down == 1):
							count_key_up -= 1
						elif (event.key == pygame.K_DOWN and count_key_up == 1) or (event.key == pygame.K_DOWN and count_key_up == 0):
							count_key_down -= 1
						elif event.key == pygame.K_LEFT and count_key_up == 0 and count_key_down == 0:
							count_key_left -= 1
						elif event.key == pygame.K_RIGHT and count_key_up == 0 and count_key_down == 0 and count_key_left == 0:
							count_key_right -= 1
						elif chr(event.key) == 'a' and count_key_up == 0 and count_key_down == 0 and count_key_left == 0 and count_key_right == 0:
							count_key_a -= 1
						elif chr(event.key) == 'b' and count_key_up == 0 and count_key_down == 0 and count_key_left == 0 and count_key_right == 0 and count_key_a == 0:
							count_key_b -= 1
						elif event.key == pygame.K_ESCAPE:
							pygame.quit()	
						elif event.key == pygame.K_SPACE and tutorial == True:
							potion = True
						elif event.key == pygame.K_SPACE:
							tutorial = True
							transparent = (0, 0, 0, 0)
							TUTORIAL_IMG.fill(transparent)
						elif chr(event.key) != word[0]:
							word_press.append(chr(event.key))
						elif chr(event.key) == word[0]:
							word_press.append(chr(event.key))
							word = cut_head_char(word)
							if is_empty_word(word):
								wpm_cal += 1
								count_vocab += 1
								word = select_word(count_vocab)
								if count_vocab == 1:
									count_round = 0

									#count time for output on screen 
									thr_3 = threading.Thread(target=time_count)
									thr_3.start()
									#bandit auto attack every 7 seconds
									thr_4 = threading.Thread(target=bandit_attack)
									thr_4.start()
									#calculate WPM but this thread start after thread count time
									thr_5 = threading.Thread(target=wordPerMinute)
									thr_5.start()

								else:
									if bandit_list[0].alive == True:
										target = bandit_list[0]
										knight.attack(target)
										action_cooldown = 0
									else:
										target = bandit_list[1]
										knight.attack(target)
										action_cooldown = 0


				if potion_button.draw():
					potion = True
				draw_text(str(knight.potions), font, green, 160,
						  SCREEN_HEIGHT - 150 + 65)

				if game_over == 0:
					# player action
					if knight.alive == True:
						action_cooldown += 1
						if action_cooldown >= action_wait_time:
							# look for player action
							# potion
							if potion == True:
								if knight.potions > 0:
									# check if the potion would heal the player beyond max health
									if knight.max_hp - knight.hp > POSION_EFFECT:
										heal_amount = POSION_EFFECT
									else:
										heal_amount = knight.max_hp - knight.hp
									POSION_SOUND.play()
									knight.hp += heal_amount
									knight.potions -= 1
									damage_text = DamageText(
										knight.rect.centerx, knight.rect.y, str(heal_amount), green)
									damage_text_group.add(damage_text)
									action_cooldown = 0
					else:
						game_over = -1

				# check if all bandits are dead
				alive_bandits = 0
				for bandit in bandit_list:
					if bandit.alive == True:
						alive_bandits += 1
				if alive_bandits == 0 and level_bandit != 6 and game_over == 0:
					run = False
					level_bandit += 1
					NEXT_LEVEL_SOUND.play()
				if alive_bandits == 0 and level_bandit == 6:
					run = True
					game_over = 1
					level_bandit -= 1

				if count_key_up == 0 and count_key_down == 0 and count_key_left == 0 and count_key_right == 0 and count_key_a == 0 and count_key_b == 0:
					level_bandit = 6
					game_over = 1

				if word_press[(len(word_press)-1)] == 'z' and word_press[(len(word_press)-2)] == 'e' and word_press[(len(word_press)-3)] == 'g' and  word_press[(len(word_press)-4)] == 'g':
					game_over = -1

				if game_over != 0:
					alive_bandits = 2

					if game_over == 1:
						draw_bg()
						draw_panel()
						if count_round == 0:
							VICTORY_SOUND.play()
							NEXT_LEVEL_SOUND.stop()
							DEFEAT_SOUND.play()
							stop = timer
							stop = str(stop)
							wpm_real = wpm
							wpm_real = round(wpm_real, 2)
							file = open("wpmfastest.txt", "r")

							# read file follow line
							lines = file.readlines()

							file.close()

							if float(lines[0]) < wpm_real:
								file = open("wpmfastest.txt", "w")
								file.write(str(wpm_real))
								file.close()
								rank_message = "Ranking"
								client.send(rank_message.encode())
								rank_message = f'{name_player} {wpm_real}'
								client.send(rank_message.encode())
							

							font_typing = pygame.font.Font(None, 80)
							text = font_typing.render(
								stop, True, (255, 255, 0))
							text_rect = text.get_rect(
								center=(SCREEN_WIDTH/2, 200))
							screen.blit(text, text_rect)
							
							wpm_out = str(format(wpm_real,'.1f')) + " wpm"
							font_typing = pygame.font.Font(None, 25)
							text = font_typing.render(wpm_out, True, (255, 255, 0))
							text_rect = text.get_rect(center=(SCREEN_WIDTH/2, 150))
							screen.blit(text, text_rect)
							count_round = 1

						BACKGROUND_SOUND.set_volume(0)
						ATTACK_SOUND.set_volume(0)
						img_rect = VICTORY_IMG.get_rect(
							center=(SCREEN_WIDTH/2, 200))
						screen.blit(VICTORY_IMG, img_rect)

						font_typing = pygame.font.Font(None, 80)
						text = font_typing.render(stop, True, (255, 255, 0))
						text_rect = text.get_rect(center=(SCREEN_WIDTH/2, 200))
						screen.blit(text, text_rect)

						wpm_out = str(format(wpm_real,'.1f')) + " wpm"
						font_typing = pygame.font.Font(None, 25)
						text = font_typing.render(wpm_out, True, (255, 255, 0))
						text_rect = text.get_rect(center=(SCREEN_WIDTH/2, 150))
						screen.blit(text, text_rect)

					if game_over == -1:
						draw_bg()
						draw_panel()
						BACKGROUND_SOUND.set_volume(0)
						ATTACK_SOUND.set_volume(0)
						knight_health_bar.draw(knight.hp)
						bandit1_health_bar.draw(bandit1.hp)
						bandit2_health_bar.draw(bandit2.hp)
						img_rect = DEFEAT_IMG.get_rect(
							center=(SCREEN_WIDTH/2, 200))
						screen.blit(DEFEAT_IMG, img_rect)
						
						if count_round == 0:
							DEFEAT_SOUND.play()
							stop = timer
							stop = str(stop)
							wpm_real = wpm

							font_typing = pygame.font.Font(None, 80)
							text = font_typing.render(
								stop, True, (255, 255, 0))
							text_rect = text.get_rect(
								center=(SCREEN_WIDTH/2, 200))
							screen.blit(text, text_rect)
							
							wpm_out = str(format(wpm_real,'.1f')) + " wpm"
							font_typing = pygame.font.Font(None, 25)
							text = font_typing.render(wpm_out, True, (255, 255, 0))
							text_rect = text.get_rect(center=(SCREEN_WIDTH/2, 150))
							screen.blit(text, text_rect)
							count_round = 1

						font_typing = pygame.font.Font(None, 80)
						text = font_typing.render(stop, True, (255, 255, 0))
						text_rect = text.get_rect(center=(SCREEN_WIDTH/2, 200))
						screen.blit(text, text_rect)

						wpm_out = str(format(wpm_real,'.1f')) + " wpm"
						font_typing = pygame.font.Font(None, 25)
						text = font_typing.render(wpm_out, True, (255, 255, 0))
						text_rect = text.get_rect(center=(SCREEN_WIDTH/2, 150))
						screen.blit(text, text_rect)

					if restart_button.draw():
						level_bandit = 1
						damage = int((level_bandit**2)//1.5)
						bandit1 = Fighter(640, 280, 'Bandit', HP_BANDIT *
								level_bandit, DAMAGE_BANDIT + damage, 0)
						bandit2 = Fighter(730, 300, 'Bandit', HP_BANDIT *
								level_bandit, DAMAGE_BANDIT + damage, 0)

						bandit_list = []
						bandit_list.append(bandit1)
						bandit_list.append(bandit2)

						knight_health_bar = HealthBar(
							100, SCREEN_HEIGHT - 150 + 40, knight.hp, knight.max_hp)
						bandit1_health_bar = HealthBar(
							550, SCREEN_HEIGHT - 150 + 40, bandit1.hp, bandit1.max_hp)
						bandit2_health_bar = HealthBar(
							550, SCREEN_HEIGHT - 150 + 100, bandit2.hp, bandit2.max_hp)
						for bandit in bandit_list:
							bandit.reset()

						action_cooldown
						game_over = 0
						count_vocab = 0
						time_real = 0
						wpm_cal = 0
						count_key_up = 2
						count_key_down = 2
						count_key_left = 1
						count_key_right = 1
						count_key_a = 1
						count_key_b = 1
						word_press = ['','','','']

						BACKGROUND_SOUND.set_volume(0.05)
						knight.reset()

						for bandit in bandit_list:
							bandit.reset()

						word = "start"

				else:
					ATTACK_SOUND.set_volume(0.5)
					game_over = 0	

				if inputName == False:
					draw_panel_text()
					if name_player == "":
						enter_name = "Enter Your Name"
						font_typing = pygame.font.Font(None, 30)
						text = font_typing.render(enter_name, True, (255, 255, 0))
						text_rect = text.get_rect(center=(SCREEN_WIDTH/2, 155))
						screen.blit(text, text_rect)
					press_space_enter = "PRESS ENTER TO SET NAME"
					font_typing = pygame.font.Font(None, 25)
					text = font_typing.render(press_space_enter, True, (255, 255, 0))
					text_rect = text.get_rect(center=(SCREEN_WIDTH/2, 220))
					screen.blit(text, text_rect)
					font_typing = pygame.font.Font(None, 80)
					text = font_typing.render(name_player.upper(), True, (255, 255, 0))
					text_rect = text.get_rect(center=(SCREEN_WIDTH/2, 155))
					screen.blit(text, text_rect)

				elif tutorial == False:
					screen.blit(TUTORIAL_IMG, (0,0))
					press_space_to_start = "PRESS SPACEBAR IF YOU'RE READY."
					font_typing = pygame.font.Font(None, 30)
					text = font_typing.render(press_space_to_start, True, (255, 255, 0))
					text_rect = text.get_rect(center=(SCREEN_WIDTH/2, 485))
					screen.blit(text, text_rect)
				
				elif inputName == True:
					font_typing = pygame.font.Font(None, 50)
					text = font_typing.render(name_player.upper(), True, (255, 255, 0))
					text_rect = text.get_rect(center=(SCREEN_WIDTH/2, 400))
					screen.blit(text, text_rect)
					font_typing = pygame.font.Font(None, 20)
					text = font_typing.render(name_player.upper(), True, (255, 255, 0))
					text_rect = text.get_rect(center=(125, SCREEN_HEIGHT - 150 + 28))
					screen.blit(text, text_rect)

				pygame.display.update()

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client: #สร้าง object ในการเชื่อมต่อ socket
		client.connect((ADDR)) #เชื่อมต่อ
		game_play()

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def main():
	thr_3 = threading.Thread(target=game_client)
	thr_3.start()
