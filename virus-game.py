#!/usr/bin/env python

# https://www.pygame.org/docs/ref/key.html
# https://inventwithpython.com/pygame/chapter2.html
# https://www.pygame.org/docs/ref/image.html#pygame.image.load
# http://usingpython.com/pygame-tilemaps/
# http://colorpalettes.net/category/pastel-color/

# TODO - game over / low health
# TODO - level complete / door exit
# TODO - power-ups / increase health
# TODO - levels
# TODO - change erased percent to true percent 

import pygame, os, math
from random import randint

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

FPS = 30
WIDTH = 20
HEIGHT = 15
TILESIZE = 36
ENEMY_START = 5000 # 5 seconds
ENEMY_TIMER = 1000 # milliseconds => 2 seconds
TILES_NEEDED = math.trunc((WIDTH * HEIGHT) / 2)
TILES_FINISHED = 0
HEALTH = 4
SCORE  = 0
LAST_ATTACK = 0

blue     = (148,192,204)
blue_b   = (21,99,108)
green    = (175,199,110)
green_b  = (103,152,0)
yellow   = (255,218,131)
yellow_b = (255,160,5)
red      = (229,120,117)
red_b    = (215,78,73)
black    = (69,66,75)
black_b  = (18,15,24)
cream    = (255,235,201)

try:
    #jump = pygame.mixer.Sound(os.path.join('data','jump.wav'))  #load sound
    boing     = pygame.mixer.Sound(os.path.join('sounds', 'boing.ogg'))
    choir     = pygame.mixer.Sound(os.path.join('sounds', 'choir.ogg'))
    fart1     = pygame.mixer.Sound(os.path.join('sounds', 'fart-1.ogg'))
    fart2     = pygame.mixer.Sound(os.path.join('sounds', 'fart-2.ogg'))
    fart3     = pygame.mixer.Sound(os.path.join('sounds', 'fart-3.ogg'))
    fart4     = pygame.mixer.Sound(os.path.join('sounds', 'fart-4.ogg'))
    fart5     = pygame.mixer.Sound(os.path.join('sounds', 'fart-5.ogg'))
    fart6     = pygame.mixer.Sound(os.path.join('sounds', 'fart-6.ogg'))
    girly     = pygame.mixer.Sound(os.path.join('sounds', 'girly-scream.ogg'))
    growl1    = pygame.mixer.Sound(os.path.join('sounds', 'growl-1.ogg'))
    growl2    = pygame.mixer.Sound(os.path.join('sounds', 'growl-2.ogg'))
    growl3    = pygame.mixer.Sound(os.path.join('sounds', 'growl-3.ogg'))
    growl4    = pygame.mixer.Sound(os.path.join('sounds', 'growl-4.ogg'))
    growl5    = pygame.mixer.Sound(os.path.join('sounds', 'growl-5.ogg'))
    growl6    = pygame.mixer.Sound(os.path.join('sounds', 'growl-6.ogg'))
    heartbeat = pygame.mixer.Sound(os.path.join('sounds', 'heartbeat.ogg'))
    heartbeat.set_volume(1)
    laugh     = pygame.mixer.Sound(os.path.join('sounds', 'evil-laugh.ogg'))
    laugh.set_volume(0.25)
    tada      = pygame.mixer.Sound(os.path.join('sounds', 'tada.ogg'))
    thud      = pygame.mixer.Sound(os.path.join('sounds', 'thud.ogg'))
    music     = pygame.mixer.music.load(os.path.join('music', 'interlude-normal.ogg'))
except:
    raise UserWarning, "could not preload sounds!"
  
try:
	sprite_player     = pygame.image.load(os.path.join('sprites', 'virus.png'))
	sprite_enemy      = pygame.image.load(os.path.join('sprites', 'antivirus.png'))
	sprite_enemy_bite = pygame.image.load(os.path.join('sprites', 'antivirus-bite.png'))
	sprite_door       = pygame.image.load(os.path.join('sprites', 'door.png'))
	sprite_door_open  = pygame.image.load(os.path.join('sprites', 'door-open.png'))
	sprite_font       = pygame.image.load(os.path.join('sprites', 'font-kromasky.png'))
except:
	raise UserWarning, "could not preload sprites!"

screen = pygame.display.set_mode((WIDTH * TILESIZE, (HEIGHT * TILESIZE) + 48))
pygame.display.set_caption('Virus: The Game')

background = pygame.Surface(screen.get_size())
background.fill((0,0,0))
background = background.convert()

# Coordinates
coords = [ [ 0 for y in range( HEIGHT ) ] for x in range( WIDTH ) ]
coords_player = [0, 0]
coords_enemy  = [WIDTH - 1, HEIGHT - 1]
coords_door   = ( randint(1, WIDTH - 1), randint(1, HEIGHT - 1) )

# Flags
RUNNING    = True   # Game running
GAME_OVER  = False
DOOR_FOUND = False
DOOR_OPEN  = False
ENEMY_RUNNING = False # Enemy can move and attack

# Sprites

# Player
player_facing = 'right'
player_direction = 'right'
enemy_facing = 'left'

enemy_image = True
enemy_flash = 0
enemy_attack = False

clock = pygame.time.Clock()
pygame.time.set_timer(pygame.USEREVENT+1, ENEMY_TIMER)
elapsed = 0
milliseconds = 0


#sound_playing = laugh.play()
#while sound_playing.get_busy():
#	pygame.time.wait(FPS)
#pygame.mixer.music.set_volume(0.25)
#pygame.mixer.music.play(-1)

def valid_move(x, y):
	if x < 0 or y < 0:
		thud.play()
		return False
	elif x > (WIDTH - 1) or y > (HEIGHT - 1):
		thud.play()
		return False
	elif x == coords_enemy[0] and y == coords_enemy[1]:
		girly.play()
		return False
	elif coords[x][y] == 3:
		thud.play()
		return False
	elif coords_door[0] == x and coords_door[1] == y:
		if DOOR_FOUND == False:
			return True
		elif DOOR_OPEN == False:
			thud.play()
			return False
		else:
			# TODO: trigger next level
			return True
	else:
		return True

def font(string):
	sprite_width  = 16
	sprite_height = 16

	surface_width = sprite_width * len(string)
	surface_height = sprite_height
	surface = pygame.Surface((surface_width, surface_height))
	
	string = string.upper()
	string_pos = 0
	for char in string:
		sprite_pos = (ord(char) - 32) * sprite_width
		sprite_font.set_clip(pygame.Rect(sprite_pos, 0, sprite_width - 1, sprite_height - 1))
		sprite_char = sprite_font.subsurface(sprite_font.get_clip())
		
		surface.blit(sprite_char, (string_pos * sprite_width, 0))
		string_pos += 1
		
	return surface
	
def status_bar():
	text_health = "HEALTH: "
	text_health = text_health.ljust(len(text_health) + HEALTH, '$') # "$" is a heart in our font
	sprite_health = font(text_health)
	screen.blit(sprite_health, (8, (HEIGHT * TILESIZE) + 8))

	percent_erased = math.trunc((float(TILES_FINISHED) / TILES_NEEDED) * 100)
	text_erased = "ERASED: " +  str(percent_erased) + "%"
	sprite_erased = font(text_erased)
	screen.blit(sprite_erased, (8, (HEIGHT * TILESIZE) + 24))
	
	text_score = "SCORE: " + str(SCORE)
	sprite_score = font(text_score)
	screen.blit(sprite_score, ((WIDTH * TILESIZE) - ((len(text_score) * 16) + 8), (HEIGHT * TILESIZE) + 8))
		

while RUNNING:
	# Door Actions
	if DOOR_FOUND == False:
		# Did we find the door?
		if coords_player[0] == coords_door[0] and coords_player[1] == coords_door[1]:
			DOOR_FOUND = True
			choir.play()
	elif DOOR_OPEN == False:
		# Should we open the door?
		if TILES_FINISHED >= TILES_NEEDED:
			DOOR_OPEN = True
			tada.play()

	# Enemy Actions
	if ENEMY_START <= elapsed:
		ENEMY_RUNNING = True
	else:
		enemy_flash += milliseconds
		if enemy_flash > 500:
			enemy_image = False if enemy_image else True
			enemy_flash = 0
		else:
			enemy_image = True


	# Key & Timer Events
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			RUNNING = False
		
		if event.type == pygame.USEREVENT+1 and ENEMY_RUNNING == True:
			
			if LAST_ATTACK > elapsed: # Not done with last attack
				enemy_attack = True
			else:
				enemy_attack = False
				LAST_ATTACK = 0

			if LAST_ATTACK == 0: 
				# Can we attack again?
				if (coords_player[0] - 1) <= coords_enemy[0] <= (coords_player[0] + 1):
					if (coords_player[1] - 1) <= coords_enemy[1] <= (coords_player[1] + 1):
						LAST_ATTACK = elapsed
						enemy_attack = True

						rand = randint(1,6)
						if   rand == 1: growl = growl1.play()
						elif rand == 2: growl = growl2.play()
						elif rand == 3: growl = growl3.play()
						elif rand == 4: growl = growl4.play()
						elif rand == 5: growl = growl5.play()
						else:           growl = growl6.play()
						
						heartbeat.play()
						HEALTH -= 1
				
				# Could not attack, so move
				if LAST_ATTACK == 0:
					# move left
					if coords_enemy[0] > coords_player[0]:
						coords_enemy[0] -= 1

						if enemy_facing != 'left':
							sprite_enemy      = pygame.transform.flip(sprite_enemy, True, False)
							sprite_enemy_bite = pygame.transform.flip(sprite_enemy_bite, True, False)
							enemy_facing      = 'left'
					
					# move right
					elif coords_enemy[0] < coords_player[0]:
						coords_enemy[0] += 1

						if enemy_facing != 'right':
							sprite_enemy      = pygame.transform.flip(sprite_enemy, True, False)
							sprite_enemy_bite = pygame.transform.flip(sprite_enemy_bite, True, False)
							enemy_facing      = 'right'
					
					# move up
					if coords_enemy[1] > coords_player[1]:
						coords_enemy[1] -= 1						
					
					# move down
					elif coords_enemy[1] < coords_player[1]:
						coords_enemy[1] += 1

		if event.type == pygame.KEYDOWN:
			moved = False
			
			# jump
			if (event.key == pygame.K_SPACE):
				# jump left
				if player_direction == 'left' and coords[ coords_player[0] - 1 ][ coords_player[1] ] == 3:
					if valid_move( coords_player[0] - 2, coords_player[1] ):
						boing.play()
						coords_player[0] -= 2
						moved = True
				
				# jump right
				elif player_direction == 'right' and coords[ coords_player[0] + 1 ][ coords_player[1] ] == 3:
					if valid_move( coords_player[0] + 2, coords_player[1] ):
						boing.play()
						coords_player[0] += 2
						moved = True
				
				# jump up
				elif player_direction == 'up' and coords[ coords_player[0] ][ coords_player[1] - 1 ] == 3:
					if valid_move( coords_player[0], coords_player[1] - 2 ):
						boing.play()
						coords_player[1] -= 2
						moved = True
				
				# jump down
				elif player_direction == 'down' and coords[ coords_player[0] ][ coords_player[1] + 1 ] == 3:
					if valid_move( coords_player[0], coords_player[1] + 2 ):
						boing.play()
						coords_player[1] += 2
						moved = True
				
				# unable to jump
				else:
					fart = randint(1,6)
					if   fart == 1: fart1.play()
					elif fart == 2: fart2.play()
					elif fart == 3: fart3.play()
					elif fart == 4: fart4.play()
					elif fart == 5: fart5.play()
					else:           fart6.play()

			# move right
			elif (event.key == pygame.K_RIGHT) or (event.key == pygame.K_d):
				player_direction = 'right'
									
				if valid_move( coords_player[0] + 1, coords_player[1] ):
					coords_player[0] += 1
					moved = True

				if player_facing != 'right':
					sprite_player = pygame.transform.flip(sprite_player, True, False)
					player_facing = 'right'
					
			# move left
			elif (event.key == pygame.K_LEFT) or (event.key == pygame.K_a):
				player_direction = 'left'
				
				if valid_move( coords_player[0] - 1, coords_player[1] ):
					coords_player[0] -= 1
					moved = True

				if player_facing != 'left':
					sprite_player = pygame.transform.flip(sprite_player, True, False)
					player_facing = 'left'

			# move up
			if (event.key == pygame.K_UP) or (event.key == pygame.K_w):
				player_direction = 'up'
									
				if valid_move( coords_player[0], coords_player[1] -1 ):
					coords_player[1] -= 1
					moved = True

			# move down
			elif (event.key == pygame.K_DOWN) or (event.key == pygame.K_s):
				player_direction = 'down'
									
				if valid_move( coords_player[0], coords_player[1] + 1):
					coords_player[1] += 1
					moved = True

			# Score & Tile Changes
			if moved == True:
				coords[ coords_player[0] ][ coords_player[1] ] += 1

				if coords[ coords_player[0] ][ coords_player[1] ] == 3:
					TILES_FINISHED += 1
					SCORE += 10
				else:
					SCORE += 1

########################################################################
# DRAW SPRITES
########################################################################

	screen.blit(background, (0,0))
	
	status_bar()

	# Background Tiles
	for x in range(WIDTH):
		for y in range(HEIGHT):
			if coords[x][y] == 0:
				color  = blue
				border = blue_b
			elif coords[x][y] == 1:
				color  = yellow
				border = yellow_b
			elif coords[x][y] == 2:
				color  = red
				border = red_b
			elif coords[x][y] == 3:
				color  = black
				border = black_b
			elif door_coords[0] == x and door_coords[1] == y:
				
				if DOOR_FOUND == False:
					color  = blue
					border = blue_b
				else:
					color  = green
					border = green_b

			pygame.draw.rect(background, border, (x * TILESIZE,  y * TILESIZE, TILESIZE, TILESIZE))
			pygame.draw.rect(background, color, ((x * TILESIZE) - 1,  (y * TILESIZE) - 1, (TILESIZE - 2), (TILESIZE - 2)))

	# Player Sprite
	screen.blit(sprite_player, (coords_player[0] * TILESIZE, coords_player[1] * TILESIZE))
	
	# Enemy Sprite
	if enemy_image == True:
		if enemy_attack == True: screen.blit(sprite_enemy_bite, ( coords_enemy[0] * TILESIZE, coords_enemy[1] * TILESIZE ))
		else:					 screen.blit(sprite_enemy, ( coords_enemy[0] * TILESIZE, coords_enemy[1] * TILESIZE ))
			
	
	# Door Sprite
	if DOOR_FOUND:
		if DOOR_OPEN:
			screen.blit(sprite_door_open, (coords_door[0] * TILESIZE, coords_door[1] * TILESIZE))
		else:
			screen.blit(sprite_door, (coords_door[0] * TILESIZE, coords_door[1] * TILESIZE))


########################################################################
# TIME KEEPING
########################################################################

	pygame.display.update()
	milliseconds = clock.tick(FPS) # do not go faster than this frame rate
	elapsed += milliseconds

print("Play time was %.2f seconds" % (elapsed / 1000.0))
