import pygame

class MAMOAC:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
    
        pygame.quit()

def main():
    app = MAMOAC()
    app.run()

if __name__ == "__main__":
    main()