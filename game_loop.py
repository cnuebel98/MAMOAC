import pygame

class GameLoop:
    @staticmethod
    def run(grid, agent1, agent2):
        clock = pygame.time.Clock()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Agent1 controls (WASD + QE for movement in 6 directions)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        agent1.move("up", grid)
                    elif event.key == pygame.K_s:
                        agent1.move("down", grid)
                    elif event.key == pygame.K_a:
                        agent1.move("bottom_left", grid)
                    elif event.key == pygame.K_d:
                        agent1.move("bottom_right", grid)
                    elif event.key == pygame.K_q:
                        agent1.move("top_left", grid)
                    elif event.key == pygame.K_e:
                        agent1.move("top_right", grid)

                    # Agent2 controls (IJKL + UO for movement in 6 directions)
                    if event.key == pygame.K_i:
                        agent2.move("up", grid)
                    elif event.key == pygame.K_k:
                        agent2.move("down", grid)
                    elif event.key == pygame.K_j:
                        agent2.move("bottom_left", grid)
                    elif event.key == pygame.K_l:
                        agent2.move("bottom_right", grid)
                    elif event.key == pygame.K_u:
                        agent2.move("top_left", grid)
                    elif event.key == pygame.K_o:
                        agent2.move("top_right", grid)

            # Draw grid and agents
            grid.draw()
            agent1.draw(grid.screen, grid)
            agent2.draw(grid.screen, grid)

            pygame.display.flip()
            clock.tick(60)  # 60 FPS
        pygame.quit()
