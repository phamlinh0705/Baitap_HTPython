
import pygame, random, math, os

# Khởi tạo Pygame
pygame.init()
try:
    pygame.mixer.init()
    sound_enabled = True
except:
    sound_enabled = False

# Cấu hình màn hình
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Astrocrash")
clock = pygame.time.Clock()

# Tải tài nguyên an toàn
def load_image(name):
    try:
        return pygame.image.load(os.path.join("assets", name)).convert_alpha()
    except Exception as e:
        print(f"[!] Không thể tải ảnh: {name} — {e}")
        return pygame.Surface((50, 50))  # Ảnh giả

ship_img = load_image("ship.png")
asteroid_img = load_image("asteroid.png")
missile_img = load_image("missile.png")
explosion_img = load_image("explosion.png")

boom_sound = None
if sound_enabled:
    try:
        boom_sound = pygame.mixer.Sound("assets/boom.wav")
        pygame.mixer.music.load("assets/music.mp3")
        pygame.mixer.music.play(-1)
    except Exception as e:
        print("[!] Không thể tải âm thanh:", e)

font = pygame.font.SysFont(None, 36)
score = 0

# -------- LỚP -------- #
class Ship(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = ship_img
        self.image = ship_img
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT//2))
        self.angle = 0
        self.speed = 0

    def update(self, keys):
        if keys[pygame.K_LEFT]:
            self.angle += 5
        if keys[pygame.K_RIGHT]:
            self.angle -= 5
        if keys[pygame.K_UP]:
            self.speed = 5
        else:
            self.speed = 0

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        rad = math.radians(-self.angle)
        dx = math.cos(rad) * self.speed
        dy = math.sin(rad) * self.speed
        self.rect.x += dx
        self.rect.y += dy
        self.rect.x %= WIDTH
        self.rect.y %= HEIGHT

class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = missile_img
        self.rect = self.image.get_rect(center=(x, y))
        self.angle = angle
        self.speed = 10
        self.timer = 60

    def update(self):
        rad = math.radians(-self.angle)
        self.rect.x += math.cos(rad) * self.speed
        self.rect.y += math.sin(rad) * self.speed
        self.timer -= 1
        if self.timer <= 0 or not screen.get_rect().colliderect(self.rect):
            self.kill()

class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = asteroid_img
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH), random.randint(0, HEIGHT)))
        self.vx = random.choice([-2, -1, 1, 2])
        self.vy = random.choice([-2, -1, 1, 2])

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.rect.x %= WIDTH
        self.rect.y %= HEIGHT

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        self.image = explosion_img
        self.rect = self.image.get_rect(center=center)
        self.timer = 15

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

# -------- KHỞI TẠO SPRITES -------- #
all_sprites = pygame.sprite.Group()
missiles = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
explosions = pygame.sprite.Group()

ship = Ship()
all_sprites.add(ship)

for _ in range(5):
    asteroid = Asteroid()
    asteroids.add(asteroid)
    all_sprites.add(asteroid)

# -------- VÒNG LẶP GAME -------- #
running = True
while running:
    clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            missile = Missile(ship.rect.centerx, ship.rect.centery, ship.angle)
            missiles.add(missile)
            all_sprites.add(missile)

    ship.update(keys)
    missiles.update()
    asteroids.update()
    explosions.update()

    hits = pygame.sprite.groupcollide(missiles, asteroids, True, True)
    for hit in hits:
        if boom_sound:
            boom_sound.play()
        explosion = Explosion(hit.rect.center)
        explosions.add(explosion)
        all_sprites.add(explosion)
        score += 10
        new_ast = Asteroid()
        asteroids.add(new_ast)
        all_sprites.add(new_ast)

    screen.fill((0, 0, 20))
    all_sprites.draw(screen)
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    pygame.display.flip()

pygame.quit()
