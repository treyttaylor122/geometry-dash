import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
GROUND_HEIGHT = 100
FPS = 60
GRAVITY = 1
JUMP_FORCE = -20
GAME_SPEED = 8
OBSTACLE_FREQUENCY = 120  # Frames between obstacles

# Colors
BACKGROUND = (20, 20, 35)
GROUND_COLOR = (45, 45, 70)
PLAYER_COLOR = (0, 200, 255)
OBSTACLE_COLOR = (255, 50, 50)
TEXT_COLOR = (255, 255, 255)
GLOW_COLOR = (100, 200, 255, 100)

class Player:
    def __init__(self):
        self.width = 40
        self.height = 40
        self.x = 150
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
        self.velocity_y = 0
        self.is_jumping = False
        self.rotation = 0
        self.glow_particles = []
        
    def jump(self):
        if not self.is_jumping:
            self.velocity_y = JUMP_FORCE
            self.is_jumping = True
            # Create jump effect
            for _ in range(5):
                self.glow_particles.append([self.x + self.width//2, 
                                          self.y + self.height, 
                                          random.uniform(-2, 2), 
                                          random.uniform(-5, -2),
                                          random.randint(10, 20)])
    
    def update(self):
        # Apply gravity
        self.velocity_y += GRAVITY
        self.y += self.velocity_y
        
        # Check ground collision
        ground_level = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
        if self.y > ground_level:
            self.y = ground_level
            self.velocity_y = 0
            self.is_jumping = False
            
        # Update rotation
        self.rotation = (self.rotation + 8) % 360
        
        # Update particles
        for particle in self.glow_particles[:]:
            particle[0] += particle[2]
            particle[1] += particle[3]
            particle[4] -= 0.5
            if particle[4] <= 0:
                self.glow_particles.remove(particle)
                
    def draw(self, screen):
        # Draw glow particles
        for particle in self.glow_particles:
            pygame.draw.circle(screen, GLOW_COLOR[:3], 
                             (int(particle[0]), int(particle[1])), 
                             int(particle[4]))
        
        # Draw player cube with rotation effect
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Create surface for rotation
        player_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(player_surface, PLAYER_COLOR, (0, 0, self.width, self.height))
        pygame.draw.rect(player_surface, (255, 255, 255), (0, 0, self.width, self.height), 2)
        
        # Draw inner details
        pygame.draw.line(player_surface, (200, 240, 255), 
                        (self.width//4, self.height//4), 
                        (3*self.width//4, self.height//4), 2)
        pygame.draw.line(player_surface, (200, 240, 255),
                        (self.width//4, 3*self.height//4),
                        (3*self.width//4, 3*self.height//4), 2)
        
        # Rotate and draw
        rotated = pygame.transform.rotate(player_surface, self.rotation)
        rotated_rect = rotated.get_rect(center=player_rect.center)
        screen.blit(rotated, rotated_rect)
        
    def get_rect(self):
        return pygame.Rect(self.x + 10, self.y + 10, self.width - 20, self.height - 20)

class Obstacle:
    def __init__(self, x, obstacle_type=0):
        self.type = obstacle_type  # 0 = spike, 1 = block
        self.width = 40 if obstacle_type == 0 else 80
        self.height = 80 if obstacle_type == 0 else 40
        self.x = x
        self.y = SCREEN_HEIGHT - GROUND_HEIGHT - self.height
        self.passed = False
        
    def update(self):
        self.x -= GAME_SPEED
        
    def draw(self, screen):
        if self.type == 0:  # Spike
            points = [
                (self.x, self.y + self.height),
                (self.x + self.width//2, self.y),
                (self.x + self.width, self.y + self.height)
            ]
            pygame.draw.polygon(screen, OBSTACLE_COLOR, points)
            # Inner color
            inner_points = [
                (self.x + 5, self.y + self.height - 5),
                (self.x + self.width//2, self.y + 10),
                (self.x + self.width - 5, self.y + self.height - 5)
            ]
            pygame.draw.polygon(screen, (255, 100, 100), inner_points)
        else:  # Block
            pygame.draw.rect(screen, OBSTACLE_COLOR, 
                           (self.x, self.y, self.width, self.height))
            pygame.draw.rect(screen, (255, 100, 100),
                           (self.x + 5, self.y + 5, self.width - 10, self.height - 10))
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-10, -5)
        self.life = 30
        self.color = (random.randint(200, 255), random.randint(100, 200), random.randint(50, 100))
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.5
        self.life -= 1
        
    def draw(self, screen):
        alpha = int(255 * (self.life / 30))
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 3)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Geometry Dash Clone")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        
        self.reset_game()
        
        # Try to add some simple sound effects
        try:
            self.jump_sound = pygame.mixer.Sound("jump.wav") if pygame.mixer.get_init() else None
        except:
            self.jump_sound = None
            
    def reset_game(self):
        self.player = Player()
        self.obstacles = []
        self.particles = []
        self.score = 0
        self.game_over = False
        self.obstacle_timer = 0
        self.bg_offset = 0
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    self.player.jump()
                    if self.jump_sound:
                        self.jump_sound.play()
                        
                if event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                    
    def generate_obstacle(self):
        obstacle_type = random.randint(0, 1)
        new_obstacle = Obstacle(SCREEN_WIDTH, obstacle_type)
        self.obstacles.append(new_obstacle)
        
    def update(self):
        if not self.game_over:
            self.player.update()
            
            # Update background offset
            self.bg_offset = (self.bg_offset - GAME_SPEED//2) % 100
            
            # Generate obstacles
            self.obstacle_timer += 1
            if self.obstacle_timer >= OBSTACLE_FREQUENCY:
                self.generate_obstacle()
                self.obstacle_timer = 0
                # Randomly adjust frequency for variety
                OBSTACLE_FREQUENCY = random.randint(90, 150)
            
            # Update obstacles and check collisions
            for obstacle in self.obstacles[:]:
                obstacle.update()
                
                # Check collision
                if self.player.get_rect().colliderect(obstacle.get_rect()):
                    self.game_over = True
                    # Create explosion particles
                    for _ in range(30):
                        self.particles.append(Particle(
                            self.player.x + self.player.width//2,
                            self.player.y + self.player.height//2
                        ))
                
                # Update score
                if not obstacle.passed and obstacle.x < self.player.x:
                    obstacle.passed = True
                    self.score += 1
                
                # Remove off-screen obstacles
                if obstacle.x < -obstacle.width:
                    self.obstacles.remove(obstacle)
            
            # Update particles
            for particle in self.particles[:]:
                particle.update()
                if particle.life <= 0:
                    self.particles.remove(particle)
                    
    def draw_background(self):
        # Gradient background
        for i in range(SCREEN_HEIGHT):
            color_value = 20 + (i // 20)
            pygame.draw.line(self.screen, (color_value, color_value, color_value + 15),
                           (0, i), (SCREEN_WIDTH, i))
        
        # Moving grid pattern
        for x in range(int(self.bg_offset), SCREEN_WIDTH, 100):
            pygame.draw.line(self.screen, (50, 50, 80, 100), 
                           (x, 0), (x, SCREEN_HEIGHT), 1)
        for y in range(0, SCREEN_HEIGHT, 100):
            pygame.draw.line(self.screen, (50, 50, 80, 100),
                           (0, y), (SCREEN_WIDTH, y), 1)
        
        # Ground
        pygame.draw.rect(self.screen, GROUND_COLOR,
                        (0, SCREEN_HEIGHT - GROUND_HEIGHT, SCREEN_WIDTH, GROUND_HEIGHT))
        
        # Ground pattern
        for x in range(0, SCREEN_WIDTH, 50):
            pygame.draw.line(self.screen, (60, 60, 90),
                           (x, SCREEN_HEIGHT - GROUND_HEIGHT),
                           (x, SCREEN_HEIGHT), 1)
    
    def draw(self):
        self.draw_background()
        
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, TEXT_COLOR)
        self.screen.blit(score_text, (20, 20))
        
        # Draw controls hint
        controls_text = self.small_font.render("SPACE/UP: Jump | R: Restart", True, TEXT_COLOR)
        self.screen.blit(controls_text, (20, SCREEN_HEIGHT - 40))
        
        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("GAME OVER", True, (255, 50, 50))
            final_score = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            restart_text = self.small_font.render("Press R to restart", True, TEXT_COLOR)
            
            self.screen.blit(game_over_text, 
                           (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 
                            SCREEN_HEIGHT//2 - 60))
            self.screen.blit(final_score,
                           (SCREEN_WIDTH//2 - final_score.get_width()//2,
                            SCREEN_HEIGHT//2))
            self.screen.blit(restart_text,
                           (SCREEN_WIDTH//2 - restart_text.get_width()//2,
                            SCREEN_HEIGHT//2 + 60))
        
        pygame.display.flip()
    
    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
