import pygame
import random
import sys
import os
from collections import deque

# --- Constants ---
GRID_W, GRID_H = 24, 15
TILE_SIZE = 40 
WIDTH, HEIGHT = GRID_W * TILE_SIZE, GRID_H * TILE_SIZE
FPS = 60

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Peaceful Maze: Collect the Diamonds")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 48)
        self.load_images()
        self.reset_game()

    def load_images(self):
        size = (TILE_SIZE, TILE_SIZE)
        try:
            self.imgs = {
                'mc': pygame.transform.scale(pygame.image.load('images/mc.png').convert_alpha(), size),
                'wall': pygame.transform.scale(pygame.image.load('images/wall.png').convert_alpha(), size),
                'earth': pygame.transform.scale(pygame.image.load('images/earth.png').convert_alpha(), size),
                'diamond': pygame.transform.scale(pygame.image.load('images/diamond.png').convert_alpha(), size),
                'door': pygame.transform.scale(pygame.image.load('images/door.png').convert_alpha(), size),
            }
        except Exception as e:
            print(f"Error loading images: {e}")
            pygame.quit()
            sys.exit()

    def reset_game(self):
        # 1 = Wall, 0 = Earth
        self.maze = [[1 for _ in range(GRID_H)] for _ in range(GRID_W)] 
        self.generate_maze(1, 1)
        
        self.diamonds = []
        self.exit_pos = (GRID_W - 2, GRID_H - 2)
        self.maze[self.exit_pos[0]][self.exit_pos[1]] = 0 
        
        earth_tiles = [(x, y) for x in range(GRID_W) for y in range(GRID_H) if self.maze[x][y] == 0 and (x,y) != (1,1)]
        random.shuffle(earth_tiles)
        
        # Spawn 10 Diamonds
        for i in range(10):
            if earth_tiles: 
                self.diamonds.append(earth_tiles.pop())

        self.mc_grid_pos = (1, 1)
        self.mc_pixel_pos = [1.0 * TILE_SIZE, 1.0 * TILE_SIZE]
        self.mc_moving_to = None
        self.state = "PLAYING"

    def generate_maze(self, x, y):
        self.maze[x][y] = 0
        dirs = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 < nx < GRID_W-1 and 0 < ny < GRID_H-1 and self.maze[nx][ny] == 1:
                self.maze[x + dx//2][y + dy//2] = 0
                self.generate_maze(nx, ny)

    def get_path(self, start, target):
        queue = deque([(start, [])])
        visited = {start}
        while queue:
            (x, y), path = queue.popleft()
            if (x, y) == target: return path
            for dx, dy in [(0,1),(0,-1),(1,0),(-1,0)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_W and 0 <= ny < GRID_H and self.maze[nx][ny] == 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path + [(nx, ny)]))
        return None

    def update(self):
        if self.mc_moving_to:
            tx, ty = self.mc_moving_to[0] * TILE_SIZE, self.mc_moving_to[1] * TILE_SIZE
            spd = 5 # Speed of movement
            if self.mc_pixel_pos[0] < tx: self.mc_pixel_pos[0] += spd
            elif self.mc_pixel_pos[0] > tx: self.mc_pixel_pos[0] -= spd
            if self.mc_pixel_pos[1] < ty: self.mc_pixel_pos[1] += spd
            elif self.mc_pixel_pos[1] > ty: self.mc_pixel_pos[1] -= spd
            
            if self.mc_pixel_pos[0] == tx and self.mc_pixel_pos[1] == ty:
                self.mc_grid_pos = self.mc_moving_to
                self.mc_moving_to = None
                if self.mc_grid_pos in self.diamonds: self.diamonds.remove(self.mc_grid_pos)
                if self.mc_grid_pos == self.exit_pos and not self.diamonds: self.state = "WIN"
        else:
            # If diamonds left, go to closest diamond. Otherwise, go to door.
            if self.diamonds:
                target = min(self.diamonds, key=lambda d: abs(d[0]-self.mc_grid_pos[0])+abs(d[1]-self.mc_grid_pos[1]))
            else:
                target = self.exit_pos
                
            path = self.get_path(self.mc_grid_pos, target)
            if path: self.mc_moving_to = path[0]

    def draw(self):
        for x in range(GRID_W):
            for y in range(GRID_H):
                img = self.imgs['wall'] if self.maze[x][y] == 1 else self.imgs['earth']
                self.screen.blit(img, (x * TILE_SIZE, y * TILE_SIZE))
        
        self.screen.blit(self.imgs['door'], (self.exit_pos[0]*TILE_SIZE, self.exit_pos[1]*TILE_SIZE))
        for d in self.diamonds: 
            self.screen.blit(self.imgs['diamond'], (d[0]*TILE_SIZE, d[1]*TILE_SIZE))
            
        self.screen.blit(self.imgs['mc'], (self.mc_pixel_pos[0], self.mc_pixel_pos[1]))

        if self.state == "WIN":
            surf = self.font.render("MAZE CLEARED! Press R to Restart", True, (255, 255, 255))
            rect = surf.get_rect(center=(WIDTH//2, HEIGHT//2))
            # Draw a small shadow for readability
            shadow = self.font.render("MAZE CLEARED! Press R to Restart", True, (0, 0, 0))
            self.screen.blit(shadow, (rect.x + 2, rect.y + 2))
            self.screen.blit(surf, rect)

        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r: self.reset_game()
            
            if self.state == "PLAYING":
                self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()