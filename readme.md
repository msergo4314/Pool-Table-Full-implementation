# Physics-Based Pool Ball Simulation

This project is a physics-based simulation of a game of billiards/pool/snooker. It uses an optimized C library (`phylib.c` and `phylib.h`) to simulate collisions between balls and balls falling into holes through OOP-like union objects. The game is played on a browser with two players and uses a highly optimized database to store data. Currently, the data cannot be retrieved, but adding such functionality would be simple since the database already tracks player names, shots, games, etc. The remainder of the project is written primarily in Python, as other operations do not need to be highly optimized.

## Project Components

- **Server**: Localhost HTTP server
- **C Library Integration**: The integration of the C library into Python (using SWIG)
- **Database**: SQLite database (`sqlite3`)
- **Webpage Logic**: `game.js` communicates with `server.py` through the `ServerGame` class, which extends the `Physics.Game` class (this class wraps the C code into callable Python functions)
- **Styling**: `style.css`
- **SWIG Interface File**: `phylib.i` is used by SWIG to link the library into Python files
- **Makefile**: Automates the file generation

## Dependencies

- **Operating System**: Requires Linux to run. If you are using Windows, use WSL.
- **SWIG**: Requires SWIG and a recent version of Python (3.11 was used, but future versions should be okay). Install with:
  ```bash
  sudo apt install swig
  sudo apt install python3.11-dev
  ```
- **Clang**: Required, but you can use GCC if you modify the compiler in the makefile. Install with:
  ```bash
  sudo apt install clang
  ```

## Bugs

- **Shoot Function Infinite Loop**: Under certain conditions, the shoot function can enter an infinite loop and break the game. This seems to occur for very high-velocity shots, likely caused by balls clipping into each other and messing with the physics. Fixing this would require changing the underlying physics functions. It seems to have about a 5% chance of occurring.

## File Overview

- **phylib.c** and **phylib.h**: Optimized C library for simulating physics.
- **game.js**: Webpage logic.
- **server.py**: Server-side logic.
- **style.css**: Styling for the webpage.
- **phylib.i**: SWIG interface file.
- **Makefile**: Automates the file generation and compilation process.

## Running the Project

1. Install the required dependencies.
2. Compile the C library using the makefile.
3. Run the server and open the game in a web browser.
