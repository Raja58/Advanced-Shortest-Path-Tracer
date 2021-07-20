# // <!--
# //  ============================
# //  @Author  :        Raja Durai M
# //  @Version :        1.0
# //  @Date    :        20 Jul 2021
# //  @Detail  :        Path Tracer
# //  ============================
# //  -->

import pygame	# 2D graphics module
import math
from queue import PriorityQueue

# A* is an informed search algorithm
# Heuristic function guides us to the right direction
# H(n) -> distance from that node to destination node
# G(n) -> current shortest distance from start node to this node
# F(n) = H(n) + G(n)

WIDTH = 800	#just keeping grid as a square (window)
WIN = pygame.display.set_mode((WIDTH, WIDTH))	#setting display size
pygame.display.set_caption("A* Path Tracer")	#setting caption

# RGB Color codes
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)


class Spot:
	def __init__(self, row, col, width, total_rows):	#constructor
		self.row = row 			#FOR our indexing
		self.col = col
		self.x = row * width	#for pygame
		self.y = col * width	#exact coordinate positions
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows

	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == RED

	def is_open(self):
		return self.color == YELLOW

	def is_barrier(self):
		return self.color == BLACK	#barrier

	def is_start(self):
		return self.color == BLUE	#starting

	def is_end(self):
		return self.color == PURPLE	#ending

	def reset(self):
		self.color = WHITE

	def make_start(self):
		self.color = BLUE

	def make_closed(self):
		self.color = RED

	def make_open(self):
		self.color = YELLOW

	def make_barrier(self):
		self.color = BLACK

	def make_end(self):
		self.color = PURPLE

	def make_path(self):
		self.color = GREEN

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))	#win - window i.e., the displayed pyboard

	def update_neighbors(self, grid):
		self.neighbors = []
		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])
 
		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])

	def __lt__(self, other):
		return False

def h(p1, p2):		#Manhattan distance
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()


def algorithm(draw, grid, start, end):
	count = 0 	#to keep track of which node came first into priority queue
	open_set = PriorityQueue()
	open_set.put((0, count, start))	#Fscore, count, node
	came_from = {}	#dictionary to know where we came from
	g_score = {spot: float("inf") for row in grid for spot in row}
	g_score[start] = 0
	f_score = {spot: float("inf") for row in grid for spot in row}
	f_score[start] = h(start.get_pos(), end.get_pos())

	open_set_hash = {start}	#to keep track of items in the priority_queue

	while not open_set.empty():	#when priority queue is not empty
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2]	#taking the node
		open_set_hash.remove(current)

		if current == end:
			reconstruct_path(came_from, end, draw)
			end.make_end()
			return True

		for neighbor in current.neighbors:
			temp_g_score = g_score[current] + 1

			if temp_g_score < g_score[neighbor]:	#update if this is a better path
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
				if neighbor not in open_set_hash:
					count += 1
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.make_open()

		draw()

		if current != start:
			current.make_closed()

	return False


def make_grid(rows, width):	#creating grid using lists
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap, rows)
			grid[i].append(spot)

	return grid


def draw_grid(win, rows, width):	#drawing lones for grid
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
	for j in range(rows):
		pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):	#each time clearing all and updating spots again in pygame, but we can't the difference due to speed
	win.fill(WHITE)	#initially make all white

	for row in grid:	
		for spot in row:
			spot.draw(win)

	draw_grid(win, rows, width)
	pygame.display.update()


def get_clicked_pos(pos, rows, width):	#getting position
	gap = width // rows
	y, x = pos

	row = y // gap
	col = x // gap

	return row, col


def main(win, width):
	ROWS = 50	# 50 x 50 board
	grid = make_grid(ROWS, width)

	start = None 
	end = None

	run = True
	while run:	#main loop which runs over and over again to update
		draw(win, grid, ROWS, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:	#closing the game when close is clicked
				run = False

			if pygame.mouse.get_pressed()[0]: # LEFT for creating cells
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				if not start and spot != end:	#assigning start also checking it's not same as end, as we can change the start even after assigning end.
					start = spot
					start.make_start()

				elif not end and spot != start:	#simlilar for end
					end = spot
					end.make_end()

				elif spot != end and spot != start:	#for barrier
					spot.make_barrier()

			elif pygame.mouse.get_pressed()[2]: # RIGHT for clearing cells
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]
				spot.reset()
				if spot == start:
					start = None
				elif spot == end:
					end = None

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and start and end:
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)

					algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

				if event.key == pygame.K_c:
					start = None
					end = None
					grid = make_grid(ROWS, width)

	pygame.quit()

main(WIN, WIDTH)