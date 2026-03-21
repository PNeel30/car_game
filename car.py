import pygame
from pygame.locals import *
import random

pygame.init()

# window
width = 1150
height = 950
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Car Game')

# colors
gray = (100, 100, 100)
green = (76, 208, 56)
red = (200, 0, 0)
white = (255, 255, 255)
yellow = (255, 232, 0)

# road
road_width = 940
marker_width = 30
marker_height = 30

# lanes
left_lane = 323
center_lane = 626
right_lane = 790
lanes = [left_lane, center_lane, right_lane]

road = (90, 0, road_width, height)
left_edge_marker = (50, 0, marker_width, height)
right_edge_marker = (1040, 0, marker_width, height)

lane_marker_move_y = 0

# player
player_x = center_lane
player_y = 700

# fps
clock = pygame.time.Clock()
fps = 120

# game state
gameover = False
paused = False   # ✅ NEW
speed = 2
score = 0

# ================= VEHICLE =================
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, image, x, y, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(image, (width, height))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

class PlayerVehicle(Vehicle):
    def __init__(self, x, y):
        image = pygame.image.load('car.png')
        super().__init__(image, x, y, 80, 160)

# groups
player_group = pygame.sprite.Group()
vehicle_group = pygame.sprite.Group()

player = PlayerVehicle(player_x, player_y)
player_group.add(player)

# vehicle types
vehicle_types = [
    ("pickup_truck.png", 110, 180),
    ("semi_trailer.png", 110, 240),
    ("taxi.png", 80, 160),
    ("van.png", 90, 180)
]

# crash
crash = pygame.image.load('crash.png')
crash = pygame.transform.scale(crash, (120, 120))
crash_rect = crash.get_rect()

# ================= GAME LOOP =================
running = True
while running:

    clock.tick(fps)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if event.type == KEYDOWN:

            # ⏸️ PAUSE TOGGLE
            if event.key == K_p and not gameover:
                paused = not paused

            if not paused and not gameover:

                if event.key == K_LEFT and player.rect.center[0] > left_lane:
                    player.rect.x -= (center_lane - left_lane)

                elif event.key == K_RIGHT and player.rect.center[0] < right_lane:
                    player.rect.x += (center_lane - left_lane)

                # side collision
                for vehicle in vehicle_group:
                    if pygame.sprite.collide_rect(player, vehicle):
                        gameover = True
                        crash_rect.center = player.rect.center

    # ================= GAMEPLAY =================
    if not paused and not gameover:

        # background
        screen.fill(green)
        pygame.draw.rect(screen, gray, road)
        pygame.draw.rect(screen, yellow, left_edge_marker)
        pygame.draw.rect(screen, yellow, right_edge_marker)

        # lane animation
        lane_marker_move_y += speed * 2
        if lane_marker_move_y >= marker_height * 2:
            lane_marker_move_y = 0

        for y in range(marker_height * -2, height, marker_height * 2):
            pygame.draw.rect(screen, white, (left_lane + 50, y + lane_marker_move_y, marker_width, marker_height))
            pygame.draw.rect(screen, white, (center_lane + 50, y + lane_marker_move_y, marker_width, marker_height))

        # draw player
        player_group.draw(screen)

        # add vehicles
        if len(vehicle_group) < 2:
            add_vehicle = True
            for vehicle in vehicle_group:
                if vehicle.rect.top < vehicle.rect.height * 2:
                    add_vehicle = False

            if add_vehicle:
                lane = random.choice(lanes)
                filename, w, h = random.choice(vehicle_types)
                image = pygame.image.load(filename)
                vehicle = Vehicle(image, lane, height / -2, w, h)
                vehicle_group.add(vehicle)

        # move vehicles
        for vehicle in vehicle_group:
            vehicle.rect.y += speed

            if vehicle.rect.top >= height:
                vehicle.kill()
                score += 1

                if score > 0 and score % 5 == 0:
                    speed += 1

        vehicle_group.draw(screen)

        # score
        font = pygame.font.Font(pygame.font.get_default_font(), 20)
        text = font.render('Score: ' + str(score), True, white)
        screen.blit(text, (50, 50))

        # collision
        if pygame.sprite.spritecollide(player, vehicle_group, True):
            gameover = True
            crash_rect.center = player.rect.center

    else:
        # draw static background when paused or gameover
        screen.fill(green)
        pygame.draw.rect(screen, gray, road)
        pygame.draw.rect(screen, yellow, left_edge_marker)
        pygame.draw.rect(screen, yellow, right_edge_marker)
        player_group.draw(screen)
        vehicle_group.draw(screen)

    # ================= PAUSE TEXT =================
    if paused:
        font = pygame.font.Font(pygame.font.get_default_font(), 60)
        text = font.render('PAUSED', True, white)
        screen.blit(text, (width // 2 - 120, height // 2 - 50))

        font_small = pygame.font.Font(pygame.font.get_default_font(), 25)
        text2 = font_small.render('Press P to Resume', True, white)
        screen.blit(text2, (width // 2 - 120, height // 2 + 20))

    # ================= GAME OVER =================
    if gameover:
        screen.blit(crash, crash_rect)

        pygame.draw.rect(screen, red, (0, 50, width, 100))

        font = pygame.font.Font(pygame.font.get_default_font(), 25)
        text = font.render('Game Over! Press Y to Restart or N to Quit', True, white)
        screen.blit(text, (200, 90))

    pygame.display.update()

    # ================= RESTART LOOP =================
    while gameover:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == QUIT:
                gameover = False
                running = False

            if event.type == KEYDOWN:
                if event.key == K_y:
                    gameover = False
                    paused = False   # reset pause
                    speed = 2
                    score = 0
                    vehicle_group.empty()
                    player.rect.center = [player_x, player_y]

                elif event.key == K_n:
                    gameover = False
                    running = False

pygame.quit()