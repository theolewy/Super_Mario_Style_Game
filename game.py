import math, pygame, sys
from pygame.locals import *
from math import *
import random

WHITE = (255,255,255)
NAVYBLUE = (0,0,128)
CLEAR = (0,0,0,0)

(WINDOWWIDTH,WINDOWHEIGHT) = (800,500)

pygame.init()

FPS      = 30
fpsClock = pygame.time.Clock()

DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))
CHANGE_SCREEN_TO = 'level1'
CURRENT_LEVEL = ''

# -------------------------------------------------- #
# -------------- UNIVERSAL FUNCTIONS --------------- #
# -------------------------------------------------- #

# ------------- Coord Converters --------------- # 
#(x,y) are coords starting from topleft of screen
#(a,b) are coords starting from topleft of floor surface

def screen_coords_to_floor_coords(x,y):	
	(a,b) = (x+Floor.offsetx,y+Floor.offsety) 	
	if a > Floor.rect.width-1 or b > Floor.rect.height-1:
		return (None,None)
	else:
		return(a,b)     	#NB if (a,b) is out of range of floor mask we return (None,None)

def floor_coords_to_screen_coords(a,b):
	(x,y) = (a-Floor.offsetx,b-Floor.offsety) 	
	return(x,y)
	

# ------------ Background Scrolling ---------------- # 
# Allows sprites to scroll correctly with background
# (a,b) are location of sprites midbottom relative to top left of floor

def scroll_with_BG(self):
	Floor.update_offset()
	(x,y) = floor_coords_to_screen_coords(self.a,self.b)
	self.rect.midbottom = (x,y)
	
# ------------ Sense Nearby Objects ---------------- # 	
# Allows any sprite to sense what objects are nearby

def onBottom(self):				
	sprites_below = {'on':[], 'in':[]}
	(a,b) = (self.a,self.b)
	for key, group in Interactable_sprites_dict.items():
		for sprite in group:
			if sprite == self:
				pass
			else:
				temp = int(collision(a,b,sprite)) + int(collision(a,b-1,sprite))
				if temp == 1:
					sprites_below['on'].append(sprite)
				elif temp == 2:
					sprites_below['in'].append(sprite)
	return sprites_below
	
def onLeft(self):				
	sprites_left = {'on':[], 'in':[]}
	(a,b) = (self.a - self.SPRITEWIDTH//2, self.b - self.SPRITEHEIGHT*2//3)
	for key, group in Interactable_sprites_dict.items():
		for sprite in group:
			if sprite == self:
				pass
			else:
				temp = int(collision(a,b,sprite)) + int(collision(a+1,b,sprite))
				if temp == 1:
					sprites_left['on'].append(sprite)
				elif temp == 2:
					sprites_left['in'].append(sprite)
	return sprites_left
	
def onTop(self):				
	sprites_above = {'on':[], 'in':[]}
	(a,b) = (self.a, self.b - self.SPRITEHEIGHT)
	for key, group in Interactable_sprites_dict.items():
		for sprite in group:
			if sprite == self:
				pass
			else:
				temp = int(collision(a,b,sprite)) + int(collision(a,b-1,sprite))
				if temp == 1:
					sprites_above['on'].append(sprite)
				elif temp == 2:
					sprites_above['in'].append(sprite)
	return sprites_above

def inMiddle(self):				
	sprites_middle = {'in':[]}
	(a,b) = (self.a, self.b - self.SPRITEHEIGHT//2)
	for key, group in Interactable_sprites_dict.items():
		for sprite in group:
			if sprite == self:
				pass
			else:
				temp = int(collision(a,b,sprite))
				if temp == 1:
					sprites_middle['in'].append(sprite)
	return sprites_middle
	
def onRight(self):				
	sprites_right = {'on':[], 'in':[]}
	(a,b) = (self.a + self.SPRITEWIDTH//2, self.b - self.SPRITEHEIGHT*2//3)
	for key, group in Interactable_sprites_dict.items():
		for sprite in group:
			if sprite == self:
				pass
			else:
				temp = int(collision(a,b,sprite)) + int(collision(a-1,b,sprite))
				if temp == 1:
					sprites_right['on'].append(sprite)
				elif temp == 2:
					sprites_right['in'].append(sprite)
	return sprites_right
	
def is_object_nearby(self, Sprite_Group, onWhere):
	sprites = onWhere(self)
	for sprite in sprites['in']:
		if sprite in Sprite_Group:
			return 'in'
	for sprite in sprites['on']:
		if sprite in Sprite_Group:
			return 'on'
	return False
	
def what_sprite_nearby(self, Sprite_Group, onWhere):
	sprites = onWhere(self)
	for sprite in sprites['in']:
		if sprite in Sprite_Group:
			return sprite
	for sprite in sprites['on']:
		if sprite in Sprite_Group:
			return sprite
	return False

	
def collision(a, b, sprite): 		# returns if (a,b) (relative to top left of floor) is in sprite,
	(w,z) = (a - sprite.a + sprite.rect.width//2, b - sprite.b + sprite.rect.height)
	try:
		return sprite.mask.get_at((w,z))
	except:
		return False
		
# ------- Convenient Methods ---------#

def on_floor(self):
	if is_object_nearby(self,Solid_Object_Group, onBottom):
		return True 
	return False
	
def is_any_member_of_list_in_group(list,group):
	for i in list:
		if i in group:
			return i
	return False

# -------------------------------------------- # 
# ------------------ Timer ----------------- # 
# -------------------------------------------- # 

class Timer(pygame.sprite.Sprite):
	
	def __init__(self):
		super().__init__()
		# for gameover
		self.gameover_time = 0
		self.GAMEOVER_WAIT_TIME = 120
		# for character
		self.fall_off_screen_time = 0
		self.FALL_OFF_SCREEN_WAIT_TIME = 20
		self.sprite_death_time = 0
		self.SPRITE_DIES_WAIT_TIME 	= 70
		self.time_since_damage = 0
		# for player
		self.portal_time = 0
		self.PORTAL_WAIT_TIME = 80
		self.death_freeze_time = 0
		self.DEATH_FREEZE_WAIT_TIME = 4
		self.spike_time = 0
		self.SPIKE_WAIT_TIME = 60
		# for enemies
		self.motion_time = 0 
		self.LEFT_RIGHT_TIME = 70
		self.WAIT_TIME = 20
		self.DIE_TIME = 20
		
	def gameover_timer(self,WAIT_TIME):
		self.gameover_time += 1
		if self.gameover_time > WAIT_TIME:
			self.gameover_time = 0
			return True
		return False
		
	def fall_off_screen_timer(self,WAIT_TIME):
		self.fall_off_screen_time += 1
		if self.fall_off_screen_time > WAIT_TIME:
			self.fall_off_screen_time = 0
			return True
		return False
		
	def sprite_death_timer(self,WAIT_TIME):
		self.sprite_death_time += 1
		if self.sprite_death_time > WAIT_TIME:
			self.sprite_death_time = 0
			return True
		return False
		
	def death_freeze_timer(self,WAIT_TIME):
		self.death_freeze_time += 1
		if self.death_freeze_time > WAIT_TIME:
			self.death_freeze_time = 0
			return True
		return False
		
	def portal_timer(self,WAIT_TIME):
		self.portal_time += 1
		if self.portal_time > WAIT_TIME:
			self.portal_time = 0
			return True
		return False
		
	def spike_timer(self,WAIT_TIME):
		self.spike_time += 1
		if self.spike_time > WAIT_TIME:
			self.spike_time = 0
			return True
		return False

	def motion_timer(self,WAIT_TIME):
		self.motion_time += 1
		if self.motion_time > WAIT_TIME:
			self.motion_time = 0
			return True
		return False
		
	def timer_since_damaged(self,WAIT_TIME):
		self.time_since_damage += 1
		if self.time_since_damage > WAIT_TIME:
			self.time_since_damage = 0
			return True
		return False
		
		
		
# -------------------------------------------- # 
# ------------------ SPRITES ----------------- # 
# -------------------------------------------- # 

class Floors(pygame.sprite.Sprite):	
						
	def __init__(self,level_filepath):
		super().__init__()
		self.image = pygame.image.load(level_filepath)
		self.mask = pygame.mask.from_surface(self.image)
		self.rect = self.image.get_rect()
		self.a, self.b = self.rect.midbottom
		(self.FLOORWIDTH,self.FLOORHEIGHT) = self.rect.size
		Floor_Group.add(self)
		Solid_Object_Group.add(self)
		Left_Wall = self.Sidewall('left',self.FLOORWIDTH,self.FLOORHEIGHT)
		Right_Wall = self.Sidewall('right',self.FLOORWIDTH,self.FLOORHEIGHT)
		
		# ------- Initial Attributes -------- #
		self.rect.bottomleft = (0,WINDOWHEIGHT)
		self.offsetx = -self.rect.left
		self.offsety = -self.rect.top
		self.GRAVITY = 1.2
			
	def update_offset(self):
		self.offsetx = -self.rect.left
		self.offsety = -self.rect.top
		
	def BG_scroll(self):		
		if P1.near_floor_edge_horiz() == 2:
			self.rect.left = WINDOWWIDTH//2 - P1.a
		if P1.near_floor_edge_horiz() == 1:
			self.rect.left = 0
		elif P1.near_floor_edge_horiz() == 3:
			self.rect.right = WINDOWWIDTH
		if P1.near_floor_edge_vert() == 1:
			self.rect.top = WINDOWHEIGHT//2 - (P1.b - P1.SPRITEHEIGHT//2) 
		if P1.near_floor_edge_vert() == 2:
			self.rect.bottom = WINDOWHEIGHT
			
	class Sidewall(pygame.sprite.Sprite):		

		def __init__(self,side,floorwidth,floorheight):				
			super().__init__()	
			self.image = pygame.Surface((100,floorheight))
			self.image.fill(NAVYBLUE)
			self.rect = self.image.get_rect()
			if side == 'left':
				self.a, self.b = -50, floorheight
			elif side == 'right':
				self.a, self.b = floorwidth+50, floorheight
			self.mask = pygame.mask.from_surface(self.image)
			Solid_Object_Group.add(self)
			Floor_Group.add(self)

	
# -------------------------------------------- # 
		
class Ladder(pygame.sprite.Sprite):		

	def __init__(self, a, b):				# (a,b) is coords of midbottom of 
		super().__init__()					# ladder relative to topleft of floor
		ladder = pygame.image.load('Images/ladder/ladder.png')
		self.image = pygame.transform.scale(ladder,(40,200))
		self.rect  = self.image.get_rect()
		self.rect.midbottom = floor_coords_to_screen_coords(a,b)
		self.mask = pygame.mask.from_surface(self.image)
		self.a, self.b = a, b
		Ladder_Group.add(self)
		self.SPRITEWIDTH, self.SPRITEHEIGHT = self.rect.size
		
# -------------------------------------------- # 

class Life(pygame.sprite.Sprite):		

	def __init__(self, a, b):				# (a,b) is coords of midbottom of 
		super().__init__()					# ladder relative to topleft of floor
		life = pygame.image.load('Images/hearts/heart_full.png')
		self.image = pygame.transform.scale(life,(30,30))
		self.rect  = self.image.get_rect()
		self.rect.midbottom = floor_coords_to_screen_coords(a,b)
		self.mask = pygame.mask.from_surface(self.image)
		self.a, self.b = a, b
		Life_Group.add(self)
		self.SPRITEWIDTH, self.SPRITEHEIGHT = self.rect.size
		
# -------------------------------------------- # 
		
class Spike(pygame.sprite.Sprite):		

	def __init__(self, a, b, spike_points_where):		# (a,b) is coords of midbottom of spike relative to 
		super().__init__()					# topleft of floor
		spike = pygame.image.load('Images/spike/spike.png')
		self.image = pygame.transform.scale(spike,(100,50))
		Spike_Group.add(self)
		Solid_Object_Group.add(self)
		self.direction = spike_points_where
		if spike_points_where == 'left':
			self.image = pygame.transform.rotate(self.image,90)
			Left_Spike_Group.add(self)
		elif spike_points_where == 'right':
			self.image = pygame.transform.rotate(self.image,-90)
			Right_Spike_Group.add(self)
		elif spike_points_where == 'down':
			self.image = pygame.transform.rotate(self.image,180)
			Down_Spike_Group.add(self)
		else:
			Up_Spike_Group.add(self)
		self.rect  = self.image.get_rect()
		self.mask = pygame.mask.from_surface(self.image)
		self.rect.midbottom = floor_coords_to_screen_coords(a,b)
		self.a, self.b = a, b
		self.SPRITEWIDTH, self.SPRITEHEIGHT = self.rect.size
		self.PUSH_SPEED_X, self.PUSH_SPEED_Y = 10, 14
	
# -------------------------------------------- # 
class Portal(pygame.sprite.Sprite):		
# ---------- Presets ---------------- #
	SPRITEWIDTH, SPRITEHEIGHT = 80,70
	sprite_list = ['Images/portal/portal1.png', 'Images/portal/portal2.png', 'Images/portal/portal3.png'] 		# Images to animate Sprite
# ----------------------------------- #
	def __init__(self, a, b):		# (a,b) is coords of midbottom of 
		super().__init__()					# ladder relative to topleft of floor
		self.images = []
		self.num_images = len(self.sprite_list)
		for i, sprite in enumerate(self.sprite_list):
			self.images.append(pygame.image.load(sprite))
			self.images[i] = pygame.transform.scale(self.images[i], (self.SPRITEWIDTH,self.SPRITEHEIGHT))
		self.image = self.images[0]
		self.rect  = self.image.get_rect()
		self.mask = pygame.mask.from_surface(self.image)
		self.rect.midbottom = floor_coords_to_screen_coords(a,b)
		self.a, self.b = a, b
		Portal_Group.add(self)
		
# ------------ Animate Trampoline --------------- # 
	def set_sprite_image(self):
		sprite_num = int((pygame.time.get_ticks()//100) % self.num_images)
		self.image = self.images[sprite_num]

class Trampoline(pygame.sprite.Sprite):		
# ---------- Presets ---------------- #
	bounce_ratio = 0.7
	bounce_power = 25
	SPRITEWIDTH, SPRITEHEIGHT = 80,50
	sprite_list = ['Images/trampoline/trampoline1.png', 'Images/trampoline/trampoline2.png'] 		# Images to animate Sprite
# ----------------------------------- #
	def __init__(self, a, b, angle):		# (a,b) is coords of midbottom of 
		super().__init__()					# ladder relative to topleft of floor, angle in rad
		self.images = []
		self.num_images = len(self.sprite_list)
		for i, sprite in enumerate(self.sprite_list):
			self.images.append(pygame.image.load(sprite))
			self.images[i] = pygame.transform.scale(self.images[i], (self.SPRITEWIDTH,self.SPRITEHEIGHT))
			self.images[i] = pygame.transform.rotate(self.images[i],angle*180/math.pi)
		self.image = self.images[0]
		self.sprite_number = 0
		self.frames_since_sprite_change = 0
		self.rect  = self.image.get_rect()
		self.rect.midbottom = floor_coords_to_screen_coords(a,b)
		self.mask = pygame.mask.from_surface(self.images[1])
		self.a, self.b, self.angle = a, b, angle
		Trampoline_Group.add(self)
		Solid_Object_Group.add(self)
		Bounce_Group.add(self)
		
		
# ------------ Animate Trampoline --------------- # 
	def set_image_to_sprite_number(self):
		for i in range(self.num_images):
			if self.sprite_number == i:
				self.image = self.images[i]
				return	
				
	def set_sprite_number(self):
		FRAMES_TILL_CHANGE_BACK = 5
		if self.sprite_number == 1:
			self.frames_since_sprite_change += 1
			if self.frames_since_sprite_change > FRAMES_TILL_CHANGE_BACK:
				self.sprite_number = 0
				self.frames_since_sprite_change = 0
		if what_sprite_nearby(P1,Trampoline_Group,onBottom) == self:
			self.sprite_number = 1
		
	def set_sprite_image(self):
		self.set_sprite_number()
		self.set_image_to_sprite_number()
			
# -------------------------------------------- # 

class Character(pygame.sprite.Sprite):

##### NOTE EVERY SUBCLASS MUST HAVE A PROGRAM FOR SET_MOTION_LIST, PERFORM_PROTOCOLS, DAMAGE, POSITION_HEARTS
	# ---------- Presets ---------------- #
	FRICTION = 1.5
	AIR_RESISTANCE = 1#0.05
# ----------------------------------- #
	def __init__(self):
		super().__init__()
		self.orig_images = []
		self.num_images = len(self.sprite_list)
		for i, sprite in enumerate(self.sprite_list):
			self.orig_images.append(pygame.image.load(sprite))
			self.orig_images[i] = pygame.transform.scale(self.orig_images[i], (self.SPRITEWIDTH,self.SPRITEHEIGHT))
		self.images = self.orig_images[:]
		self.image = self.images[0]
		self.sprite_number = 0
		self.rect  = self.image.get_rect()				
		self.mask = pygame.mask.from_surface(self.image)
		self.timer = Timer()
		# ----- Initial Attributes -------	#	
		self.v_x, self.v_y = 0, 0		
		self.prev_direct = 'right'
		self.direct = 'right'
		self.step_count_since_sprite_change = 0
		self.damaged = 'no'
		self.fall_off_screen_timer = 0
		self.motion = ['']
		self.hearts_image = pygame.Surface((0,0))
		self.freeze_time = 0
		
# ---------- Drawer -----------	#	

	def draw_character(self):
		DISPLAYSURF.blit(self.image,self.rect)
		
	def draw_hearts(self):
		DISPLAYSURF.blit(self.hearts_image,self.hearts_rect)
		
# ---------- Senses Location -----------	#	
		
	def falloffScreen(self):
		return self.b > Floor.FLOORHEIGHT

# -------------- Sense Nearby Objects --------------- # 	
	def near_floor_edge_horiz(self):		
		if 	(Floor.FLOORWIDTH - self.a) <= WINDOWWIDTH//2:
			return 3					# returns 3 if next to right edge (floor fixed, player moves)
		elif self.a <= WINDOWWIDTH//2:
			return 1					# returns 1 if next to left edge (floor fixed, player moves)
		else:		
			return 2					# returns 2 if not near an edge (floor moves, player fixed)
		
	def near_floor_edge_vert(self):		
		if (Floor.FLOORHEIGHT - (self.b - self.rect.height//2 )) <= WINDOWHEIGHT//2:
			return 2					# returns 2 if next to bottom edge (floor fixed, player moves)			# returns 1 if next to top edge (floor fixed, player moves)
		else:		
			return 1					# returns 1 if not near an edge (floor moves, player fixed)	
				
	def sense_spikes(self):
		up = is_any_member_of_list_in_group(self.below['in']+self.below['on']+self.left['in']+self.left['on']+\
			self.right['in']+self.right['on'], Up_Spike_Group)
		if up != False:
			return up
		down = is_any_member_of_list_in_group(self.above['in']+self.above['on']+self.left['in']+self.left['on']+\
			self.right['in']+self.right['on'], Down_Spike_Group)
		if down != False:
			return down
		right = is_any_member_of_list_in_group(self.below['in']+self.below['on']+self.left['in']+self.left['on']+\
			self.above['in']+self.above['on'], Right_Spike_Group)
		if right != False:
			return right
		left = is_any_member_of_list_in_group(self.below['in']+self.below['on']+self.above['in']+self.above['on']+\
			self.right['in']+self.right['on'], Left_Spike_Group)
		return left
		
	def in_portal(self):
		return is_object_nearby(self, Portal_Group, onBottom) and is_object_nearby(self, Portal_Group, onLeft) and is_object_nearby(self,Portal_Group, onRight)
		
	def touch_solid_object(self):
		return is_any_member_of_list_in_group(self.below['in']+self.below['on']+self.above['in']+self.above['on']+\
		self.left['in']+self.left['on']+self.right['in']+self.right['on'], Solid_Object_Group)
		
	def hit_by_enemy(self):
		return is_any_member_of_list_in_group(self.above['in']+self.above['on']+self.left['in']+self.left['on']+\
			self.right['in']+self.right['on'], Enemy_Group)
				
	def player_bounce_on_top(self):
		return self in P1.below['in']+P1.below['on']

# -------- Motion Resistances -------- #		
			
	def decrease_speed(self,STRENGTH):
		if abs(self.v_x) < STRENGTH:
			self.v_x = 0
		elif self.v_x > 0:
			self.v_x -= STRENGTH
		elif self.v_x < 0:
			self.v_x += STRENGTH
			
# --------- Defaults ---------------------- # 
			
	def bounce_defaults(self,bouncy_obj):					# if bouncy object doesn't have angle or bounce power attributes
		try:
			t = bouncy_obj.angle
		except:
			t = 0
		try:
			e = bouncy_obj.bounce_ratio
		except:
			e = 1.2
		try:
			bounce_power = bouncy_obj.bounce_power
		except:
			bounce_power = self.JUMPPOWER
		return t, e, bounce_power
	
# --------- Protocols ---------------------- # 
		
	def ladder_protocol(self):
			if 'left' in self.motion[0]:						
				self.v_x = -self.LADDER_SPEED
				self.direct = 'left'	
			elif 'right' in self.motion[0]:					
				self.v_x = self.LADDER_SPEED
				self.direct = 'right'
			else: 
				self.v_x = 0
			if 'up' in self.motion[0]:
				self.v_y = -self.LADDER_SPEED
			elif 'down' in self.motion[0]:
				self.v_y = self.LADDER_SPEED
			else:
				self.v_y = 0
				
	def life_protocol(self,life_obj):
		if self.LIVES == self.MAXLIVES:
			pass
		elif self.LIVES < self.MAXLIVES:
			life_obj.kill()
			self.LIVES += 1
		
	def bounce_protocol(self,bouncy_obj):
		self.default_left_right_movement(self.FRICTION)
		t, e, bounce_power = self.bounce_defaults(bouncy_obj)
		if 'up' in self.motion[0]:
			self.v_x, self.v_y = -bounce_power*sin(t) ,-bounce_power*cos(t)
		else:
			if abs(self.v_y) > 10:
				self.v_x, self.v_y = self.v_x*(-e*sin(t)**2+ cos(t)**2) - self.v_y*(e+1)*sin(t)*cos(t), \
													-self.v_x*(e+1)*sin(t)*cos(t) + self.v_y*(-e*cos(t)**2+ sin(t)**2)
			else:	
				self.v_y = 0
	
	def solid_object_protocol(self):
		if (self.left['in']+self.left['on']+self.right['in']+self.right['on']) in Solid_Object_Group:		
			self.v_x = 0
		if (self.above['in']+self.above['on']+self.below['in']+self.below['on']) in Solid_Object_Group:
			self.v_y = 0
		self.default_left_right_movement(self.FRICTION)
		if is_any_member_of_list_in_group(self.below['on'], Solid_Object_Group):
			if 'up' in self.motion[0]:
				self.v_y = -self.JUMPPOWER
		else:
			self.v_y += Floor.GRAVITY
		if on_floor(self):
			self.last_safe_loc = self.a,self.b
			
	def air_protocol(self):
		self.default_left_right_movement(self.AIR_RESISTANCE)
		self.v_y += Floor.GRAVITY
		
	def portal_protocol(self):
		global CHANGE_SCREEN_TO, CURRENT_LEVEL
		self.v_x, self.v_y = 0,0
		if self.timer.portal_timer(self.timer.PORTAL_WAIT_TIME):
			new_level = CURRENT_LEVEL + 1
			CHANGE_SCREEN_TO = 'level' + str(new_level)
			
	def enemy_protocol(self):
		if self.left['in']+self.left['on'] in Enemy_Group:
			self.v_x = self.ENEMY_PUSH_SPEED_X
			self.v_y = -self.ENEMY_PUSH_SPEED_Y
		elif self.right['in']+self.right['on'] in Enemy_Group:
			self.v_x = -self.ENEMY_PUSH_SPEED_X
			self.v_y = -self.ENEMY_PUSH_SPEED_Y
		elif self.above['in']+self.above['on'] in Enemy_Group:
			self.v_y = self.ENEMY_PUSH_SPEED_Y
			
	def spike_protocol(self,spike_obj):
		if self.left['in']+self.left['on'] in Spike_Group:
			self.v_x = spike_obj.PUSH_SPEED_X
			self.v_y = -spike_obj.PUSH_SPEED_Y
		elif self.right['in']+self.right['on'] in Spike_Group:
			self.v_x = -spike_obj.PUSH_SPEED_X
			self.v_y = -spike_obj.PUSH_SPEED_Y
		elif self.above['in']+self.above['on'] in Spike_Group:
			self.v_y = spike_obj.PUSH_SPEED_Y
		elif self.below['in']+self.below['on'] in Spike_Group:
			self.v_y = -spike_obj.PUSH_SPEED_Y
			
	def default_left_right_movement(self,resistance):
		if 'left' in self.motion[0]:						# perform_protocols left
			self.direct = 'left'
			if self.v_x > -self.MAXSPEED:
				self.v_x -= self.SIDE_ACCELERATION	
		elif 'right' in self.motion[0]:						# perform_protocols right
			self.direct = 'right'
			if self.v_x < self.MAXSPEED:	
				self.v_x += self.SIDE_ACCELERATION
		else:											# resistances to motion
				self.decrease_speed(resistance)
			
			
	def to_last_safe_loc_protocol(self):
		if self.damaged == 'yes_spike':
			if self.timer.spike_timer(self.timer.SPIKE_WAIT_TIME):
				if self.last_safe_loc == self.last_safe_loc_before_damage:
					self.v_x, self.v_y = 0, 0
					self.a,self.b = self.last_safe_loc
					self.freeze_time = 40
		elif self.damaged == 'yes_off_screen':
			if self.timer.fall_off_screen_timer(self.timer.FALL_OFF_SCREEN_WAIT_TIME):
				self.v_x, self.v_y = 0, 0
				self.a,self.b = self.last_safe_loc
				self.freeze_time = 40
		else:
			self.timer.spike_time = 0
			
			

# --------- KEY BUNDLES ------------#	

	def troubleshoot(self):
	
		def exit_barrier_soft(self):					# leaves barrier if one sensor is in barrier
			while is_object_nearby(self,Solid_Object_Group,onBottom) == 'in':
				self.b -= 1
			while is_object_nearby(self,Solid_Object_Group,onRight) == 'in':
				self.a -= 1
			while is_object_nearby(self,Solid_Object_Group,onLeft) == 'in':
				self.a += 1
			while is_object_nearby(self,Solid_Object_Group,onTop) == 'in':
				self.b += 1

			
		def exit_barrier_hard(self):					# leaves barrier if 2 sensors are in barrier
			while int(is_object_nearby(self,Solid_Object_Group,onBottom)=='in') + \
					int(is_object_nearby(self,Solid_Object_Group,onLeft)=='in') + \
					int(is_object_nearby(self,Solid_Object_Group,onRight)=='in') + \
					int(is_object_nearby(self,Solid_Object_Group,onTop)=='in') > 1:
				if abs(self.v_x) > abs(self.v_y):				# significant speed is in x dir
					self.a -= int((self.v_x)/abs(self.v_x))
					self.b -= round(self.v_y/self.v_x)
				elif abs(self.v_x) < abs(self.v_y):				# significant speed is in y dir
					self.b -= int((self.v_y)/abs(self.v_y))
					self.a -= round(self.v_x/self.v_y)
				else:
					self.b -= 1
					
		exit_barrier_hard(self)
		exit_barrier_soft(self)
	
	def update_attributes(self):
	
		def update_rect_and_mask(self):
			self.rect = self.image.get_rect()
			self.rect.midbottom = floor_coords_to_screen_coords(self.a, self.b)
			self.mask = pygame.mask.from_surface((self.image))
	
		def sense_nearby_objects(self):
			self.above = onTop(self)
			self.below = onBottom(self)
			self.left  = onLeft(self)
			self.right = onRight(self)
			self.center = inMiddle(self)
	
		def damage_recovery(self):
			player_recovery_time_from_spike  = 50
			player_recovery_time_from_enemy  = 40
			enemy_recovery_time_from_player_on_top  = 20
			if self.damaged == 'yes_spike':
				if self.timer.timer_since_damaged(player_recovery_time_from_spike):
					self.damaged = 'no'
			elif self.damaged == 'yes_enemy':
				if self.timer.timer_since_damaged(player_recovery_time_from_enemy):
					self.damaged = 'no'
			elif self.damaged == 'yes_player_on_top':
				if self.timer.timer_since_damaged(enemy_recovery_time_from_player_on_top):
					self.damaged = 'no'
				
		def update_lives(self):
			if 'yes' in self.damaged and self.timer.time_since_damage == 1:
				self.LIVES -= 1	
		
		update_rect_and_mask(self)
		sense_nearby_objects(self)
		damage_recovery(self)
		update_lives(self)
			
			
	def set_sprite_image(self):			# DETERMINES WHICH SPRITE TO USE
	
		def shrink_into_portal(self):
			time_in_portal = self.timer.portal_time
			if self.timer.portal_time < self.timer.PORTAL_WAIT_TIME:
				scalefactor = (self.timer.PORTAL_WAIT_TIME - time_in_portal)/self.timer.PORTAL_WAIT_TIME
				for i in range(self.num_images):
					self.images[i] = pygame.transform.scale(self.orig_images[i], (int(scalefactor*self.SPRITEWIDTH),int(scalefactor*self.SPRITEHEIGHT)))
			self.rect = self.image.get_rect()

		
		def direction(self):
			change_dir = (self.prev_direct != self.direct)
			self.prev_direct = self.direct
			if change_dir:
				for i in range(self.num_images):
					self.images[i] = pygame.transform.flip(self.images[i], True, False)
			
		def set_image_to_sprite_number(self):
			for i in range(self.num_images):
				if self.sprite_number == i:
					self.image = self.images[i]
			
		def change_sprite(self):
			CHANGE_AT = 8
			self.step_count_since_sprite_change += abs(self.v_x) //4
			if self.step_count_since_sprite_change > CHANGE_AT:
				self.sprite_number = (self.sprite_number + 1) % self.num_images
				set_image_to_sprite_number(self)
				self.step_count_since_sprite_change = 0
			else:
				set_image_to_sprite_number(self)
			
		def blinking_damaged_sprite(self):
			if (self.timer.time_since_damage//5) % 2 == 0:
				set_image_to_sprite_number(self)
			else:
				self.image = pygame.Surface((self.SPRITEWIDTH,self.SPRITEHEIGHT))	
				
		def health_hearts(self):
			hearts_image = pygame.Surface(((self.MAXLIVES-1)*self.HEARTSPACE+self.HEARTWIDTH,self.HEARTHEIGHT))
			for i in range(self.MAXLIVES):
				if i < self.LIVES:
					heart_image = pygame.transform.scale(pygame.image.load('Images/hearts/heart_full.png'),(self.HEARTWIDTH,self.HEARTHEIGHT))
				else:
					heart_image = pygame.transform.scale(pygame.image.load('Images/hearts/heart_empty.png'),(self.HEARTWIDTH,self.HEARTHEIGHT))
				hearts_image.blit(heart_image,(self.HEARTSPACE*i,0))
			self.hearts_image = hearts_image
	
		direction(self)
		change_sprite(self)
		blinking_damaged_sprite(self)
		health_hearts(self)
		self.position_hearts()
		if self.in_portal():
			shrink_into_portal(self)

		
		
	def update_speed_and_loc(self):
		
		def freeze_motion(self):
			if self.freeze_time > 0:
				self.v_x,self.v_y = 0,0
				self.freeze_time -= 1
		
		def update_loc(self):
			self.a += int(self.v_x)
			self.b += int(self.v_y)
			
		self.perform_protocols()
		self.damage()
		freeze_motion(self)
		update_loc(self)
		
#------------ BUNDLE EVERYTHING ------------#		
	
	def character_motion_bundle(self):
		self.set_motion_list()
		self.update_attributes()
		self.update_speed_and_loc()
		self.troubleshoot()

			
#--------------------------------#



class Player(Character):
	
# ---------- Presets ---------------- #
	sprite_list = ['Images/cat/cat1.png', 'Images/cat/cat2.png', 'Images/cat/cat3.png']
	MAXSPEED = 12
	SIDE_ACCELERATION = 2
	JUMPPOWER = 18
	LADDER_SPEED = 5
	ENEMY_PUSH_SPEED_X = 10		# After collision with enemy, these 
	ENEMY_PUSH_SPEED_Y = 14		# speeds say how fast player pushed away
	MAXLIVES = 5
	SPRITEWIDTH,SPRITEHEIGHT = 50,42
	HEARTWIDTH, HEARTHEIGHT, HEARTSPACE = 30,30,45
# ----------------------------------- #
	def __init__(self,a,b):
		super().__init__()
		self.INITIAL_LOC = a,b
		self.a, self.b = self.INITIAL_LOC
		self.LIVES = self.MAXLIVES
		self.death_freeze_timer = 0
		self.sprite_death_timer = 0
		self.gameover_timer = 0
		self.last_safe_loc = self.INITIAL_LOC
		self.dead = 'no'
		self.last_safe_loc_before_damage = self.INITIAL_LOC
		Player_Group.add(self)
		
	
# -------------- REQUIRED FUNCTIONS ------------- # 	

	def set_motion_list(self):
		pressed_keys = pygame.key.get_pressed()
		self.motion = ['']
		if pressed_keys[K_LEFT] and not pressed_keys[K_RIGHT]:
			self.motion[0] += 'left_'
		if not pressed_keys[K_LEFT] and  pressed_keys[K_RIGHT]:
			self.motion[0] += 'right_'
		if pressed_keys[K_UP] and not pressed_keys[K_DOWN]:
			self.motion[0] += '_up'
		if not pressed_keys[K_UP] and  pressed_keys[K_DOWN]:
			self.motion[0] += '_down'

		
	def perform_protocols(self):
		if self.LIVES <= 0:
			self.death()
		elif is_any_member_of_list_in_group(self.center['in'], Life_Group):
			life_obj = what_sprite_nearby(self,Life_Group,inMiddle)
			self.life_protocol(life_obj)
		elif self.in_portal():
			self.portal_protocol()
		elif self.sense_spikes():
			spike_obj = self.sense_spikes()
			self.spike_protocol(spike_obj)
		elif self.hit_by_enemy():
			self.enemy_protocol()
		elif pygame.sprite.spritecollideany(self,Ladder_Group):
			self.ladder_protocol()
		elif is_any_member_of_list_in_group(self.below['in']+self.below['on'], Bounce_Group):
			bouncy_obj = what_sprite_nearby(self,Bounce_Group,onBottom)
			self.bounce_protocol(bouncy_obj)
		elif self.touch_solid_object():
			self.solid_object_protocol()
		else:
			self.air_protocol()
		self.to_last_safe_loc_protocol()
			
	def damage(self):
		if self.falloffScreen():
			self.damaged = 'yes_off_screen'
		elif self.sense_spikes():
			self.damaged = 'yes_spike'
			self.last_safe_loc_before_damage = self.last_safe_loc
			if self.timer.time_since_damage > 1: 		# ensures we remain damaged if we keep bouncing on spikes
				self.timer.time_since_damage = 2
		elif self.hit_by_enemy():
			enemy = self.hit_by_enemy()
			if enemy.damaged == 'no':
				self.damaged = 'yes_enemy'
			
	def position_hearts(self):
		self.hearts_rect = self.hearts_image.get_rect()
		self.hearts_rect.topleft = (30,30)
		
# --------- GAME OVER ------------#

	def death(self):
		global CHANGE_SCREEN_TO
		self.damaged = 'yes'
		if self.timer.death_freeze_timer(self.timer.DEATH_FREEZE_WAIT_TIME):
			self.freeze_time = 1000
		if self.timer.sprite_death_timer(self.timer.SPRITE_DIES_WAIT_TIME):
			self.TIME_OF_PLAYER_DEATH = pygame.time.get_ticks()/1000
			CHANGE_SCREEN_TO = 'gameover'
			self.kill()
	
		
# -------------------------------------------- # 
class Enemy(Character):
# Movement Type 1 is jump up and down
# Movement Type 2 is jump to left and right
# Movement Type 3 is run left and right

# ---------- Presets ---------------- #
	sprite_list = ['Images/mouse/mouse2.png', 'Images/mouse/mouse1.png'] 		# Images to animate Sprite
	FRICTION = 1.5
	AIR_RESISTANCE = 0.05
	MAXSPEED = 12
	SIDE_ACCELERATION = 3
	JUMPPOWER = 13
	bounce_ratio = 1.05
	MAXLIVES = 1
	SPRITEWIDTH,SPRITEHEIGHT = 60,30
	HEARTWIDTH, HEARTHEIGHT, HEARTSPACE = 10, 10, 15
	
	
# ----------------------------------- #
	def __init__(self,a,b,movement_type):
		super().__init__()
		self.INITIAL_LOC = a,b
		# ----- Initial Attributes -------	#	
		self.a, self.b = self.INITIAL_LOC
		self.motion_timer = 0
		self.death_timer = 0
		self.LIVES = self.MAXLIVES
		# ----- Groups   ------ #
		Solid_Object_Group.add(self)
		Bounce_Group.add(self)
		Enemy_Group.add(self)
		# ----- Motion List -------	#
		if movement_type == 1:
			self.motion = ['up', 'floor', 'wait']
		elif movement_type == 2:
			self.motion = [ 'wait', 'up', 'right_floor','wait', 'up', 'left_floor']
		elif movement_type == 3:
			self.motion = ['right_time', 'wait', 'left_time', 'wait']
		
# -------------- REQUIRED FUNCTIONS --------------- # 
	
	def set_motion_list(self):				# Automates motion for enemy
	
		def next_on_list(self):
			self.motion.append(self.motion.pop(0))
			
		if 'up' in self.motion[0]:
			next_on_list(self)
		elif self.motion[0] == 'left_time' or self.motion[0] == 'right_time':
			if self.timer.motion_timer(self.timer.LEFT_RIGHT_TIME):
				next_on_list(self)
		elif self.motion[0] == 'wait':
			if self.timer.motion_timer(self.timer.WAIT_TIME):
				next_on_list(self)
		elif 'floor' in self.motion[0]:
			if on_floor(self):
				next_on_list(self)
		
		
	def perform_protocols(self):		
		if self.LIVES == 0:
			Bounce_Group.remove(self)
			if self.timer.sprite_death_timer(self.timer.DIE_TIME):
				self.kill()
		if self.touch_solid_object():
			self.solid_object_protocol()
		else:
			self.air_protocol()
			
	def damage(self):
		if self.player_bounce_on_top():
			self.damaged = 'yes_player_on_top'
			
	def position_hearts(self):
		self.hearts_rect = self.hearts_image.get_rect()
		Floor.update_offset()
		(x,y) = floor_coords_to_screen_coords(self.a,self.b)
		self.hearts_rect.midbottom = (x,y-self.SPRITEHEIGHT-20)
		if self.damaged == 'no':
			self.hearts_image = pygame.Surface((0,0))
	
# -------------------------------------------- # 


	
# -------------------------------------------- # 
#			WORLD FUNCTION BUNDLES			   #
# -------------------------------------------- # 


def update_world():
	change_level()
	Floor.update_offset()
	for player in Player_Group:
		player.character_motion_bundle()
	for enemy in Enemy_Group:
		enemy.character_motion_bundle()
	
def set_sprites():
	for trampoline in Trampoline_Group:
		trampoline.set_sprite_image()
	for portal in Portal_Group:
		portal.set_sprite_image()
	for player in Player_Group:
		player.set_sprite_image()
	for enemy in Enemy_Group:
		enemy.set_sprite_image()
	
	
def move_world():
	Floor.BG_scroll()
	for ladder in Ladder_Group:
		scroll_with_BG(ladder)
	for trampoline in Trampoline_Group:
		scroll_with_BG(trampoline)
	for enemy in Enemy_Group:
		scroll_with_BG(enemy)
	for spike in Spike_Group:
		scroll_with_BG(spike)
	for life in Life_Group:
		scroll_with_BG(life)
	for portal in Portal_Group:
		scroll_with_BG(portal)
	for thing in Floor_Group:
		scroll_with_BG(thing)
	for player in Player_Group:
		scroll_with_BG(player)
	
def draw_world():
	global CHANGE_SCREEN_TO
	DISPLAYSURF.blit(BG,(0,0,WINDOWWIDTH,WINDOWHEIGHT))
	Floor_Group.draw(DISPLAYSURF)
	Ladder_Group.draw(DISPLAYSURF)
	Trampoline_Group.draw(DISPLAYSURF)
	Spike_Group.draw(DISPLAYSURF)
	Life_Group.draw(DISPLAYSURF)
	Portal_Group.draw(DISPLAYSURF)
	Enemy_Group.draw(DISPLAYSURF)
	for enemy in Enemy_Group:
		enemy.draw_hearts()
	Player_Group.draw(DISPLAYSURF)
	for player in Player_Group:
		player.draw_hearts()
	if CHANGE_SCREEN_TO == 'gameover':
		draw_gameover()	
	

	

# -------------- GROUP DEFITNITIONS ------------------ # 
# GROUP BY OBJECT #
Floor_Group = pygame.sprite.Group()					# Floor sprites
Ladder_Group = pygame.sprite.Group()				# Ladder sprites
Trampoline_Group = pygame.sprite.Group()			# Trampoline sprites
Enemy_Group =  pygame.sprite.Group()				# Enemy sprites
Spike_Group = pygame.sprite.Group()					# Spike sprites
Player_Group = pygame.sprite.Group()				# Player sprite
Portal_Group = pygame.sprite.Group()				# Portal sprites
Life_Group = pygame.sprite.Group()					# Life sprites

# GROUP BY PROPERTY #
Bounce_Group = pygame.sprite.Group()				# Bouncy sprites
Solid_Object_Group = pygame.sprite.Group()			# Sprites you cannot enter
Up_Spike_Group =  pygame.sprite.Group()				# Spike sprites pointing left
Right_Spike_Group =  pygame.sprite.Group()			# Spike sprites pointing right
Left_Spike_Group =  pygame.sprite.Group()			# Spike sprites pointing up
Down_Spike_Group =  pygame.sprite.Group()			# Spike sprites pointing down

Group_List = [	Floor_Group, Ladder_Group, Trampoline_Group, Enemy_Group, Spike_Group,
				Portal_Group, Life_Group, Bounce_Group, Solid_Object_Group, 
				Up_Spike_Group, Right_Spike_Group, Left_Spike_Group, Down_Spike_Group]
# ----------------	 Changing Level	----------------- # 

def change_level():
	global CHANGE_SCREEN_TO, CURRENT_LEVEL, Interactable_sprites_dict
	if CHANGE_SCREEN_TO == 'level1':
		CHANGE_SCREEN_TO = ''
		CURRENT_LEVEL 	 = 1 
		prepare_for_next_level()
		Level1()
	elif CHANGE_SCREEN_TO == 'level2':
		CHANGE_SCREEN_TO = ''
		CURRENT_LEVEL 	 = 2
		prepare_for_next_level()
		Level2()
	elif CHANGE_SCREEN_TO == 'level3':
		CHANGE_SCREEN_TO = ''
		CURRENT_LEVEL 	 = 3
		prepare_for_next_level()
		Level3()

	Interactable_sprites_dict = {	'Floor': 				Floor_Group,		# EVERY INTERACTABLE NON PLAYER SPRITE MUST BE HERE
									'Ladders':				Ladder_Group,
									'Trampolines':			Trampoline_Group,
									'Enemies':				Enemy_Group,				
									'Spikes':				Spike_Group,
									'Portals':				Portal_Group,	
									'Lives':				Life_Group			}
					
# ----------------	 Gameover	----------------- # 
def draw_gameover():
	if (pygame.time.get_ticks()//1000 - P1.TIME_OF_PLAYER_DEATH) > 1:
		gameover_image = pygame.image.load('Images/gameover/gameover.png')
		gameover_rect = gameover_image.get_rect()
		gameover_rect.center = (WINDOWWIDTH//2,WINDOWHEIGHT//2)
		DISPLAYSURF.blit(gameover_image,gameover_rect)
		
# ----------------	 Clear Level	----------------- # 
def prepare_for_next_level():
	for group in Group_List:
		group.empty()
	P1.images = P1.orig_images[:]
	P1.prev_direct = 'right'
	P1.direct = 'right'
# ----------------	 Level 1 	----------------- # 
def Level1():
	global Floor, P1, BG
	BG = pygame.transform.scale(pygame.image.load('Images/forest/forest_bg.png'), (WINDOWWIDTH,WINDOWHEIGHT))
	Floor = Floors('Images/forest/forest_floor1.png')
	P1.a, P1.b = 100,930

	Ladder1 = Ladder(520,1050)
	Ladder2 = Ladder(640,1050)
	Ladder3 = Ladder(1880,1040)
	Life1   = Life(900,1040)
	Spike1  = Spike(1120,1046,'up')
	Spike2 = Spike(1619,462,'down')
	Trampoline1 = Trampoline(1630,791,0)
	Trampoline2 = Trampoline(1868,595,0)
	Portal1 = Portal(1619,352)

# --------------	Level 2 	--------------- # 
def Level2():
	global Floor, P1, BG
	BG = pygame.transform.scale(pygame.image.load('Images/forest/forest_bg.png'), (WINDOWWIDTH,WINDOWHEIGHT))
	Floor = Floors('Images/forest/forest_floor2.png')
	P1.a, P1.b = 150,750
	

	Trampoline1 = Trampoline(576,1286,0)
	Trampoline1.bounce_power = 32
	Trampoline2 = Trampoline(847,1286,0)
	Trampoline2.bounce_power = 32
	Trampoline3 = Trampoline(1238,1252,0)
	Trampoline3.bounce_power = 32
	Trampoline4 = Trampoline(1511,1252,0)
	Trampoline4.bounce_power = 32
	Trampoline4 = Trampoline(1784,1252,0)
	Trampoline4.bounce_power = 32
	Enemy1 = Enemy(1300,804,2)
	Enemy1.JUMPPOWER = 15
	Enemy1.MAXSPEED = 4
	Enemy2 = Enemy(1571,750,2)
	Enemy2.JUMPPOWER = 15
	Enemy2.MAXSPEED = 4
	Enemy3 = Enemy(2450,858,3)
	Enemy3.MAXSPEED=4
	Enemy4 = Enemy(2170,840,1)
	Enemy5 = Enemy(3377,840,1)
	Spike1 = Spike(2982,1320,'up')
	Spike2 = Spike(3182,1320,'up')
	Spike3 = Spike(3382,1320,'up')
	Spike4 = Spike(3582,1320,'up')
	Portal1 = Portal(2590,1321)

# --------------	Level 3 	--------------- # 
def Level3():
	global Floor, P1, BG
	BG = pygame.transform.scale(pygame.image.load('Images/forest/forest_bg.png'), (WINDOWWIDTH,WINDOWHEIGHT))
	Floor = Floors('Images/forest/forest_floor3.png')
	P1.a, P1.b = 860,2720
	
	Spike1 = Spike(1026,2805,'up')
	Spike2 = Spike(1958,2805,'up')
	Trampoline1 = Trampoline(1496,2850,0)
	Trampoline1.bounce_power = 28
	Trampoline2a = Trampoline(1347,2585,0)
	Trampoline2a.bounce_power = 32
	Trampoline2b = Trampoline(1639,2585,0)
	Trampoline2b.bounce_power = 20
	Trampoline3a = Trampoline(1187,2210,0)
	Trampoline3a.bounce_power = 23
	Trampoline3b = Trampoline(1493,2210,0)
	Trampoline3b.bounce_power = 19
	Trampoline3c = Trampoline(1797,2210,0)
	Trampoline3c.bounce_power = 35
	Trampoline4a = Trampoline(1045,1765,0)
	Trampoline4a.bounce_power = 35
	Trampoline4b = Trampoline(1340,1765,0)
	Trampoline4b.bounce_power = 18
	Trampoline4c = Trampoline(1641,1765,0)
	Trampoline4c.bounce_power = 23
	Trampoline4d = Trampoline(1935,1765,0)
	Trampoline4d.bounce_power = 18
	Trampoline5 = Trampoline(2083,1335,0)
	Trampoline5.bounce_power = 32
	Life1 = Life(1486,1580)
	Life2 = Life(1641,2013)
	
	Enemy1 = Enemy(1459,1327,3)
	Enemy1.MAXSPEED = 3.6
	Enemy1.timer.LEFT_RIGHT_TIME = 15
	Enemy2 = Enemy(1159,1327,3)
	Enemy2.MAXSPEED = 3.6
	Enemy2.timer.LEFT_RIGHT_TIME = 15
	
	Spike3 = Spike(893,981,'up')
	Spike4 = Spike(993,981,'up')
	Spike5 = Spike(1093,981,'up')
	Spike6 = Spike(1193,981,'up')
	Spike7 = Spike(1293,981,'up')
	Spike8 = Spike(1393,981,'up')
	Spike9 = Spike(1493,981,'up')
	Spike10 = Spike(1593,981,'up')
	Spike11 = Spike(1693,981,'up')
	
	Spike12 = Spike(756,473,'left')
	Spike12.PUSH_SPEED_Y = 0
	Spike12.PUSH_SPEED_X = 4
	Spike13 = Spike(756,573,'left')
	Spike13.PUSH_SPEED_Y = 0
	Spike13.PUSH_SPEED_X = 4
	Spike14 = Spike(756,673,'left')
	Spike14.PUSH_SPEED_Y = 0
	Spike14.PUSH_SPEED_X = 4
	Spike15 = Spike(756,773,'left')
	Spike15.PUSH_SPEED_Y = 0
	Spike15.PUSH_SPEED_X = 4
	Spike16 = Spike(756,873,'left')
	Spike16.PUSH_SPEED_Y = 0
	Spike16.PUSH_SPEED_X = 4
	Spike17 = Spike(756,973,'left')
	Spike17.PUSH_SPEED_Y = 0
	Spike17.PUSH_SPEED_X = 4
	
	Life3 = Life(678,573)
	Life3 = Life(678,673)
	Life3 = Life(678,773)
	
	
	Spike18 = Spike(600,473,'right')
	Spike18.PUSH_SPEED_X = 4
	Spike18.PUSH_SPEED_Y = 0
	Spike19 = Spike(600,573,'right')
	Spike19.PUSH_SPEED_Y = 0
	Spike19.PUSH_SPEED_X = 4
	Spike20 = Spike(600,673,'right')
	Spike20.PUSH_SPEED_Y = 0
	Spike20.PUSH_SPEED_X = 4
	Spike21 = Spike(600,773,'right')
	Spike21.PUSH_SPEED_Y = 0
	Spike21.PUSH_SPEED_X = 4
	Spike22 = Spike(600,873,'right')
	Spike22.PUSH_SPEED_Y = 0
	Spike22.PUSH_SPEED_X = 4
	
	Portal1 = Portal(462,982)
# --------------------------------------------- # 
P1 = Player(0,0)
while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()	
		elif event.type == MOUSEBUTTONUP:						#REMOVE FOR ACTUAL GAME
			x,y = event.pos										#REMOVE FOR ACTUAL GAME
			P1.a, P1.b  = screen_coords_to_floor_coords(x,y)	#REMOVE FOR ACTUAL GAME
	update_world()
	set_sprites()
	move_world()
	draw_world()
	fpsClock.tick(FPS)
	pygame.display.update()
	
	
	
	
	
