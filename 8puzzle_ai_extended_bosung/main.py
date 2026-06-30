import pygame

from config import WIDTH, HEIGHT, BG, FPS, START, GOAL
from puzzle import apply_move, valid_moves, manhattan

from solvers.backtracking import Backtracking
from solvers.forward_checking import ForwardChecking
from solvers.and_or import AndOr


# ================= INIT =================
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

mode = "backtracking"
auto = False

solver = Backtracking(START, GOAL)


# ================= BUTTON =================
def handle_click(pos):
    global mode, solver

    if 50 <= pos[0] <= 190 and 20 <= pos[1] <= 60:
        mode = "backtracking"
        solver = Backtracking(solver.state, GOAL)

    elif 250 <= pos[0] <= 390 and 20 <= pos[1] <= 60:
        mode = "forward"
        solver = ForwardChecking(solver.state, GOAL)

    elif 400 <= pos[0] <= 540 and 20 <= pos[1] <= 60:
        mode = "andor"
        solver = AndOr(solver.state, GOAL)


# ================= DRAW =================
def draw(screen, state):
    screen.fill(BG)

    font = pygame.font.SysFont("arial", 22)

    buttons = [("Backtracking", 50), ("Forward", 250), ("AND/OR", 400)]

    for text, x in buttons:
        pygame.draw.rect(screen, (80,80,100), (x,20,140,40))
        screen.blit(font.render(text, True, (255,255,255)), (x+10, 30))

    # board
    size = 120
    ox, oy = WIDTH//2 - 180, HEIGHT//2 - 180

    font2 = pygame.font.SysFont("arial", 50)

    for i,v in enumerate(state):
        r, c = divmod(i,3)

        rect = pygame.Rect(ox+c*size, oy+r*size, size, size)

        pygame.draw.rect(screen, (40,45,55), rect)
        pygame.draw.rect(screen, (120,120,140), rect, 2)

        if v != 0:
            t = font2.render(str(v), True, (255,255,255))
            screen.blit(t, t.get_rect(center=rect.center))


# ================= LOOP =================
running = True

while running:
    clock.tick(FPS)

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

        # CLICK BUTTON
        if e.type == pygame.MOUSEBUTTONDOWN:
            handle_click(e.pos)

        # SPACE = STEP
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_SPACE:
                solver.step()

            if e.key == pygame.K_a:
                auto = not auto


    # AUTO RUN
    if auto:
        solver.step()

    draw(screen, solver.state)
    pygame.display.flip()

pygame.quit()