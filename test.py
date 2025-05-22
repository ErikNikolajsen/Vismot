import pygame

pygame.init()
screen = pygame.display.set_mode((200, 100))
font = pygame.font.SysFont('DejaVu Sans Mono', 32)  # Or any font with │ support
text = font.render("│\n│─\n│", True, (255, 255, 255))

screen.fill((0, 0, 0))
screen.blit(text, (50, 25))
pygame.display.flip()

# Basic event loop to keep the window open
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

pygame.quit()
