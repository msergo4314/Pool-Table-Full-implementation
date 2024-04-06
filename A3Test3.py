import math
import random
from time import perf_counter
import sys
import Physics
NUM = 1

def make_default_table() -> Physics.Table:
    
    def millimeter_offset() -> float:
        return 14.0
    
    # Setup the table
    table_to_return = Physics.Table()  # Create a new table

    # Define the number of rows and balls per row
    import math
    ball_ordering = [1, 2, 9, 3, 8, 10, 4, 14, 7, 11, 12, 6, 15, 13, 5]

    root_3 = math.sqrt(3.0)
    for row in range(5):
        for ball in range(row + 1):
            x = Physics.TABLE_WIDTH / 2.0 + (ball - (row + 1) / 2.0) * (Physics.BALL_DIAMETER + millimeter_offset())
            y = Physics.TABLE_WIDTH / 2.0 - root_3 / 2.0 * (Physics.BALL_DIAMETER + millimeter_offset()) * row
            current_ball_number = ball_ordering.pop(0)
            pos = Physics.Coordinate(x, y)
            sb = Physics.StillBall(current_ball_number, pos)
            table_to_return += sb

    # Add cue ball
    pos = Physics.Coordinate(Physics.TABLE_WIDTH / 2.0, Physics.TABLE_LENGTH - Physics.TABLE_WIDTH / 2.0)
    sb = Physics.StillBall(0, pos)
    table_to_return += sb
    return table_to_return


def main():
    # print("initial table looks like:" + str(table))
    if "reset" in sys.argv:
        print("resetting db")
        db = Physics.Database(reset=True)
        del db
    game = Physics.Game(gameName=f"Game {NUM:02}", player1Name="Stefan", player2Name="Efren Reyes")
    special = True if len(sys.argv) > 2 else False
    RANGE = 5000
    LOOP = 100
    x_rand = [round(random.uniform(RANGE/2, RANGE), 4) for i in range(LOOP)]
    y_rand = [round(random.uniform(RANGE/2, RANGE), 4) for i in range(LOOP)]
    
    # x_rand = [int(random.uniform(-RANGE, RANGE)) for i in range(100)]
    # y_rand = [int(random.uniform(-RANGE, RANGE)) for i in range(100)]
    
    start1 = perf_counter()
    if special:
        game.shoot("Stefan", make_default_table(), 0, -1000)
    else:
        for i in range(LOOP):
            game.shoot(game.player1_name if i % 2 == 0 else game.player2_name, make_default_table(), x_rand[i], y_rand[i])
            # print(f"VEL: {x_rand[i]}, {y_rand[i]}\n")
            
    # print("SPECIAL CASE")
    # game.shoot(game.game_Name, game.player1_name, make_table(), -300, 2680)
    print(f"total time for {LOOP} shoots: {perf_counter() - start1:6f}\n")
    start = perf_counter()
    x = 0
    for i in range(1 + LOOP * (NUM - 1), LOOP + 1 + LOOP * (NUM - 1)):
        x += game.get_number_of_tables_for_shot(i)
    print(f"There were {x} tables added to the database for game ID = {game.game_ID}\n")
    print(f"total time for counting shoots: {perf_counter() - start:6f}")
    
    start2 = perf_counter()
    game.database.open_cursor()
    
    for i in range(x):
        game.database.readTable(i)
    
    print(f"time for reads: {(perf_counter() - start2):6f}")
    print(f"time for all: {(perf_counter() - start1):6f}")
    print(f"TOTAL NUMBER OF TABLES IN DB: {game.get_total_number_of_tables_in_database()}")
    game.close()
    
if __name__ == '__main__':
    main()