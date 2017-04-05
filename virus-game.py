#!/usr/bin/env python

# https://www.pygame.org/docs/ref/key.html
# https://inventwithpython.com/pygame/chapter2.html
# https://www.pygame.org/docs/ref/image.html#pygame.image.load
# http://usingpython.com/pygame-tilemaps/
# http://colorpalettes.net/category/pastel-color/

import pygame, os
from random import randint

pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

FPS = 30
WIDTH = 20
HEIGHT = 15
TILESIZE = 36
ENEMY_TIMER = 1000 # milliseconds => 2 seconds

blue     = (148,192,204)
bluer    = (21,99,108)
yellow   = (255,218,131)
yellower = (255,160,5)
black    = (69,66,75)
blacker  = (18,15,24)

try:
    #jump = pygame.mixer.Sound(os.path.join('data','jump.wav'))  #load sound
    boing     = pygame.mixer.Sound(os.path.join('sounds', 'boing.ogg'))
    fart1     = pygame.mixer.Sound(os.path.join('sounds', 'fart-1.ogg'))
    fart2     = pygame.mixer.Sound(os.path.join('sounds', 'fart-2.ogg'))
    fart3     = pygame.mixer.Sound(os.path.join('sounds', 'fart-3.ogg'))
    fart4     = pygame.mixer.Sound(os.path.join('sounds', 'fart-4.ogg'))
    fart5     = pygame.mixer.Sound(os.path.join('sounds', 'fart-5.ogg'))
    fart6     = pygame.mixer.Sound(os.path.join('sounds', 'fart-6.ogg'))
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
    thud      = pygame.mixer.Sound(os.path.join('sounds', 'thud.ogg'))
except:
    raise UserWarning, "could not preload sounds!"

try:
	music_normal = pygame.mixer.music.load(os.path.join('music', 'interlude-normal.ogg'))
except:
    raise UserWarning, "could not preload music!"

screen = pygame.display.set_mode((WIDTH * TILESIZE, HEIGHT * TILESIZE))
pygame.display.set_caption('Virus: The Game')

background = pygame.Surface(screen.get_size())
background.fill((0,0,0))
background = background.convert()

cells = [ [ 0 for y in range( HEIGHT ) ] for x in range( WIDTH ) ]

player_posx = 0
player_posy = 0
player_facing = 'right'
player = pygame.image.load(os.path.join('sprites', 'virus.png'))
player = player.convert_alpha()

enemy_posx = WIDTH - 1
enemy_posy = HEIGHT - 1
enemy_facing = 'left'
enemy = pygame.image.load(os.path.join('sprites', 'antivirus.png'))
enemy = enemy.convert_alpha()
enemy_bite = pygame.image.load(os.path.join('sprites', 'antivirus-bite.png'))
enemy_bite = enemy_bite.convert_alpha()

farted = False

clock = pygame.time.Clock()
pygame.time.set_timer(pygame.USEREVENT+1, ENEMY_TIMER)
playtime = 0.0
running = True


#sound_playing = laugh.play()
#while sound_playing.get_busy():
#	pygame.time.wait(FPS)
#pygame.mixer.music.set_volume(0.25)
#pygame.mixer.music.play(-1)

while running:
	screen.blit(background, (0,0))
	
	for x in range(WIDTH):
		for y in range(HEIGHT):
			if cells[x][y] == 0:
				color  = blue
				border = bluer
			elif cells[x][y] == 1:
				color  = yellow
				border = yellower
			elif cells[x][y] == 2:
				color  = black
				border = blacker
				
			#pygame.draw.rect(background, bluer, (row * TILESIZE,  column * TILESIZE, TILESIZE, TILESIZE))
			#pygame.draw.rect(background, blue, ((row * TILESIZE) - 1,  (column * TILESIZE) - 1, (TILESIZE - 2), (TILESIZE - 2)))
			pygame.draw.rect(background, border, (x * TILESIZE,  y * TILESIZE, TILESIZE, TILESIZE))
			pygame.draw.rect(background, color, ((x * TILESIZE) - 1,  (y * TILESIZE) - 1, (TILESIZE - 2), (TILESIZE - 2)))

	screen.blit(player, (player_posx * TILESIZE, player_posy * TILESIZE))
	screen.blit(enemy, (enemy_posx * TILESIZE, enemy_posy * TILESIZE))
	
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		
		if event.type == pygame.USEREVENT+1:
			attack = False
			
			if (player_posx - 1) <= enemy_posx <= (player_posx + 1):
				if (player_posy - 1) <= enemy_posy <= (player_posy + 1):
					attack = True
					screen.blit(enemy_bite, (enemy_posx * TILESIZE, enemy_posy * TILESIZE))
					pygame.display.update()

					rand = randint(1,6)
					if   rand == 1: growl = growl1.play()
					elif rand == 2: growl = growl2.play()
					elif rand == 3: growl = growl3.play()
					elif rand == 4: growl = growl4.play()
					elif rand == 5: growl = growl5.play()
					else:           growl = growl6.play()

					while growl.get_busy():
						pygame.time.wait(FPS)

					screen.blit(enemy, (enemy_posx * TILESIZE, enemy_posy * TILESIZE))
					pygame.display.update()
					heartbeat.play()

			if attack == False:
				if player_posy < enemy_posy:
					enemy_posy -= 1						
				elif player_posy > enemy_posy:
					enemy_posy += 1

				if player_posx < enemy_posx:
					enemy_posx -= 1

					if enemy_facing != 'left':
						enemy = pygame.transform.flip(enemy, True, False)
						enemy_bite = pygame.transform.flip(enemy_bite, True, False)
						enemy_facing = 'left'
						
				elif player_posx > enemy_posx:
					enemy_posx += 1

					if enemy_facing != 'right':
						enemy = pygame.transform.flip(enemy, True, False)
						enemy_bite = pygame.transform.flip(enemy_bite, True, False)
						enemy_facing = 'right'

		if event.type == pygame.KEYDOWN:
			moved = False
			
			if (event.key == pygame.K_UP) or (event.key == pygame.K_w):
				if player_posy == 0 or cells[player_posx][player_posy - 1] == 2:
					thud.play()
				else:
					player_posy -= 1
					moved = True

			elif (event.key == pygame.K_DOWN) or (event.key == pygame.K_s):
				if player_posy == HEIGHT - 1 or cells[player_posx][player_posy + 1] == 2:
					thud.play()
				else:
					player_posy += 1
					moved = True

			elif (event.key == pygame.K_LEFT) or (event.key == pygame.K_a):
				if player_posx == 0 or cells[player_posx - 1][player_posy] == 2:
					thud.play()
				else:
					player_posx -= 1
					moved = True

				if player_facing != 'left':
					player = pygame.transform.flip(player, True, False)
					player_facing = 'left'

			elif (event.key == pygame.K_RIGHT) or (event.key == pygame.K_d):
				if player_posx == WIDTH - 1 or cells[player_posx + 1][player_posy] == 2:
					thud.play()
				else:
					player_posx += 1
					moved = True

				if player_facing != 'right':
					player = pygame.transform.flip(player, True, False)
					player_facing = 'right'

			if moved == True:
				cells[ player_posx ][ player_posy ] += 1
				
				if cells[ player_posx ][ player_posy ] == 2:
					if farted == False:
						fart = randint(1,6)
						if fart == 1:
							fart1.play()
						elif fart == 2:
							fart2.play()
						elif fart == 3:
							fart3.play()
						elif fart == 4:
							fart4.play()
						elif fart == 5:
							fart5.play()
						else:
							fart6.play()
						
					farted = True
				else:
					farted = False

	pygame.display.update()
	milliseconds = clock.tick(FPS) # do not go faster than this frame rate
	playtime += milliseconds / 1000.0

print("Play time was %.2f seconds" % playtime)
