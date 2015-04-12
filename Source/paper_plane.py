import pygame, random, sys, shelve, os
from pygame.locals import *
from collections import OrderedDict
from time import *
sys.path.append("lib")
import parallax
'''
Global constants
'''

# Colors
BLACK    	= (   0,   0,   0)
WHITE    	= ( 255, 255, 255)
BLUE     	= (   0,   0, 255)
ORANGE   	= ( 252, 177,  54)
LIGHT_BLUE	= ( 1,   174, 240)
BROWN    	= ( 91,    0,   0)
RED 		= (255,    0,   0)
POS_LEFT 	= 0
POS_RIGHT	= 1
FPS			= 60
EVENT_TL = pygame.USEREVENT + 1 # Event turn left
EVENT_TR = pygame.USEREVENT + 2 # Event turn right
# Screen dimensions
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
IS_FULL_SCREEN = False
BG = {
		"clouds":'data/images/background.png',
	  	"factory":'data/images/factory_background.png',
	  	"cloud_to_factory":'data/images/gradient.png'
	  }

FONT_PATH = 'data/coders_crux.ttf'

'''
End of GC
'''

def newcolour():
	# any colour but black or white 
	return (random.randint(10,250), random.randint(10,250), random.randint(10,250))

def write(msg="pygame is cool",x=0,y=0,color=ORANGE,s=False,use_gravity_center=False,font="None",font_size=30): #use_gravity_center, will use the gravity center of the text.
	if(os.path.isfile(font)):
		myfont = pygame.font.Font(font, font_size)
	else:
		myfont = pygame.font.SysFont(font, font_size)
	mytext = myfont.render(msg, True, color)
	mytext_rect = mytext.get_rect()
	# G = myfont.render("+", True, RED) # UNCOMMENT 4 DEBUG : Display the gravity center
	size = list(myfont.size(msg))
	if(x <= SCREEN_WIDTH/2):
		x = x+10
	else:
		x = x-10-size[0]
	mytext = mytext.convert_alpha()
	mytext_rect.center = (x,y)
	if(s == False):
		if(use_gravity_center==True):
			screen.blit(mytext,mytext_rect)
		else:
			screen.blit(mytext,(x,y))
		# screen.blit(G,(x,y-10)) # UNCOMMENT 4 DEBUG : Display the gravity center
	else:
		if(use_gravity_center==True):
			s.blit(mytext,mytext_rect)
		else:
			s.blit(mytext,(x,y))
	return mytext

# This class represents the bar at the bottom that the player controls
class Player(pygame.sprite.Sprite):

	# Set speed vector
	change_x = 0
	change_y = 0
	walls = None
	frame_walls = None
	score = -2
	high_score = 0
	crached = False
	plane_color = LIGHT_BLUE #Blue by default
	plane_img = {	
					"face":pygame.image.load("data/images/plane_face.png"),
					"left":pygame.image.load("data/images/plane_left.png"),
					"right":pygame.image.load("data/images/plane_right.png")
				}
	
	# Constructor function
	def __init__(self, x, y,color=LIGHT_BLUE,high_score=0):
		# Call the parent's constructor
		super(self.__class__, self).__init__()
		self.plane_color = color
		# Set height, width
		self.image = self.plane_img["face"].convert() #pygame.Surface([22, 23],pygame.SRCALPHA) # Contain the plane
		self.image.set_colorkey(WHITE) # Light is the transparent color

		# Make our top-left corner the passed-in location.
		self.rect = self.image.get_rect()
		self.rect.y = y
		self.rect.x = x

		self.high_score = high_score # Set the hscore
	def change_player_color(self,color):
		self.image.fill(color)
	def changespeed(self, x, y):
		#Change the speed and coordinates of the player
		if(not self.crached):
			if(x<0):
				self.image = self.plane_img["left"].convert()
				# self.image.fill(self.plane_color) # Nevermind...
				self.image.set_colorkey(WHITE)
			elif(x>0):
				self.image = self.plane_img["right"].convert()
				# self.image.fill(self.plane_color) # Nevermind...
				self.image.set_colorkey(WHITE)
			self.change_x = x
			self.change_y = y

	def update(self):
		if(self.score >= 0):
			write(str(self.score),SCREEN_WIDTH)
		else:
			write("0",SCREEN_WIDTH)
		if(self.score >= self.high_score): # Are you good ?
			self.high_score = self.score # Ok ! not that bad !
		write(str(self.high_score),SCREEN_WIDTH,30,RED)
		# Update the player position.
		# Move left/right
		if((SCREEN_HEIGHT/5) > self.rect.y):
			# Move down, simulate grav.
			self.rect.y += self.change_y
		self.rect.x += self.change_x

		# Did this update cause us to hit a wall?
		block_hit_list = pygame.sprite.spritecollide(self, self.walls, False)
		block_hit_list_frame = pygame.sprite.spritecollide(self, self.frame_walls, False)
		
		for block in block_hit_list_frame:
				#If we hit the frame blocks then push us back in the game
			self.change_x = -(self.change_x)
		for block in block_hit_list:
				self.changespeed(0,0) # Stop moves
				self.crached = True # Set the variable
				print "***Collision detected***"
				write("***Crash !***",0,0,RED)
		for block in self.walls:
			# print str(block.rect.x) + " AND => " + str(self.rect.x)
			block.rect.y = block.rect.y-(self.change_y) #Move the blocks up
			# write(str(self.rect.y),10,0)
			# write(str(block.rect.y),10,30)
			if(block.rect.y==self.rect.y): #Is the player @ the same line as block ?
				# print(self.score)
				self.score +=1

class Wall(pygame.sprite.Sprite): 
	wall_img =	{
					"frame_left":pygame.image.load("data/images/frame_left.png"), # Need to be defined & drawn
					"frame_right":pygame.image.load("data/images/frame_right.png"), # Need to be defined & drawn
					"lvl_left":pygame.image.load("data/images/lvl_left.png"), # Need to be defined & drawn
					"platform_left_e":pygame.image.load("data/images/platform_left_edge.png"), # Need to be defined & drawn
					"platform_left_b":pygame.image.load("data/images/platform_body_left.png"), # Need to be defined & drawn
					"platform_right_e":pygame.image.load("data/images/platform_right_edge.png"), # Need to be defined & drawn
					"platform_right_b":pygame.image.load("data/images/platform_body_right.png"), # Need to be defined & drawn
					"lvl_right":pygame.image.load("data/images/lvl_right.png"), # Need to be defined & drawn
					"demo":pygame.image.load("data/images/platform_demo.png") # Need to be defined & drawn
				}
	# Wall the player can run into.
	def __init__(self, x, y, width, height,color=WHITE,img="",blit_pos="",fit_img = True):
		# Constructor for the wall that the player can run into.
		# Call the parent's constructor
		super(self.__class__, self).__init__()
		self.width,self.height = width,height 
		# Make a blue wall, of the size specified in the parameters
		self.container = pygame.Surface([width, height]).convert()
		self.container.fill(color)
		if(img in self.wall_img):# If is in the wall_img array
			self.container.set_colorkey(color) # Make the color transparent
			if(blit_pos == "right"):
				i_pos = (width,0)
			elif(isinstance(blit_pos,tuple) and len(blit_pos == 2)):
				i_pos = blit_pos
			else: # We assume that it on the default position = left
				i_pos = (0,0)
			if(fit_img == True):
				self.container.blit(pygame.transform.scale(self.wall_img[img], (width,height)),i_pos) # Blit the scaled image
			else:
				self.container.blit(self.wall_img[img],i_pos) # Blit the image regardless to the resolution
		elif(img == "wall_left"):
			pre_img_size = self.wall_img["platform_right_e"].get_size()
			prb_img_size = self.wall_img["platform_right_b"].get_size()
			self.container.set_colorkey(color) # Make the color transparent
			self.container.blit(self.wall_img["platform_right_e"],(width-pre_img_size[0],0))
			for i in xrange(1,(width/prb_img_size[0])+2):
				self.container.blit(self.wall_img["platform_right_b"],(width-pre_img_size[0]-i*prb_img_size[0],0))
		elif(img == "wall_right"):
			ple_img_size = self.wall_img["platform_left_e"].get_size()
			plb_img_size = self.wall_img["platform_left_b"].get_size()
			self.container.set_colorkey(color) # Make the color transparent
			self.container.blit(self.wall_img["platform_left_e"],(0,0))
			for i in xrange(0,(width/plb_img_size[0])+1):
				self.container.blit(self.wall_img["platform_left_b"],(i*plb_img_size[0]+ple_img_size[0],0))


		# self.wall_img["demo"] = pygame.transform.scale(self.wall_img["demo"].convert(),(width,height))
		
		self.image = self.container

		# Make our top-left corner the passed-in location.
		self.rect = self.container.get_rect()
		self.rect.y = y
		self.rect.x = x

	def write(self,msg,x=0,y=0,color=LIGHT_BLUE,font_size=50,font=FONT_PATH): # An alias to the write function
		if(x == "center"):
			x = self.width/2
		if(y == "center"):
			y = self.height/2
		write(msg,x,y,color,self.image,True,font=font,font_size=font_size)
		
	def draw(self,x,y,surface,img):
		img_size = img.convert().get_size()
		if(x!=0):
			x = x-img_size[0]
		if(y!=0):
			y = y-img_size[1]
		surface.blit(img,(x,y))
		

class Menu(object):
	''' Variables definition '''
	legacy_list = []
	fields = []
	font_size = 32
	font_path = FONT_PATH # Font being used
	font = pygame.font.Font # Init font
	dest_surface = pygame.Surface # Init surface
	fields_quantity = 0
	background_color = (51, 51, 51)
	text_color = (255, 255, 153)
	selection_color = (153, 102, 255)
	selection_position = 0
	paste_position = (0, 0)
	menu_width = 0
	menu_height = 0
	''' End of variables definition '''

	class Pole(object):
		text = ''
		field = pygame.Surface
		field_rect = pygame.Rect
		selection_rect = pygame.Rect

	def move_menu(self, top, left):
		self.paste_position = (top, left)
	def get_block_position(self):
		return self.paste_position
	def set_colors(self, text, selection, background):
		self.background_color = background
		self.text_color = text
		self.selection_color = selection

	def set_fontsize(self, font_size):
		self.font_size = font_size

	def set_font(self, path):
		self.font_path = path

	def get_position(self):
		return self.selection_position

	def init(self, legacy_list, dest_surface):
		self.legacy_list = legacy_list
		self.dest_surface = dest_surface
		self.fields_quantity = len(self.legacy_list)
		self.create_structure()

	def draw(self, move=0):
		if move:
			self.selection_position += move
			if self.selection_position == -1:
				self.selection_position = self.fields_quantity - 1
			self.selection_position %= self.fields_quantity
		menu = pygame.Surface((self.menu_width, self.menu_height))
		menu.fill(self.background_color)
		selection_rect = self.fields[self.selection_position].zaznaczenie_rect
		pygame.draw.rect(menu, self.selection_color, selection_rect)
		for i in xrange(self.fields_quantity):
			menu.blit(self.fields[i].pole, self.fields[i].pole_rect)
			bg.draw(screen)
			menu.set_colorkey(self.background_color) # Get the bloc invisible
		self.dest_surface.blit(menu, self.paste_position)
		return self.selection_position

	def create_structure(self):
		self.menu_height = 0
		self.font = pygame.font.Font(self.font_path, self.font_size)
		for i in xrange(self.fields_quantity):
			self.fields.append(self.Pole())
			self.fields[i].tekst = self.legacy_list[i]
			self.fields[i].pole = self.font.render(
				self.fields[i].tekst,
				1,
				self.text_color
			)

			self.fields[i].pole_rect = self.fields[i].pole.get_rect()
			move = int(self.font_size * 0.2)

			height = self.fields[i].pole_rect.height
			self.fields[i].pole_rect.left = move
			self.fields[i].pole_rect.top = move + (move * 2 + height) * i

			width = self.fields[i].pole_rect.width + move * 2
			height = self.fields[i].pole_rect.height + move * 2
			left = self.fields[i].pole_rect.left - move
			top = self.fields[i].pole_rect.top - move

			self.fields[i].zaznaczenie_rect = (left, top, width, height)
			if width > self.menu_width:
					self.menu_width = width
			self.menu_height += height
		x = self.dest_surface.get_rect().centerx - self.menu_width / 2
		y = self.dest_surface.get_rect().centery - self.menu_height / 2
		mx, my = self.paste_position
		self.paste_position = (x+mx, y+my)

def gen_wall(game,pos,slimit=500,color=BROWN,img=""):
	size = random.randint(100,slimit)
	if(pos == POS_LEFT):
		x = 10
	else:
		x = SCREEN_WIDTH-size-10
	wall = Wall(x, SCREEN_HEIGHT+10, size, 30,color,img=img)
	game.wall_list.add(wall)
	game.all_sprite_list.add(wall)


class Play(object):
	"""Play the game with some parameters"""
	param = {}
	# List to hold all the sprites
	all_sprite_list = pygame.sprite.Group()
	# Make the walls. (x_pos, y_pos, width, height)
	wall_list = pygame.sprite.Group()
	level = 0
	wall_gentime = 2000 # in ms

	def __init__(self,uparam):
		#super(self.__class__, self).__init__()
		super(Play, self).__init__()
		dparam = {	
					"pcolor":ORANGE,
					"dynamic_speed":False,
					"speed":1,
					"tspeed":3,
				}
		self.param.update(dparam) #Merge given array & default array
	def setp(self,uparam): # set parametter
		self.param.update(uparam) #Merge given array & default array
	
	def increase_speed(self,player,factor=1):
		'''
			> Need to decrease wall generation time &
			> Need to increase gravity speed
			 (!) Tips : - Use player.changespeed function
						- Use self.wall_gentime variable
		'''
		pass


	def set_high_score(self,player,file_name="score.ppp"):
		f = shelve.open(file_name)
		if("best_score" in f):# Is variable defined ?
			if(player.score <= f["best_score"]):
				return False # Nah ! looser !
			else:
				f["best_score"] = player.score
				return True # Ok saved !
		else:
			f["best_score"] = player.score
			return True # Ok saved !
	
	def get_high_score(self,file_name="score.ppp"):
		f = shelve.open(file_name)
		if("best_score" in f):# Is variable defined ?
			return int(f["best_score"])
		else:
			f["best_score"] = 0 # Set the high score & go !
			return 0
	
	def crashed(self,player):
		self.reset_game()
		if(self.set_high_score(player)):
			screen.fill(ORANGE)
			write("**** "+str(player.score)+" IS THE NEW BEST SCORE ****",SCREEN_WIDTH/2,SCREEN_HEIGHT/2,WHITE,use_gravity_center=True)
		else:
			screen.fill(BLACK)
			write("You're a loooooser !",SCREEN_WIDTH/2,SCREEN_HEIGHT/2,WHITE,use_gravity_center=True)
		write("<ESCAPE> Main menu",0,(SCREEN_HEIGHT)-30,WHITE)
		write("<ENTER> Retry",SCREEN_WIDTH,(SCREEN_HEIGHT)-30,WHITE)
		del player # Clean the game
	def set_level(self,lvl=0):
		self.level = lvl

	def reset_game(self):
		# List to hold all the sprites
		self.all_sprite_list = pygame.sprite.Group()
		# Make the walls. (x_pos, y_pos, width, height)
		self.wall_list = pygame.sprite.Group()

	def start(self,lvl=0):
		self.set_level(lvl)
		frame_wall_list = pygame.sprite.Group()
		# Left side wall
		wall = Wall(0, 0, 10, SCREEN_HEIGHT,BLACK,"frame_left")
		frame_wall_list.add(wall)
		self.all_sprite_list.add(wall)

		''' Obstacles samples
		self, x, y, width, height,color=BROWN
		'''
		wall = Wall(10, SCREEN_HEIGHT/5, 300, 530,BLUE,"lvl_left")
		self.wall_list.add(wall)
		self.all_sprite_list.add(wall)
		
		wall = Wall(SCREEN_WIDTH-310, SCREEN_HEIGHT/5, 300, 530,BLUE,"lvl_right")
		wall.write(str(self.level),"center","center",font_size=150)
		self.wall_list.add(wall)
		self.all_sprite_list.add(wall)
		
		''' End of Obstacles '''

		# Right side wall
		wall = Wall(SCREEN_WIDTH-10, 0, 10, SCREEN_HEIGHT,BLACK,"frame_right")
		frame_wall_list.add(wall)
		self.all_sprite_list.add(wall)
		
		
		# Create the player paddle object @ the middle of the screen
		player = Player(SCREEN_WIDTH/2, 0,self.param["pcolor"],self.get_high_score())
		player.walls = self.wall_list
		player.frame_walls = frame_wall_list
		
		self.all_sprite_list.add(player)
		
		clock = pygame.time.Clock()
		
		done = False
		
		speed = 10 # Speed of the airplane
		tspeed = 13 # Turning speed
		tesla,ttesla = 0,0 # Time elapsed since last action
		player.changespeed(0,speed) # Not turning at t=0
		dt = clock.tick(FPS) # delta of t
		pos = POS_RIGHT # Start the game @ left position
		# bg = player.background_img.convert_alpha()
		# size = bg.get_rect().size
		while not done:
			screen.fill(WHITE) # Clean the screen
			bg.draw(screen)
			bg.scroll(1,{"orientation":"vertical","direction":"top"})
			tesla += dt
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					show_menu(menu_lst) # On quit, return to the main menu
				elif event.type == EVENT_TL:
					player.changespeed(-tspeed, speed)
					pygame.time.set_timer(EVENT_TL, 0) # Stop the event to be repeated
				elif event.type == EVENT_TR:
					player.changespeed(tspeed, speed)
					pygame.time.set_timer(EVENT_TR, 0) # Stop the event to be repeated
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_LEFT:
						pygame.time.set_timer(EVENT_TL,1) #25 ms before the action is realised
					elif event.key == pygame.K_RIGHT:
						pygame.time.set_timer(EVENT_TR,1) #25 ms before the action is realised
			if (tesla > self.wall_gentime):
				pos = 1-pos #Turn in the opposite dir.
				tesla = 0 # Reset timer
				if(pos == POS_RIGHT):
					gen_wall(self,pos,color=RED,img="wall_right") #Generate a wall
				else:
					gen_wall(self,pos,color=BLUE,img="wall_left") #Generate a wall
			# Rendering
			if(player.score == 2):
				bg.add_transition(BG["clouds"], .1,(SCREEN_WIDTH,SCREEN_HEIGHT))
				bg.add_transition(BG["clouds"], .1,(SCREEN_WIDTH,SCREEN_HEIGHT))
				bg.add_transition(BG["cloud_to_factory"], .1,(SCREEN_WIDTH,SCREEN_HEIGHT))
				bg.add_transition(BG["factory"], .1,(SCREEN_WIDTH,SCREEN_HEIGHT))
				bg.enable_transition()
			self.all_sprite_list.draw(screen) # Draw everything so that text will be on top
			self.all_sprite_list.update()
			pygame.display.flip()
			clock.tick(FPS) #Frame rate (in milliseconds)
			if(player.crached):
				del frame_wall_list
				self.crashed(player) # The player crashed ! What a nooooob !
				break # Stop the loop


# Call this function so the Pygame library can initialize itself
pygame.init()
# pygame.mouse.set_visible(False) # Hide the mouse

# Create an 800x600 sized screen
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
bg = parallax.ParallaxSurface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RLEACCEL)
bg.add(BG["clouds"], .1,(SCREEN_WIDTH,SCREEN_HEIGHT))

# Set the title of the window
pygame.display.set_caption('SUUUUPPPEEERRR Paper Plane v0.1')


game = Play({"hey":False})
#game.setp({"pcolor":ORANGE})

def change_screen_mode(w,h,fs=False):
	global SCREEN_WIDTH
	global SCREEN_HEIGHT
	global IS_FULL_SCREEN
	global menu_lst
	if((w != SCREEN_WIDTH and h != SCREEN_HEIGHT) or (IS_FULL_SCREEN!=fs)):
		SCREEN_WIDTH = w
		SCREEN_HEIGHT = h
		IS_FULL_SCREEN = fs
		if(fs== True):
			screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT],pygame.FULLSCREEN)
		else:
			screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
		bg.update(BG["clouds"], 3,(SCREEN_WIDTH,SCREEN_HEIGHT))
		show_menu(menu_lst['Options'][show_menu]["Display"][show_menu])
	return True

def show_menu(mlst,title=""): #menu list menu is a list with (name:function)
	if not mlst: # If menu is empty
		return False
	screen.fill((51, 51, 51))
	if(menu_lst.keys() != mlst.keys()): # If not located @ the main menu
		mlst["<"] = {show_menu:(menu_lst)} #Append the go back to main menu button in options
	keys = mlst.keys()
	menu = Menu()
	menu.init(keys, screen)  # necessary
	menu.draw()
	mpos = menu.get_block_position()
	pygame.key.set_repeat(199, 69)  # (delay,interval)
	pygame.display.update()
	while 1:
		for event in pygame.event.get():
			if event.type == KEYDOWN:
				if event.key == K_UP:
					# here is the Menu class method
					menu.draw(-1)
				if event.key == K_DOWN:
					# here is the Menu class method
					menu.draw(1)
				if event.key == K_RETURN: # Did we press ENTER ?
					name = keys[menu.get_position()] # Get the name of the current position.
					if isinstance(mlst[name], list): # Is builtin function bunch of lists ?
						for fn in mlst[name]: # Then
							fn() # Run every function
					elif isinstance(mlst[name], dict): # Is it a standalone function
						for fn, param in mlst[name].iteritems(): # Then
							if(isinstance(param, tuple)): # Is this a tuple ?
								fn(*param) # Put tuple as fn param.
							else:
								fn(param) # Run every function
					else:
						mlst[name]() # Run it !
				if event.key == K_ESCAPE or event.key == K_LEFT: # Quit the game
					name = keys[menu.get_position()] # Get the name of the current position.
					if(name not in menu_lst.keys()):
						show_menu(menu_lst)
					else:
						pygame.display.quit()
						sys.exit()
				pygame.display.update() # Update the display so, we can animate screen
			elif event.type == QUIT:
				pygame.display.quit()
				sys.exit()
		pygame.time.wait(8)

menu_lst = OrderedDict({
			'Play !':OrderedDict({
				show_menu:OrderedDict({
					"Lvl 0":OrderedDict({game.start:(0)}),
					"Lvl 2":OrderedDict({game.start:(2)}),
				})
			}),
			'Options':OrderedDict({
				show_menu:OrderedDict({
					"Color":OrderedDict({
						show_menu:OrderedDict({
							"Blue":OrderedDict({ game.setp:{"pcolor":BLUE},write:("Done !",0,0,BLUE) }),
							"Black":OrderedDict({ game.setp:{"pcolor":BLACK},write:("Done !",0,0,BLACK) }),
							"Brown":OrderedDict({ game.setp:{"pcolor":BROWN},write:("Done !",0,0,BROWN) }),
							"Red":OrderedDict({ game.setp:{"pcolor":RED},write:("Done !",0,0,RED) }),
							"Orange":OrderedDict({ game.setp:{"pcolor":ORANGE},write:("Done !",0,0,ORANGE) })
						})
					}),
					"Display":OrderedDict({
						show_menu:OrderedDict({
							"Windowed (800x600)":OrderedDict({ change_screen_mode:(800,600) }),
							"Windowed (1024x768)":OrderedDict({ change_screen_mode:(1024,768) }),
							"Windowed (1280x800)":OrderedDict({ change_screen_mode:(1280,800) }),
							"Full Screen (800x600)":OrderedDict({ change_screen_mode:(800,600,True) }),
							"Full Screen (1024x768)":OrderedDict({ change_screen_mode:(1024,768,True) }),
							"Full Screen (1280x800)":OrderedDict({ change_screen_mode:(1280,800,True) }),
						})
					}),

				})
			}),
			'Quit':[
				pygame.display.quit,
				sys.exit
				]
		})

def main():
	show_menu(menu_lst)
if __name__ == '__main__': main()
