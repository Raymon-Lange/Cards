import pygame
import logging
from Network import Network
from Game import *

WIDTH = 800
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Client")


def drawBoard():
    screen.fill((0,100,0))

    
    


def main():
    run = True
    n = Network()
    playerId = n.getP()
    logger = logging.getLogger("Client")
    logger.info("You are player %s", playerId)

    clock = pygame.time.Clock()

    while run:
        clock.tick(60)

        try:
            game = n.send("get")
        except Exception as e:
            run = False
            logging.getLogger("Client").error("Couldn't get game: %s", e)
            break
       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        game.draw(screen)
        pygame.display.update()



main()