"""
sudoku_solver.py

Implement the function `solve_sudoku(grid: List[List[int]]) -> List[List[int]]` using a SAT solver from PySAT.
"""

from pysat.formula import CNF
from pysat.solvers import Solver
from typing import List

def solve_sudoku(grid: List[List[int]]) -> List[List[int]]:
    """Solves a Sudoku puzzle using a SAT solver. Input is a 2D grid with 0s for blanks."""

    # TODO: implement encoding and solving using PySAT
    cnf = CNF();
    
    #at least one of each digit per row
    for i in range(9):
        for k in range(9):
            my_list : List[int] = []
            for j in range(9):
                c = i*81+j*9+k+1
                my_list.append(c)
            cnf.append(my_list)

    #at least one of each digit per row
    for j in range(9):
        for k in range(9):
            my_list : List[int] = []
            for i in range(9):
                c = i*81+j*9+k+1
                my_list.append(c)
            cnf.append(my_list)
    # at least one of each digit per 3x3 box
    for k in range(9):
        for m in range(3):
            for n in range(3):
                my_list : list[int] = []
                for i in range(m*3, m*3 + 3): 
                    for j in range(n*3, n*3 + 3): 
                        c = i*81 + j*9 + k + 1
                        my_list.append(c)
                cnf.append(my_list)

    #every cell must have at least one number.
    for i in range(9):
        for j in range(9):
            cnf.append([i*81 + j*9 + k + 1 for k in range(9)])
            
    #at most one number per cell
    for i in range(9):
        for j in range(9):
            for k in range(9):
                for l in range(k+1,9):
                    my_list : List[int] = []
                    d = -(i*81+j*9+k+1)
                    c = -(i*81+j*9+l+1)
                    my_list.append(d)
                    my_list.append(c)
                    cnf.append(my_list)
    #at most one of each digit per row
    for i in range(9):
        for k in range(9):
            for j1 in range(9):
                for j2 in range(j1 + 1, 9): 
                    cnf.append([-(i*81 + j1*9 + k + 1), -(i*81 + j2*9 + k + 1)])

    #at most one of each digit per column
    for j in range(9): 
        for k in range(9):
            for i1 in range(9):
                for i2 in range(i1 + 1, 9): 
                    cnf.append([-(i1*81 + j*9 + k + 1), -(i2*81 + j*9 + k + 1)])
    
    # initial grid numbers as facts
    for row_idx, row in enumerate(grid):
        for col_idx, number in enumerate(row):
            if number != 0:
                c = row_idx*81+col_idx*9 + (number - 1) + 1 
                cnf.append([c])

    solution = None
    with Solver(name='glucose3') as solver:
        solver.append_formula(cnf.clauses)
        if solver.solve():
            model = solver.get_model()
            solution = [[0]*9 for _ in range(9)]
            for lit in model:
                if lit > 0:
                    lit -= 1
                    r = lit // 81
                    c = (lit % 81) // 9
                    d = lit % 9
                    solution[r][c] = d + 1
        else:
            print("UNSAT")
    
    return solution if solution else []