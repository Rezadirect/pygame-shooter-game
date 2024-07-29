import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
PLAYER_RADIUS = 20
PLAYER_HEALTH = 100  # Starting health for player
ENEMY_WIDTH, ENEMY_HEIGHT = 50, 50
AMMO_RADIUS = 5
ENEMY_SPAWN_RATE = 30  # Frames between enemy spawns
FPS = 60
ENEMY_SPEED = 1  # enemy speed
ENEMY_SHOOT_RATE = 60  # Frames between enemy shoots
MAX_ENEMIES = 2  # Maximum number of enemies allowed on the screen
MAX_AMMO = 30  # Max ammo before needing to reload

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
LIGHT_GRAY = (200, 200, 200)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Game")

# Clock
clock = pygame.time.Clock()

# Player class
class Player:
    def __init__(self):
        self.position = pygame.Vector2(WIDTH // 2, HEIGHT // 2)
        self.health = PLAYER_HEALTH

    def move(self, direction):
        self.position += direction

    def draw(self):
        pygame.draw.circle(screen, GREEN, (int(self.position.x), int(self.position.y)), PLAYER_RADIUS)

    def get_rect(self):
        return pygame.Rect(self.position.x - PLAYER_RADIUS, self.position.y - PLAYER_RADIUS, PLAYER_RADIUS * 2, PLAYER_RADIUS * 2)

    def draw_health(self):
        health_bar_length = 100
        health_percentage = self.health / PLAYER_HEALTH
        current_health_length = health_bar_length * health_percentage
        pygame.draw.rect(screen, RED, (10, HEIGHT - 30, health_bar_length, 20))  # Background bar
        pygame.draw.rect(screen, GREEN, (10, HEIGHT - 30, current_health_length, 20))  # Health bar

# Enemy class
class Enemy:
    def __init__(self):
        self.position = pygame.Vector2(random.randint(0, WIDTH - ENEMY_WIDTH), random.randint(0, HEIGHT - ENEMY_HEIGHT))
        self.health = 3  # Enemies can take 3 hits
        self.rect = pygame.Rect(self.position.x, self.position.y, ENEMY_WIDTH, ENEMY_HEIGHT)
        self.shoot_timer = 0  # Timer for shooting

    def update(self):
        self.rect.topleft = (self.position.x, self.position.y)

    def move_towards_player(self, player_position):
        if self.position.distance_to(player_position) > 1:
            direction = (player_position - self.position).normalize()
            self.position += direction * ENEMY_SPEED

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)

    def hit(self):
        self.health -= 1

    def is_alive(self):
        return self.health > 0

    def shoot(self, player_position):
        return Ammo(self.position, player_position - self.position)

# Ammo class
class Ammo:
    def __init__(self, position, direction):
        self.position = pygame.Vector2(position)
        self.direction = direction.normalize()
        self.speed = 10
        self.rect = pygame.Rect(self.position.x, self.position.y, AMMO_RADIUS * 2, AMMO_RADIUS * 2)

    def update(self):
        self.position += self.direction * self.speed
        self.rect.center = (self.position.x, self.position.y)

    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.position.x), int(self.position.y)), AMMO_RADIUS)

# Main game loop
def main():
    global screen  # Declare screen as a global variable
    player = Player()
    enemies = []
    ammo_list = []
    enemy_bullets = []
    ammo_count = 30
    kills = 0
    game_over = False
    reload_start_time = None
    reload_duration = 3000  # just 3000 duration what you want here :/
    reloading = False

    running = True
    frame_count = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Toggle full-screen on pressing F11
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    # Check current mode to toggle between full screen and windowed
                    if screen.get_flags() & pygame.FULLSCREEN:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT))  # windowed mode
                    else:
                        screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)  # full screen

        if game_over:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                main()
            continue
        
        # Move player
        keys = pygame.key.get_pressed()
        player_direction = pygame.Vector2(0, 0)
        if keys[pygame.K_w]: player_direction.y -= 5
        if keys[pygame.K_s]: player_direction.y += 5
        if keys[pygame.K_a]: player_direction.x -= 5
        if keys[pygame.K_d]: player_direction.x += 5
        player.move(player_direction)

        # Get mouse position for shooting direction
        mouse_pos = pygame.mouse.get_pos()
        direction = pygame.Vector2(mouse_pos) - player.position

        # Shooting ammo
        if pygame.mouse.get_pressed()[0] and not reloading:  # Prevent shooting while reloading
            if ammo_count > 0:
                ammo_list.append(Ammo(player.position, direction))
                ammo_count -= 1

        # Reload ammo
        if keys[pygame.K_r] and not reloading and ammo_count < MAX_AMMO:
            print("Reloading...")
            reload_start_time = pygame.time.get_ticks()
            reloading = True

        if reloading:
            elapsed_time = pygame.time.get_ticks() - reload_start_time
            if elapsed_time >= reload_duration:
                ammo_count = MAX_AMMO
                print("Reload complete!")
                reloading = False

        # Update ammo and check for collisions
        for bullet in ammo_list[:]:
            bullet.update()
            for enemy in enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    ammo_list.remove(bullet)
                    enemy.hit()
                    if not enemy.is_alive():
                        enemies.remove(enemy)
                        kills += 1  # Increase kills count when an enemy is defeated
                    break

        # Spawn enemies only if the count is less than MAX_ENEMIES
        if len(enemies) < MAX_ENEMIES:
            frame_count += 1
            if frame_count % ENEMY_SPAWN_RATE == 0:
                new_enemy = Enemy()
                enemies.append(new_enemy)
                print(f"Spawned an enemy. Total enemies: {len(enemies)}")

        # Move enemies and check for hits
        for enemy in enemies[:]:
            enemy.update()
            enemy.move_towards_player(player.position)

            if enemy.rect.colliderect(player.get_rect()):
                player.health -= 1  # Reduce player health when enemy collides
                if player.health <= 0:
                    game_over = True
                break  # Exit the enemy loop if the player is hit

            # Handle enemy shooting
            enemy.shoot_timer += 1
            if enemy.shoot_timer >= ENEMY_SHOOT_RATE:
                enemy_bullets.append(enemy.shoot(player.position))
                enemy.shoot_timer = 0

        # Update enemy bullets
        for bullet in enemy_bullets[:]:
            bullet.update()
            if bullet.rect.colliderect(player.get_rect()):
                player.health -= 10  # Reduce player health when enemy bullet hits
                if player.health <= 0:
                    game_over = True
                enemy_bullets.remove(bullet)
                break  # Exit the enemy bullet loop if the player is hit

        # Draw everything
        screen.fill(BLACK)
        player.draw()

        for enemy in enemies:
            enemy.draw()

        for bullet in ammo_list:
            bullet.draw()

        for bullet in enemy_bullets:
            bullet.draw()

        # Draw player health and ammo count
        player.draw_health()
        
        # Draw reload status
        if reloading:
            font = pygame.font.Font(None, 36)
            reload_surf = font.render("Reloading...", True, LIGHT_GRAY)
            screen.blit(reload_surf, (WIDTH // 2 - reload_surf.get_width() // 2, HEIGHT // 2 - 50))

        # Draw current ammo count
        ammo_count_text = f'Bullets: {ammo_count}/{MAX_AMMO}'
        ammo_surf = pygame.font.Font(None, 36).render(ammo_count_text, True, LIGHT_GRAY)
        screen.blit(ammo_surf, (WIDTH - 150, HEIGHT - 30))
        # Draw kills count
        kills_text = f'Kills: {kills}'
        kills_surf = pygame.font.Font(None, 36).render(kills_text, True, LIGHT_GRAY)
        screen.blit(kills_surf, (WIDTH - 150, HEIGHT - 60))

        if game_over:
            font = pygame.font.Font(None, 74)
            text = font.render('You Died!', True, WHITE)
            screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()