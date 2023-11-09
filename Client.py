import pygame
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

    print("You are player", playerId)

    clock = pygame.time.Clock()

    while run:
        clock.tick(60)

        try:
            game = n.send("get")
        except:
            run = False
            print("Couldn't get game")
            break
       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        game.draw(screen)
        pygame.display.update()



main()