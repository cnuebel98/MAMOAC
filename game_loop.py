import pygame
from mc_simulator import MCSimulator

class GameLoop:
    @staticmethod
    def run(grid, grid_renderer, agent1, agent2):
        clock = pygame.time.Clock()
        running = True

        # States to track input mode
        agent1_mode = 'move'  # Options: 'move', 'shift'
        agent2_mode = 'move'  # Options: 'move', 'shift'

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Agent1 controls (WASD + QE for movement in 6 directions)
                if event.type == pygame.KEYDOWN:
                    if agent1:
                        if event.key == pygame.K_SPACE:
                            #print("Simulation Started.")      
                            # Trigger Monte Carlo Simulation when space bar is pressed
                            # repeat the steps below 10 times
                            for _ in range(10):
                                mc_simulator = MCSimulator(agent1, grid, simu_depth=100, time_limit=1, max_rollouts=4000000)
                                best_move, best_shift = mc_simulator.simulate()
                                print((best_move, best_shift))
                                if agent1_mode == 'move':
                                    agent1.move(best_move, grid)
                                    agent1_mode = 'shift_obstacle'
                                if agent1_mode == 'shift_obstacle':
                                    agent1.shift_obstacle(best_shift, grid)
                                    agent1_mode = 'move'
                                best_move, best_shift = None, None 
                                #update the screen with grid and agent
                                grid_renderer.draw()
                                agent1.draw(grid_renderer.screen, grid)
                                pygame.display.flip()
                        if event.key in [pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_q, pygame.K_e]:
                            if agent1_mode == 'move':
                                # Handle the agent's movement
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

                                # Switch to obstacle shifting mode if necessary
                                if grid.grid[agent1.row][agent1.col]['weight']:
                                    agent1_mode = 'shift_obstacle'
                                else:
                                    agent1_mode = 'move'

                            elif agent1_mode == 'shift_obstacle':
                                if grid.grid[agent1.row][agent1.col]['weight']:
                                    if event.key == pygame.K_w:
                                        agent1.shift_obstacle("up", grid)
                                    elif event.key == pygame.K_s:
                                        agent1.shift_obstacle("down", grid)
                                    elif event.key == pygame.K_a:
                                        agent1.shift_obstacle("bottom_left", grid)
                                    elif event.key == pygame.K_d:
                                        agent1.shift_obstacle("bottom_right", grid)
                                    elif event.key == pygame.K_q:
                                        agent1.shift_obstacle("top_left", grid)
                                    elif event.key == pygame.K_e:
                                        agent1.shift_obstacle("top_right", grid)
                                if agent1.successful_shift:    
                                    agent1_mode = 'move'

                    # Agent2 controls (same logic as Agent1 but with different keys)
                    if agent2:
                        if event.key in [pygame.K_i, pygame.K_k, pygame.K_j, pygame.K_l, pygame.K_u, pygame.K_o]:
                            if agent2_mode == 'move':
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

                                if grid.grid[agent2.row][agent2.col]['weight']:
                                    agent2_mode = 'shift_obstacle'
                                else:
                                    agent2_mode = 'move'

                            elif agent2_mode == 'shift_obstacle':
                                if grid.grid[agent2.row][agent2.col]['weight']:
                                    if event.key == pygame.K_i:
                                        agent2.shift_obstacle("up", grid)
                                    elif event.key == pygame.K_k:
                                        agent2.shift_obstacle("down", grid)
                                    elif event.key == pygame.K_j:
                                        agent2.shift_obstacle("bottom_left", grid)
                                    elif event.key == pygame.K_l:
                                        agent2.shift_obstacle("bottom_right", grid)
                                    elif event.key == pygame.K_u:
                                        agent2.shift_obstacle("top_left", grid)
                                    elif event.key == pygame.K_o:
                                        agent2.shift_obstacle("top_right", grid)
                                if agent2.successful_shift:
                                    agent2_mode = 'move'

            # Render the grid and agents
            grid_renderer.draw()

            if agent1:
                agent1.draw(grid_renderer.screen, grid)
            
            if agent2:
                agent2.draw(grid_renderer.screen, grid)

            pygame.display.flip()
            clock.tick(60)  # 60 FPS

        pygame.quit()
