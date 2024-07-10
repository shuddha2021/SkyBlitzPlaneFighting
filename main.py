import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH = 800
HEIGHT = 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Colorful Airplane Fighting Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)


# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 30), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, BLUE, [(0, 30), (20, 0), (40, 30)])
        pygame.draw.polygon(self.image, CYAN, [(10, 25), (20, 5), (30, 25)])
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 5
        self.cooldown = 0
        self.health = 100
        self.score = 0
        self.power_up = None
        self.power_up_time = 0

    def move(self, dx, dy):
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed
        self.rect.clamp_ip(pygame.Rect(0, 0, WIDTH, HEIGHT))

    def shoot(self):
        if self.cooldown == 0:
            if self.power_up == "spread":
                bullets = [Bullet(self.rect.centerx, self.rect.top, -10, -2, YELLOW),
                           Bullet(self.rect.centerx, self.rect.top, -10, 0, YELLOW),
                           Bullet(self.rect.centerx, self.rect.top, -10, 2, YELLOW)]
            else:
                bullets = [Bullet(self.rect.centerx, self.rect.top, -10, 0, YELLOW)]

            for bullet in bullets:
                all_sprites.add(bullet)
                player_bullets.add(bullet)

            self.cooldown = 15

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

        if self.power_up:
            self.power_up_time -= 1
            if self.power_up_time <= 0:
                self.power_up = None


# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type):
        super().__init__()
        self.enemy_type = enemy_type
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        if enemy_type == 'red':
            color = RED
            self.bullet_color = ORANGE
            self.health = 1
        elif enemy_type == 'green':
            color = GREEN
            self.bullet_color = CYAN
            self.health = 2
        else:  # purple
            color = PURPLE
            self.bullet_color = YELLOW
            self.health = 3
        pygame.draw.polygon(self.image, color, [(0, 0), (15, 30), (30, 0)])
        pygame.draw.polygon(self.image, WHITE, [(7, 8), (15, 22), (23, 8)])
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed_y = random.randrange(1, 3)
        self.speed_x = random.randrange(-2, 2)
        self.shoot_delay = random.randint(60, 120)
        self.last_shot = pygame.time.get_ticks()

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speed_y = random.randrange(1, 3)

        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.shoot()
            self.last_shot = now
            self.shoot_delay = random.randint(60, 120)

    def shoot(self):
        if self.enemy_type == 'red':
            bullet = Bullet(self.rect.centerx, self.rect.bottom, 5, 0, self.bullet_color)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)
        elif self.enemy_type == 'green':
            for i in [-1, 1]:
                bullet = Bullet(self.rect.centerx, self.rect.bottom, 5, i * 2, self.bullet_color)
                all_sprites.add(bullet)
                enemy_bullets.add(bullet)
        else:  # purple
            for i in range(-1, 2):
                bullet = Bullet(self.rect.centerx, self.rect.bottom, 5, i * 2, self.bullet_color)
                all_sprites.add(bullet)
                enemy_bullets.add(bullet)


# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_y, speed_x, color):
        super().__init__()
        self.image = pygame.Surface((5, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, color, [0, 0, 5, 10])
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = speed_y
        self.speed_x = speed_x

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()


# Power-up class
class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, YELLOW, [(10, 0), (20, 10), (10, 20), (0, 10)])
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


# Explosion animation
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, color):
        super().__init__()
        self.color = color
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == 3:
                self.kill()
            else:
                center = self.rect.center
                self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.circle(self.image, self.color, (15, 15), 15 - 5 * self.frame)
                self.rect = self.image.get_rect()
                self.rect.center = center


# Star class for background
class Star(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((2, 2))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = random.randrange(WIDTH)
        self.rect.y = random.randrange(HEIGHT)
        self.speed = random.randrange(1, 3)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.x = random.randrange(WIDTH)
            self.rect.y = random.randrange(-50, -10)


# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
power_ups = pygame.sprite.Group()
stars = pygame.sprite.Group()

# Create player
player = Player(WIDTH // 2, HEIGHT - 50)
all_sprites.add(player)

# Create stars
for i in range(50):
    star = Star()
    all_sprites.add(star)
    stars.add(star)

# Game loop
running = True
clock = pygame.time.Clock()
score = 0
spawn_enemy = pygame.USEREVENT + 1
pygame.time.set_timer(spawn_enemy, 1500)  # Reduced spawn rate
spawn_power_up = pygame.USEREVENT + 2
pygame.time.set_timer(spawn_power_up, 10000)

font = pygame.font.Font(None, 36)

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == spawn_enemy:
            enemy_type = random.choice(['red', 'green', 'purple'])
            enemy = Enemy(enemy_type)
            all_sprites.add(enemy)
            enemies.add(enemy)
        elif event.type == spawn_power_up:
            if random.random() < 0.3:  # 30% chance to spawn a power-up
                power_up = PowerUp()
                all_sprites.add(power_up)
                power_ups.add(power_up)

    # Handle input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.move(-1, 0)
    if keys[pygame.K_RIGHT]:
        player.move(1, 0)
    if keys[pygame.K_UP]:
        player.move(0, -1)
    if keys[pygame.K_DOWN]:
        player.move(0, 1)
    if keys[pygame.K_SPACE]:
        player.shoot()

    # Update
    all_sprites.update()

    # Check for collisions
    hits = pygame.sprite.spritecollide(player, enemies, True)
    for hit in hits:
        player.health -= 20
        explosion = Explosion(hit.rect.center, ORANGE)
        all_sprites.add(explosion)
        if player.health <= 0:
            running = False

    hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
    for hit in hits:
        player.health -= 10
        explosion = Explosion(hit.rect.center, YELLOW)
        all_sprites.add(explosion)
        if player.health <= 0:
            running = False

    hits = pygame.sprite.groupcollide(enemies, player_bullets, False, True)
    for enemy, bullets in hits.items():
        enemy.health -= len(bullets)
        if enemy.health <= 0:
            score += 10
            explosion = Explosion(enemy.rect.center, enemy.bullet_color)
            all_sprites.add(explosion)
            enemy.kill()

    hits = pygame.sprite.spritecollide(player, power_ups, True)
    for hit in hits:
        player.power_up = "spread"
        player.power_up_time = 300  # 5 seconds

    # Draw
    window.fill(BLACK)
    all_sprites.draw(window)

    # Draw HUD
    score_text = font.render(f"Score: {score}", True, WHITE)
    window.blit(score_text, (10, 10))

    health_text = font.render(f"Health: {player.health}", True, WHITE)
    window.blit(health_text, (WIDTH - 150, 10))

    if player.power_up:
        power_up_text = font.render("Power-up active!", True, YELLOW)
        window.blit(power_up_text, (WIDTH // 2 - 70, 10))

    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Game over screen
window.fill(BLACK)
game_over_text = font.render("Game Over", True, WHITE)
final_score_text = font.render(f"Final Score: {score}", True, WHITE)
window.blit(game_over_text, (WIDTH // 2 - 70, HEIGHT // 2 - 50))
window.blit(final_score_text, (WIDTH // 2 - 70, HEIGHT // 2 + 10))
pygame.display.flip()

# Wait for a few seconds before quitting
pygame.time.wait(3000)

# Quit the game
pygame.quit()