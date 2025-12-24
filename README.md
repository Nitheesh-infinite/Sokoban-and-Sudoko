# SAT-Based Puzzle Solvers (Sudoku & Sokoban)

This repository contains two logic-based puzzle solvers that utilize Boolean Satisfiability (SAT) encoding. By translating the rules of Sudoku and the movement logic of Sokoban into Conjunctive Normal Form (CNF), we leverage the `PySAT` library to find valid solutions.

## 👥 Authors
* **Nitheesh Kumar Vennela**
* **M Sai Siva Lochan**

---

## 📂 Repository Structure

The project is organized into two main directories. Each folder is a self-contained solver with its own logic and test cases.

```text
.
├── LICENSE
├── README.md
├── SAT-Based Sokoban Solver/
│   ├── input/              # Input test cases for Sokoban levels
│   ├── output/             # Generated output solutions
│   ├── README.md           # Local running instructions
│   ├── Sokoban.py          # Core logic for Sokoban-to-SAT encoding
│   └── tester.py           # Tester script for Sokoban
└── SAT-Based Sudoku Solver/
    ├── pysat_tutorial.md   # Guide for using the PySAT library
    ├── README.md           # Local running instructions
    ├── testcases/          # Input test cases for Sudoku grids
    ├── Sudoku.py           # Core logic for Sudoku-to-SAT encoding
    └── tester.py           # Tester script for Sudoku

```
## 🛠️ Installation & Setup

### Install Dependencies

Ensure your virtual environment is active (you should see `(venv)` in your terminal), then install **PySAT**:

```bash
pip install --upgrade pip
pip install python-sat[pblib,aiger]
```