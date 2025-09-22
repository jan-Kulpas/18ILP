# 18XX Improved Logistics Pathfinder (18ILP)

**18ILP** is an optimal route finder and calculator for 18XX board games. It currently supports *Shikoku 1889* and uses a Integer Linear Programming (ILP) solver to determine the most profitable train routes for a given game state.

Please note that this app is **heavily WIP** so there is no proper documentation yet and things may break.  

## Features

- Full support for Shikoku 1889
- Qt6 User Interface
- Tile placement on the game board
- Purchasing trains by railways, along with train rusting
- Optimal route display on the map
- Board state save and loading to .json file

## How It Works

After converting the board state to a graph, 18xx Router creates decision variables for whether a given node or edge belongs to each trains route. This is then fed along with constraints based on the *Shikoku 1889* ruleset to the CBC solver which returns the optimal solution to the linear problem. See `solver/pathfinder.py` for the various constraints.

## Usage

After cloning, set up a venv and install all required dependencies, then run the app using the following command in the cloned folder:

``` bash
python -m main
```
