"""
Sokoban Solver using SAT (Boilerplate)
--------------------------------------
Instructions:
- Implement encoding of Sokoban into CNF.
- Use PySAT to solve the CNF and extract moves.
- Ensure constraints for player movement, box pushes, and goal conditions.

Grid Encoding:
- 'P' = Player
- 'B' = Box
- 'G' = Goal
- '#' = Wall
- '.' = Empty space
"""

from pysat.formula import CNF
from pysat.solvers import Solver

# Directions for movement
DIRS = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}


class SokobanEncoder:
    def __init__(self, grid, T):
        """
        Initialize encoder with grid and time limit.

        Args:
            grid (list[list[str]]): Sokoban grid.
            T (int): Max number of steps allowed.
        """
        self.grid = grid
        self.T = T
        self.N = len(grid)
        self.M = len(grid[0])

        self.goals = []
        self.boxes = []
        self.player_start = None
        self.non_walls = []

        # TODO: Parse grid to fill self.goals, self.boxes, self.player_start
        self._parse_grid()

        self.num_boxes = len(self.boxes)
        self.cnf = CNF()

    def _parse_grid(self):
        """Parse grid to find player, boxes, and goals."""
        # TODO: Implement parsing logic
        for r in range(self.N):
            for c in range(self.M):
                if self.grid[r][c] == "#":
                    continue

                char = self.grid[r][c]
                if char == 'P':
                    self.player_start = (r,c)
                elif char == 'B':
                    self.boxes.append((r,c))
                elif char == 'G':
                    self.goals.append((r,c))

                self.non_walls.append((r,c))
    

    # ---------------- Variable Encoding ----------------
    def var_player(self, x, y, t):
        """
        Variable ID for player at (x, y) at time t.
        """
        # TODO: Implement encoding scheme

        return (t * self.N * self.M) + (x * self.M) + y + 1

    def var_box(self, b, x, y, t):
        """
        Variable ID for box b at (x, y) at time t.
        """
        # TODO: Implement encoding scheme
        player_offset = (self.T + 1) * self.N * self.M # All player variables ,maximum value of var_player
        box_offset = b * player_offset # variable for box distincttion
        time_space_offset = (t * self.N * self.M) + (x * self.M) + y + 1 # for each box all variables 

        return player_offset + box_offset + time_space_offset

    # ---------------- Encoding Logic ----------------
    def encode(self):
        """
        Build CNF constraints for Sokoban:
        - Initial state
        - Valid moves (player + box pushes)
        - Non-overlapping boxes
        - Goal condition at final timestep
        """
        # TODO: Add constraints for:
        # 1. Initial conditions
        # 2. Player movement
        # 3. Box movement (push rules)
        # 4. Non-overlap constraints
        # 5. Goal conditions
        # 6. Other conditions\
        # Initial conditions
        self.cnf.append([self.var_player(self.player_start[0],self.player_start[1],0)])
        for b, coords in enumerate(self.boxes):
            r, c = coords 
            box_var = self.var_box(b, r, c, 0)
            self.cnf.append([box_var])

        # At most one
        for T in range(self.T + 1):
            for indices in self.non_walls:
                r1,c1 = indices
                for indices2 in self.non_walls:
                    r2,c2 = indices2
                    if (r1,c1) < (r2,c2):
                        player_var_1 = self.var_player(r1,c1,T)
                        player_var_2 = self.var_player(r2,c2,T)
                        self.cnf.append([-player_var_1,-player_var_2])
                        for b in range(self.num_boxes):
                            box_var_1 = self.var_box(b,r1,c1,T)
                            box_var_2 = self.var_box(b,r2,c2,T)
                            self.cnf.append([-box_var_1,-box_var_2])


        # At least one place the object should exists
        for T in range(self.T + 1):
            player_clause = []
            for indices in self.non_walls:
                r,c = indices
                player_var = self.var_player(r,c,T)
                player_clause.append(player_var)

            self.cnf.append(player_clause)

            for b in range(self.num_boxes):
                box_clause = []
                for indices in self.non_walls:
                    r,c = indices
                    box_var = self.var_box(b,r,c,T)
                    box_clause.append(box_var)

                self.cnf.append(box_clause)

        #No two objects should be in same box
        for T in range(self.T+1):
            for indices in self.non_walls:
                r,c = indices
                player_var = self.var_player(r,c,T)
                for b in range(self.num_boxes):
                   box_var = self.var_box(b,r,c,T)
                   self.cnf.append([-player_var,-box_var])
                
                for b1 in range(self.num_boxes):
                    box_var_1 = self.var_box(b1,r,c,T)
                    for b2 in range(b1+1,self.num_boxes):
                        box_var_2 = self.var_box(b2,r,c,T)
                        self.cnf.append([-box_var_1,-box_var_2])

        # transition rules Box movement 
        # player can be only move to adjacent squares
        for T in range(self.T):
            for indices in self.non_walls:
                r,c = indices
                possible_previous_cells = []
                for indices2 in DIRS.values():
                    dr,dc = indices2
                    previous_r, previous_c = r - dr, c - dc
                    if (previous_r, previous_c) in self.non_walls:
                        possible_previous_cells.append(self.var_player(previous_r,previous_c,T))
                self.cnf.append([-self.var_player(r,c,T+1)] + possible_previous_cells)

        # pushing conditions
        for T in range(self.T):
            for indices in self.non_walls:
                r,c = indices
                for indices2 in DIRS.values():
                    ar,ac = indices2
                    player_next_pos = (r+ar,c+ac)
                    box_final_pos = (r+2*ar,c+2*ac)
                    if player_next_pos in self.non_walls and box_final_pos in self.non_walls:
                        for b in range(self.num_boxes):
                            self.cnf.append([-self.var_player(r, c, T),-self.var_box(b, player_next_pos[0], player_next_pos[1], T),-self.var_player(player_next_pos[0], player_next_pos[1], T + 1),self.var_box(b, box_final_pos[0], box_final_pos[1], T + 1)])

        # Inertia 
        # box is not pushed 
        for T in range(self.T):
            for indices in self.non_walls:
                r,c = indices
                for b in range(self.num_boxes):
                    pushed_conditions = []
                    for indices2 in DIRS.values():
                        pr,pc = r - indices2[0], c - indices2[1]
                        if (pr,pc) in self.non_walls:
                            push_action_another_var = self.cnf.nv + 1
                            self.cnf.nv += 1
                            self.cnf.append([-self.var_player(pr, pc, T), -self.var_player(r, c, T+1), push_action_another_var])
                            self.cnf.append([self.var_player(pr, pc, T), -push_action_another_var])
                            self.cnf.append([self.var_player(r, c, T+1), -push_action_another_var])
                            pushed_conditions.append(push_action_another_var)
                    self.cnf.append([-self.var_box(b, r, c, T)] + pushed_conditions + [self.var_box(b, r, c, T+1)])

        #invalid pushes
        for T in range(self.T):
            for indices in self.non_walls:
                r,c = indices
                for indices2 in DIRS.values():
                    ar , ac = indices2
                    br , bc = r + ar , c + ac
                    cr , cc = ar + br , ac + bc 
                    if (br,bc) in self.non_walls:
                        #pushing into a wall
                        if (cr,cc) not in self.non_walls:
                            for b in range(self.num_boxes):
                                self.cnf.append([-self.var_player(r, c, T), -self.var_box(b, br, bc, T), -self.var_player(br, bc, T + 1)])
                        #pushing into another box
                        else :
                            for b1 in range(self.num_boxes):
                                for b2 in range(self.num_boxes):
                                    if b1 == b2: continue
                                    self.cnf.append([-self.var_player(r, c, T), -self.var_box(b1, br, bc, T), -self.var_box(b2, cr, cc, T), -self.var_player(br, bc, T + 1)])

        #final goal condition
        for b in range(self.num_boxes):
            goal_clause = []
            for gr,gc in self.goals:
                goal_clause.append(self.var_box(b, gr, gc, self.T))
            self.cnf.append(goal_clause)

        return self.cnf
def decode(model, encoder):
    """
    Decode SAT model into list of moves ('U', 'D', 'L', 'R').

    Args:
        model (list[int]): Satisfying assignment from SAT solver.
        encoder (SokobanEncoder): Encoder object with grid info.

    Returns:
        list[str]: Sequence of moves.
    """
    N, M, T = encoder.N, encoder.M, encoder.T
    moves = []
    player_path = [None] * (T + 1)
    player_vars_count = (T + 1) * N * M
    for v in model:
        if 0 < v <= player_vars_count:
            base_v = v - 1 
            t = base_v // (N * M)
            remainder = base_v % (N * M)
            r = remainder // M
            c = remainder % M
            if t < len(player_path):
                player_path[t] = (r, c)


    for t in range(T):
        if player_path[t] is None or player_path[t+1] is None:
            break
        r1, c1 = player_path[t]
        r2, c2 = player_path[t+1]
        dr, dc = r2 - r1, c2 - c1
        if (dr, dc) == (0,0): continue
        for char, (mr, mc) in DIRS.items():
            if (dr, dc) == (mr, mc):
                moves.append(char)
                break
    return moves


def solve_sokoban(grid, T):
    """
    DO NOT MODIFY THIS FUNCTION.
 
    Solve Sokoban using SAT encoding.

    Args:
        grid (list[list[str]]): Sokoban grid.
        T (int): Max number of steps allowed.

    Returns:
        list[str] or "unsat": Move sequence or unsatisfiable.
    """
    encoder = SokobanEncoder(grid, T)
    cnf = encoder.encode()

    with Solver(name='g3') as solver:
        solver.append_formula(cnf)
        if not solver.solve():
            return -1

        model = solver.get_model()
        if not model:
            return -1

        return decode(model, encoder)


if __name__ == "__main__":
    # --- Your original tests (left as-is) ---
    print(solve_sokoban([['P', '.', '.'], ['.', 'B', '.'], ['.', '.', 'G']], 5))
    print(solve_sokoban([["P", ".", ".", ".", "."], [ ".", ".", ".", ".", "."], [ ".", ".","G", ".", "."], [ ".", ".", ".","B", "."], [ ".", ".", ".", ".", "."]], 11))
    print(solve_sokoban([["P", ".", ".", ".", ".", "."], [".", ".", ".", ".", ".", "."], [".", "B", ".", ".", "G", "."], [".", ".", ".", ".", ".", "."], [".", ".", "B", ".", ".", "G"], [".", ".", ".", ".", ".", "."]], 12))
    print(solve_sokoban([["#", "#", "#", "#", "#", "#"], ["#", "P", ".", ".", "G", "#"], ["#", ".", "B", ".", ".", "#"], ["#", ".", ".", ".", ".", "#"], ["#", "G", ".", "B", ".", "#"], ["#", "#", "#", "#", "#", "#"]], 10))
    print(solve_sokoban([["G", ".", ".", ".", ".", "G"], [".", ".", ".", ".", ".", "."], [".", "B", ".", ".", "B", "."], ["P", ".", ".", ".", ".", "."], [".", ".", ".", ".", ".", "."], [".", ".", ".", ".", ".", "."]], 15))
    print(solve_sokoban([[".", ".", ".", ".", ".", "."],
                        [".", "P", ".", ".", ".", "."],
                        [".", "B", ".", "B", ".", "."],
                        [".", ".", ".", ".", ".", "."], 
                        [".", "G", ".", "G", ".", "."], 
                        [".", ".", "B", ".", ".", "G"]], 16))
    print(solve_sokoban([['P', '.', '.'], ['.', 'G', '.'], ['.', '.', 'B']], 99))
    print(solve_sokoban([["#", "#", "#", "#", "#", "#", "#"],
                        ["#", "P", ".", "#", ".", ".", "#"], 
                        ["#", ".", "B", "#", "G", ".", "#"], 
                        ["#", ".", ".", "#", ".", ".", "#"], 
                        ["#", "G", ".", "B", ".", ".", "#"], 
                        ["#", "#", "#", "#", "#", "#","#"]],99))
