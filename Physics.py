import phylib
from typing import Union
from time import perf_counter
from math import hypot, floor
# other libraries imported later: sqlite3, math, os, time

################################################################################
# header and footer for svg function

SHOW_BALL_NUMBERS_ON_TABLE : bool = False

HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg id="poolTable" width="700" height="1375" viewBox="-25 -25 1400 2750"
xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink">
<rect width="1350" height="2700" x="0" y="0" fill="#0e3b0d" />"""

FOOTER = """</svg>\n"""

################################################################################
# import constants from phylib to global varaibles (some new constants)

FRAME_INTERVAL = phylib.PHYLIB_FRAME_INTERVAL # constant frame rate for database operations
BALL_RADIUS    = phylib.PHYLIB_BALL_RADIUS
BALL_DIAMETER  = phylib.PHYLIB_BALL_DIAMETER
HOLE_RADIUS    = phylib.PHYLIB_HOLE_RADIUS
TABLE_LENGTH   = phylib.PHYLIB_TABLE_LENGTH
TABLE_WIDTH    = phylib.PHYLIB_TABLE_WIDTH
SIM_RATE       = phylib.PHYLIB_SIM_RATE
VEL_EPSILON    = phylib.PHYLIB_VEL_EPSILON
DRAG           = phylib.PHYLIB_DRAG
MAX_TIME       = phylib.PHYLIB_MAX_TIME
MAX_OBJECTS    = phylib.PHYLIB_MAX_OBJECTS

################################################################################
# the standard colours of pool balls
# if you are curious check this out:  
# https://billiards.colostate.edu/faq/ball/colors/

BALL_COLOURS = [ 
    "WHITE",
    "YELLOW",
    "BLUE",
    "RED",
    "PURPLE",
    "ORANGE",
    "GREEN",
    "BROWN",
    "BLACK",
    "LIGHTYELLOW",
    "LIGHTBLUE",
    "PINK",             # no LIGHTRED
    "MEDIUMPURPLE",     # no LIGHTPURPLE
    "LIGHTSALMON",      # no LIGHTORANGE
    "LIGHTGREEN",
    "SANDYBROWN",       # no LIGHTBROWN, 16 colours total
    ]

################################################################################
class Coordinate(phylib.phylib_coord):
    """
    This creates a Coordinate subclass, that adds nothing new, but looks
    more like a nice Python class.
    """
    pass

################################################################################
class StillBall(phylib.phylib_object):
    """
    Python StillBall class.
    """
    def __init__(self, number, pos):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """
        # this creates a generic phylib_object
        phylib.phylib_object.__init__(self, 
                                       phylib.PHYLIB_STILL_BALL, 
                                       number, 
                                       pos, None, None, 
                                       0.0, 0.0)
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = StillBall


    # add an svg method here
    def svg(self):
        cx: int = self.obj.still_ball.pos.x
        cy: int = self.obj.still_ball.pos.y
        svg_str: str = f"""<circle cx="{cx}" cy="{cy}" r="{BALL_RADIUS}" fill="{BALL_COLOURS[self.obj.still_ball.number]}" />\n"""
        if self.obj.still_ball.number and SHOW_BALL_NUMBERS_ON_TABLE:
            svg_str += f"""<circle cx="{cx}" cy="{cy}" r="{BALL_RADIUS/2}" fill="white" />\n"""
            svg_str += f"""<text x="{cx}" y="{cy + 4}" text-anchor="middle" alignment-baseline="middle" fill="black" font-size="{BALL_RADIUS/2}px" font-weight="bold" pointer-events="none">{self.obj.still_ball.number}</text>"""
        return svg_str

################################################################################
class RollingBall(phylib.phylib_object):
    """
    Python RollingBall class.
    """

    def __init__(self, number, pos, vel, acc):
        """
        Constructor function. Requires ball number, position, velocity, and acceleration
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__(self, 
                                       phylib.PHYLIB_ROLLING_BALL, 
                                       number, 
                                       pos, vel, acc, 
                                       0.0, 0.0)
      
        # this converts the phylib_object into a RollingBall class
        self.__class__ = RollingBall

    # add an svg method here
    def svg(self):
        cx: int = self.obj.still_ball.pos.x
        cy: int = self.obj.still_ball.pos.y
        svg_str: str = f"""<circle cx="{cx}" cy="{cy}" r="{BALL_RADIUS}" fill="{BALL_COLOURS[self.obj.rolling_ball.number]}" />\n"""
        if self.obj.rolling_ball.number and SHOW_BALL_NUMBERS_ON_TABLE:
            svg_str += f"""<circle cx="{cx}" cy="{cy}" r="{BALL_RADIUS/2}" fill="white" />\n"""
            svg_str += f"""<text x="{cx}" y="{cy + 4}" text-anchor="middle" alignment-baseline="middle" fill="black" font-size="{BALL_RADIUS/2}px" font-weight="bold" pointer-events="none">{self.obj.rolling_ball.number}</text>"""
        return svg_str

################################################################################
class Hole(phylib.phylib_object):
    """
    Python Hole class.
    """

    def __init__(self, pos):
        """
        Constructor function. Requires hole position
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__(self, 
                                       phylib.PHYLIB_HOLE, 
                                       0, 
                                       pos, None, None, 
                                       0.0, 0.0)
      
        # this converts the phylib_object into a Hole class
        self.__class__ = Hole

    # add an svg method here
    def svg(self):
        return """ <circle cx="%d" cy="%d" r="%d" fill="black" />\n""" %\
        (self.obj.hole.pos.x,self.obj.hole.pos.y, HOLE_RADIUS)

################################################################################
class HCushion(phylib.phylib_object):
    """
    Python HCushion class.
    """

    def __init__(self, y):
        """
        Constructor function. Requires y position only
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__(self, 
                                       phylib.PHYLIB_HCUSHION, 
                                       0, 
                                       None, None, None, 
                                       0.0, y)
      
        # this converts the phylib_object into a HCushion class
        self.__class__ = HCushion

    # add an svg method here
    
    def svg(self):
        return """ <rect width="1400" height="25" x="-25" y="%d" fill="#7c3f00" />\n""" \
        % (-25 if self.obj.hcushion.y == 0.0 else 2700)

################################################################################
class VCushion(phylib.phylib_object):
    """
    Python VCushion class.
    """

    def __init__(self, x):
        """
        Constructor function. Requires x position as only argument
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__(self, 
                                       phylib.PHYLIB_VCUSHION, 
                                       0, 
                                       None, None, None, 
                                       x, 0.0)
      
        # this converts the phylib_object into a VCushion class
        self.__class__ = VCushion

    # add an svg method here
    def svg(self):
        return """ <rect width="25" height="2750" x="%d" y="-25" fill="#7c3f00" />\n""" % (-25 if self.obj.vcushion.x == 0.0 else 1350)

################################################################################
class Table(phylib.phylib_table):
    """
    Pool table class.
    """
    
    def __init__(self):
        """
        Table constructor method.
        This method call the phylib_table constructor and sets the current
        object index to -1.
        """
        self.current = -1
        phylib.phylib_table.__init__(self)
        
    def __iadd__(self, other):
        """
        += operator overloading method.
        This method allows you to write "table+=object" to add another object
        to the table.
        """
        self.add_object(other)
        return self

    def __iter__(self):
        """
        This method adds iterator support for the table.
        This allows you to write "for object in table:" to loop over all
        the objects in the table.
        """
        # this code is called before every "for object in table" starts so set current as needed
        self.current = -1
        return self

    def __next__(self):
        """
        This provides the next object from the table in a loop.
        """
        self.current += 1  # increment the index to the next object
        if self.current < MAX_OBJECTS:   # check if there are no more objects
            return self[ self.current ] # return the latest object

        # if we get there then we have gone through all the objects
        raise StopIteration  # raise StopIteration to tell for loop to stop

    def __getitem__(self, index):
        """
        This method adds item retreivel support using square brackets [ ] .
        It calls get_object (see phylib.i) to retreive a generic phylib_object
        and then sets the __class__ attribute to make the class match
        the object type.
        """
        result = self.get_object(index) 
        if result==None:
            return None
        if result.type == phylib.PHYLIB_STILL_BALL:
            result.__class__ = StillBall
        if result.type == phylib.PHYLIB_ROLLING_BALL:
            result.__class__ = RollingBall
        if result.type == phylib.PHYLIB_HOLE:
            result.__class__ = Hole
        if result.type == phylib.PHYLIB_HCUSHION:
            result.__class__ = HCushion
        if result.type == phylib.PHYLIB_VCUSHION:
            result.__class__ = VCushion
        return result

    def __str__(self):
        """
        Returns a string representation of the table that matches
        the phylib_print_table function from A1Test1.c.
        """
        result = ""    # create empty string
        result += "time = %6.2f\n" % self.time # append time
        for i,obj in enumerate(self): # loop over all objects and number them
            result += "  [%02d] = %s\n" % (i,obj)  # append object description
        return result  # return the string

    def segment(self):
        """
        Calls the segment method from phylib.i (which calls the phylib_segment
        functions in phylib.c.
        Sets the __class__ of the returned phylib_table object to Table
        to make it a Table object.
        """

        result = phylib.phylib_table.segment(self)
        if result:
            result.__class__ = Table
            result.current = -1
        return result

    def svg(self) -> str:
        svg_strings = ''
        for i in self:
            if i:
                svg_strings += i.svg() # call SVG method for each object in table
        return HEADER + svg_strings + FOOTER

    def roll(self, t):
        """
        Function for rolling balls in the table
        """
        new = Table()
        for ball in self:
            if isinstance(ball, RollingBall):
                # create a new ball with the same number as the old ball
                new_ball = RollingBall(ball.obj.rolling_ball.number,
                Coordinate(0,0),
                Coordinate(0,0),
                Coordinate(0,0))
                # compute where it rolls to
                phylib.phylib_roll(new_ball, ball, t)
                new += new_ball
            if isinstance(ball, StillBall):
                # create a new ball with the same number and pos as the old ball
                new_ball = StillBall(ball.obj.still_ball.number,
                Coordinate(ball.obj.still_ball.pos.x,
                ball.obj.still_ball.pos.y))
                # add ball to table
                new += new_ball
                # return table
        return new

    def get_cue_ball(self) -> Union[RollingBall, StillBall, None]:
        for object in self:
            # safe to access like this even for rolling balls due to union in C
            if isinstance(object, (StillBall, RollingBall)) and object.obj.still_ball.number == 0:
                return object
        return None

    def balls_in_table(self) -> tuple[int]:
        ball_list = []
        for item in self:
            if isinstance(item, (RollingBall, StillBall)):
                ball_list.append(item.obj.still_ball.number)
        return tuple(ball_list)

################################################################################
class Database:
    """
    Database class for reading and writing tables/games etc.
    """

    DATABASE_NAME: str = "phylib.db"
    current_database_connection = None
    current_cursor = None

    def __init__(self, reset=False):
        from os.path import exists
        from os import remove
        if reset and exists(Database.DATABASE_NAME):
            remove(Database.DATABASE_NAME)
        self.open_connection()
        self.open_cursor()
        return

    def createDB(self):
        
        def create_index_if_not_exists(cursor, index_name : str, table_name : str, column_name : str):
            if cursor is None:
                return
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND name='{index_name}'")
            result = cursor.fetchone()
            if result is None:
                cursor.execute(f"CREATE INDEX {index_name} ON {table_name} ({column_name})")
            return
        
        # need to create each table if it does not exist
        self.open_cursor()
        table_names = ("Ball", "TTable", "BallTable", "Shot", "TableShot", "Game", "Player")
        for current_table in table_names:
            # make sure table exists. If not, create it
            current_data = Database.current_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name = '{current_table}';").fetchone()
            if current_data is None:
                self.create_DB_table(current_table)
        
        # will definitely want these two
        # Database.current_cursor.execute("CREATE INDEX BallTable_BALLID_idx ON BallTable (BALLID);") # speeds up writes (shoot method)
        # Database.current_cursor.execute("CREATE INDEX BallTable_TABLEID_idx ON BallTable (TABLEID);") # speeds up reads dramatically
        
        # use Indexing to speed up operations further
        # read table speedups
        create_index_if_not_exists(Database.current_cursor, "Ball_BALLID_idx", "Ball", "BALLID")
        create_index_if_not_exists(Database.current_cursor, "TTable_TABLEID_idx", "TTable", "TABLEID")
        # #write table speedups
        create_index_if_not_exists(Database.current_cursor, "BallTable_BALLID_idx", "BallTable", "BALLID")
        create_index_if_not_exists(Database.current_cursor, "BallTable_TABLEID_idx", "BallTable", "TABLEID")
        # # get number of shots speedups
        create_index_if_not_exists(Database.current_cursor, "TableShot_SHOTID_idx", "TableShot", "SHOTID")
        Database.current_database_connection.commit()
        self.close_cursor()
        return

    def create_DB_table(self, table_name_to_create):
        # creates the table that is passed in as name_to_create
        table_names = ("Ball", "TTable", "BallTable", "Shot", "TableShot", "Game", "Player")
        if not table_name_to_create in table_names:
            return
        table_dictionary = {'Ball'      : "BALLID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, BALLNO INTEGER NOT NULL, \
                                           XPOS FLOAT NOT NULL, YPOS FLOAT NOT NULL, XVEL FLOAT, YVEL FLOAT",
                            'TTable'    : "TABLEID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, TIME FLOAT NOT NULL",
                            'BallTable' : "BALLID INTEGER NOT NULL, TABLEID INTEGER NOT NULL, FOREIGN KEY (BALLID) REFERENCES Ball(BALLID), \
                                           FOREIGN KEY (TABLEID) REFERENCES TTable(TABLEID)",
                            'Shot'      : "SHOTID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, PLAYERID INTEGER NOT NULL, \
                                           GAMEID INTEGER NOT NULL, FOREIGN KEY (GAMEID) REFERENCES Game(GAMEID), \
                                            FOREIGN KEY (PLAYERID) REFERENCES Player(PLAYERID) ",
                            'TableShot' : "TABLEID INTEGER NOT NULL, SHOTID INTEGER NOT NULL, FOREIGN KEY (TABLEID) REFERENCES TTable(TABLEID), \
                                           FOREIGN KEY (SHOTID) REFERENCES Shot(SHOTID)",
                            'Game'      : "GAMEID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, GAMENAME VARCHAR(64) NOT NULL",
                            'Player'    : "PLAYERID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, GAMEID INTEGER NOT NULL, PLAYERNAME VARCHAR(64) NOT NULL, \
                                           FOREIGN KEY (GAMEID) REFERENCES Game(GAMEID)"}
        Database.current_cursor.execute(f"CREATE TABLE \"{table_name_to_create}\" (\
                                     {table_dictionary.get(table_name_to_create)}\
                                     );")
        return

    def readTable(self, tableID):
        if not isinstance(tableID, int):
            return None
        # self.open_cursor()
        balls_in_table = Database.current_cursor.execute(f"""SELECT b.BALLNO, b.XPOS, b.YPOS, b.XVEL, b.YVEL, t.TIME
                FROM Ball AS b JOIN BallTable AS bt
                ON b.BALLID = bt.BALLID JOIN TTable AS t
                ON bt.TABLEID = t.TABLEID
                WHERE bt.TABLEID = {tableID + 1}""").fetchall() # inner join is default join
        
        if not balls_in_table:
            return None
        table_to_return = Table() # create a table object
        table_to_return.time = balls_in_table[len(balls_in_table) - 1][5]

        for current_ball in balls_in_table:
            if current_ball[3] is None and current_ball[4] is None:
                new_ball = StillBall(current_ball[0], Coordinate(current_ball[1], current_ball[2]))
            else:
                # new_ball = StillBall(current_ball[0], Coordinate(current_ball[1], current_ball[2]))
                new_ball = RollingBall(current_ball[0], Coordinate(current_ball[1], current_ball[2]), Coordinate(current_ball[3], current_ball[4]),\
                get_acceleration_coordinates(current_ball[3], current_ball[4]))
            table_to_return += new_ball
        # Database.current_database_connection.commit() # commits are too slow and also this function does not change the actual db
        # self.close_cursor()
        return table_to_return

    def writeTable(self, table) -> int:
        if not isinstance(table, Table):
            return
        # self.open_cursor()
        # Get the next available TABLEID
        table_ID = Database.current_cursor.execute("SELECT COALESCE(MAX(TABLEID), 0) FROM TTable;").fetchone()[0] + 1
        Database.current_cursor.execute("INSERT INTO TTable (TABLEID, TIME) VALUES (?, ?);", (table_ID, table.time))
        ball_values : list = []  # Initialize an empty list for batch insertion
        
        # Batch insert into Ball and BallTable
        for item in table:
            if isinstance(item, (RollingBall, StillBall)):
                ball = item.obj.rolling_ball if isinstance(item, RollingBall) else item.obj.still_ball
                ball_values.append((ball.number, ball.pos.x, ball.pos.y,\
                               ball.vel.x if isinstance(item, RollingBall) else None,\
                                ball.vel.y if isinstance(item, RollingBall) else None))

        Database.current_cursor.executemany("INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL) VALUES (?, ?, ?, ?, ?) ", ball_values)
        max_ball_id = Database.current_cursor.execute("SELECT COALESCE(MAX(BALLID), 0) FROM BallTable").fetchone()[0] + 1
        ball_table_values = [(max_ball_id + i, table_ID) for i in range(len(ball_values))] # list comprehension
        Database.current_cursor.executemany("INSERT INTO BallTable (BALLID, TABLEID) VALUES (?, ?)", ball_table_values)

        # Commit changes and close cursor
        # Database.current_database_connection.commit()
        # self.close_cursor()
        return table_ID - 1 # adjust for offset of 1

    def add_shot(self, player_name, game_ID) -> Union[int, None]:
        # self.open_cursor()
        player_ID = Database.current_cursor.execute("SELECT PLAYERID FROM Player WHERE Player.PLAYERNAME = ? AND Player.GAMEID = ?", (player_name, game_ID)).fetchone()
        player_ID = player_ID[0] if player_ID else None
        if player_ID is not None:
            Database.current_cursor.execute("INSERT INTO Shot (PLAYERID, GAMEID) SELECT ?, ?;", (player_ID, game_ID))
            shot_ID = Database.current_cursor.execute("SELECT MAX(SHOTID) FROM Shot WHERE Shot.GAMEID = ? AND Shot.PLAYERID = ?", (game_ID, player_ID)).fetchone()[0]
            # Database.current_database_connection.commit()
            # self.close_cursor()
            return shot_ID
        print(f"player {player_name} has no playerID with game ID of {game_ID}")
        return None

    def print_database(self) -> None:
        print(self.database_str(), end='')
        return

    def database_to_file(self, file_name: str = "database.txt") -> None:
        with open(file_name, "w") as file:
            file.write(self.database_str())
        file.close()
        return

    def database_str(self) -> str:
        self.open_cursor()
        # helper for printing entire database to string
        table_names = ("Ball", "TTable", "BallTable", "Shot", "TableShot", "Game", "Player")
        nameColumns = {
                        "Ball": ("BALLID", "BALLNO", "XPOS", "YPOS", "XVEL", "YVEL"),
                        "TTable": ("TABLEID", "TIME"),
                        "BallTable": ("BALLID", "TABLEID"),
                        "Shot": ("SHOTID", "PLAYERID", "GAMEID"),
                        "TableShot": ("TABLEID", "SHOTID"),
                        "Game": ("GAMEID", "GAMENAME"),
                        "Player": ("PLAYERID", "GAMEID", "PLAYERNAME")
                      }
        string = ""
        for name in table_names:
            string += f"Table {name} data is:\n\n"
            string += self.single_table_str(Database.current_cursor.execute(f"SELECT * FROM '{name}';").fetchall(), nameColumns.get(name)) + '\n'
        self.close_cursor()
        return string.strip()

    def single_table_str(self, listoftuples : list, nameColumns : tuple) -> str:
        if not listoftuples:
            return ''
        string = ''
        widths_data = [max(len(str(item[col])) for item in listoftuples) for col in range(len(nameColumns))]
        name_widths = tuple(len(i) for i in nameColumns)
        widths = tuple(max(pair) for pair in zip(widths_data, name_widths))
        left_side = '| '
        right_side = left_side[::-1]
        column_strings = [("%-" + str(width) + "s") % name.center(width) for width, name in zip(widths, nameColumns)]
        column_line = " | ".join(column_strings)
        string += (left_side + column_line + right_side + '\n')

        # add separator line
        separator = "+".join(["-" * ((width + 1) if i < 1 else (width + 2)) for i, width in enumerate(widths)])
        chars_removed = len(left_side) - len(left_side.strip())
        string += (left_side.strip() +'-'*chars_removed + separator[:len(separator)-1] +'-'*chars_removed + right_side.strip() + '\n')
        fmt = " | ".join(["%%-%ds" % width for width in widths])
        for row in listoftuples:
            centered_row = [str(data).center(width) for data, width in zip(row, widths)]
            string += (left_side +  fmt % tuple(centered_row) + right_side + '\n')
            # string += (left_side + separator[:len(separator)-1] + right_side + '\n')
        return string

    def set_game(self, game_name : str, player_1_name: str, player_2_name: str) -> int:
        # used in Game class
        # self.open_cursor()
        # if (Database.current_cursor.execute("SELECT 1 FROM Game WHERE Game.GAMENAME = ?;", (game_name,)).fetchone()) is not None:
        #     # if gamename matches do not proceed
        #     self.close_cursor()
        #     return
        self.open_cursor()
        game_ID = Database.current_cursor.execute("SELECT COALESCE(MAX(GAMEID), 0) FROM Game;").fetchone()[0] + 1
        Database.current_cursor.execute("INSERT INTO Game (GAMENAME) SELECT ?;", (game_name, ))
        # GAMEID autoincrements so do not actually need to insert it directly
        Database.current_cursor.execute("INSERT INTO Player (GAMEID, PLAYERNAME) SELECT ?, ?;", (game_ID, player_1_name)) # need to do player one first
        Database.current_cursor.execute("INSERT INTO Player (GAMEID, PLAYERNAME) SELECT ?, ?;", (game_ID, player_2_name)) # add player two
        self.close_cursor()
        self.current_database_connection.commit()
        return game_ID

    def open_connection(self):
        if Database.current_database_connection is None:
            import sqlite3
            Database.current_database_connection = sqlite3.connect(Database.DATABASE_NAME)
        return

    def open_cursor(self):
        if Database.current_database_connection is not None: # must have connection
            if Database.current_cursor is None:
                Database.current_cursor = Database.current_database_connection.cursor()
        return

    def close(self):
        if Database.current_database_connection is not None:
            Database.current_database_connection.commit()
        self.close_cursor()
        self.close_connection()
        return

    def close_cursor(self):
        if Database.current_cursor is not None:
            Database.current_cursor.close()
            Database.current_cursor = None
        return
    
    def close_connection(self):
        if Database.current_database_connection is not None:
            Database.current_database_connection.close()
            Database.current_database_connection = None
        return

    def __del__(self):
        # self.close()
        return

################################################################################
class Game:
    """
    Game class. Used with database to record shots, platers, games, etc.
    """

    database : Database = None
    current_cursor = None

    def __init__(self, gameID=None, gameName=None, player1Name=None, player2Name=None):
        Game.database = Database() # do not reset
        Game.database.createDB() # create db if not already created
        self.open_cursor() # make sure cursor is open

        self.game_ID = gameID
        self.game_name = gameName
        self.player1_name : str = player1Name
        self.player2_name : str = player2Name
        self.most_recent_shot_ID : int = None

        arguments = (gameID, gameName, player1Name, player2Name)
        if isinstance(gameID, int) and all(obj is None for obj in arguments[1:]):
            self.gameID = gameID + 1
            # Order by PLAYERID to make sure the first entry (player one) comes first
            data = Game.current_cursor.execute(f"SELECT p.PLAYERNAME, g.GAMENAME FROM Game AS g\
                        INNER JOIN Player AS p ON g.GAMEID = ? AND p.GAMEID = ? ORDER BY p.PLAYERID;", (self.gameID, self.gameID)).fetchall()
            if not data:
                return
            self.player_1_name, self.player_2_name, self.game_name = data[0][0], data[1][0], data[0][1]
        elif (gameID is None and all((type(i) == str and i) for i in arguments[1:-1])):
            self.game_ID = Game.database.set_game(game_name=gameName, player_1_name=player1Name, player_2_name=player2Name)
        else:
            raise TypeError # raise an exception
        return
    
    def shoot(self, gameName, playerName, table, xvel, yvel) -> tuple[Table]:
        # print(f"shoot called with: ({xvel} {yvel}) GameName: {gameName} playerName: {playerName}")
        """
        returns a list of the segments that are generated by rolling the cue ball with the given x and y velocities (used to calculate game state).
        Each segment time is divided into the FRAME_INTERVAL at the top of the module and written into the database.
        """
        if not (all(isinstance(obj, (float, int)) for obj in (xvel, yvel)) and isinstance(table, Table) and table):
            return
        self.open_cursor()
        # Game.current_cursor.execute("SELECT G.GAMEID FROM (Game AS G INNER JOIN Player AS P ON G.GAMEID = P.GAMEID)\
        #                                       WHERE G.GAMENAME = ? AND P.PLAYERNAME = ? AND G.GAMEID = ?", (gameName, playerName, self.game_ID)).fetchone()
        shot_ID = Game.database.add_shot(playerName, self.game_ID)
        cue_ball: Union[RollingBall, StillBall, None] = table.get_cue_ball()
        if not (cue_ball and shot_ID):
            print("CUE BALL OR SHOT ID ARE FALSY")
            return
        cue_ball = self.set_cue_ball(cue_ball, xvel, yvel)
        list_of_segments : list[Table] = []
        table_ID_list : list[int] = []
        # self.open_cursor()
        count = 0
        start = perf_counter()
        while table:
            count += 1
            if (current_segment := table.segment()) is None:
                break
            num_iterations = floor((current_segment.time - table.time) / FRAME_INTERVAL)
            # print(f"segment {count} has {num_iterations} svgs")
            for i in range(num_iterations):
                roll_time : int = i * FRAME_INTERVAL
                table_inner : Table = table.roll(roll_time)
                table_inner.time = table.time + roll_time
                table_ID_list.append(Game.database.writeTable(table_inner)  + 1) # add one since we will be inserting this ID into the db
            # write the segment itself to the database, and append it to the tuple for return
            table_ID_list.append(Game.database.writeTable(current_segment)  + 1)
            list_of_segments.append(current_segment)
            table = current_segment
            if count == 5000:
                print(f"TOO MANY SEGMENTS -- ENTERING INFINITE LOOP -- (COUNTED {count} SEGMENTS). ABORTING SHOOT")
                print("SHOT PARAMS: ", xvel, yvel)
                # print("CURRENT SEGMENT:", str(current_segment), sep='\n')
                return
        table_shot_values = [(table_ID, shot_ID) for table_ID in table_ID_list]
        self.most_recent_shot_ID = shot_ID
        print(f'Time to shoot: {perf_counter() - start}')
        print(f'NUMBER OF SEGMENTS: {count}')
        Game.current_cursor.executemany("INSERT INTO TableShot (TABLEID, SHOTID) VALUES (?, ?);", (table_shot_values))
        # self.database.current_database_connection.commit()
        self.close_cursor()
        return tuple(list_of_segments)

    def set_cue_ball(self, cue_ball : Union[StillBall, RollingBall], xvel: float, yvel: float) -> Union[StillBall, RollingBall, None]:
        # should be okay to access as stillball even if rolling
        # cue_ball_pos = Coordinate(cue_ball.obj.still_ball.pos.x, cue_ball.obj.still_ball.pos.y)
        cue_ball.type = phylib.PHYLIB_ROLLING_BALL
        cue_ball.obj.rolling_ball.number = 0 # not necessary but why not
        # cue_ball.obj.rolling_ball.pos = cue_ball_pos
        cue_ball.obj.rolling_ball.vel = Coordinate(xvel, yvel)
        cue_ball.obj.rolling_ball.acc = get_acceleration_coordinates(xvel, yvel)
        return cue_ball

    def __del__(self):
        # Game.database.close()
        return

    def open_cursor(self):
        # wrapper method
        Game.database.open_cursor()
        Game.current_cursor = Game.database.current_cursor
        return
    
    def close_cursor(self):
        # wrapper method
        Game.database.close_cursor()
        Game.current_cursor = Game.database.current_cursor
        return

    def close_connection(self):
        # wrapper method
        Game.database.close_connection()
        return
    
    def close(self):
        # wrapper method
        Game.database.close()
        return
    
    def get_number_of_tables_for_shot(self, shot_ID : int) -> int:
        self.open_cursor()
        num_shots = Game.current_cursor.execute("SELECT COUNT(t.TABLEID) FROM (TableShot as t INNER JOIN SHOT\
                                                as s ON (t.SHOTID = s.SHOTID)) WHERE s.GAMEID = ? and s.SHOTID = ?;", (self.game_ID, shot_ID)).fetchone()[0]
        self.close_cursor()
        return num_shots
    
    def get_total_number_of_tables_in_database(self):
        self.open_cursor()
        x = Game.current_cursor.execute("SELECT COUNT(t.TABLEID) FROM TTable as t;").fetchone()[0]
        self.close_cursor()
        return x

    def get_most_recent_shotID(self) -> int:
        self.open_cursor()
        x = Game.current_cursor.execute("SELECT COALESCE(MAX(s.SHOTID), 0) FROM Shot as s\
            INNER JOIN TableShot as ts on (ts.SHOTID = s.SHOTID) WHERE s.GAMEID = ?;", (self.game_ID,)).fetchone()[0]
        self.close_cursor()
        return x

    def get_first_tableID_for_shot(self, shot_ID : int) -> int:
        self.open_cursor()
        id = Game.current_cursor.execute("SELECT MIN(t.TABLEID) FROM (TableShot as t INNER JOIN SHOT\
                                                as s ON (t.SHOTID = s.SHOTID)) WHERE s.GAMEID = ? and s.SHOTID = ?;", (self.game_ID, shot_ID)).fetchone()[0]
        self.close_cursor()
        return id
    
    def get_last_tableID_for_shot(self, shot_ID : int) -> int:
        self.open_cursor()
        id = Game.current_cursor.execute("SELECT COALESCE(MAX(t.TABLEID), 0) FROM (TableShot as t INNER JOIN SHOT\
                                                as s ON (t.SHOTID = s.SHOTID)) WHERE s.GAMEID = ? and s.SHOTID = ?;", (self.game_ID, shot_ID)).fetchone()[0]
        self.close_cursor()
        return id

################################################################################    
def get_acceleration_coordinates(rolling_ball_dx: float, rolling_ball_dy: float) -> Coordinate:
    rolling_ball_a_x, rolling_ball_a_y = 0.0, 0.0
    rolling_ball_speed = hypot(rolling_ball_dx, rolling_ball_dy)
    if (rolling_ball_speed > VEL_EPSILON):
        rolling_ball_a_x = -rolling_ball_dx * DRAG / rolling_ball_speed
        rolling_ball_a_y = -rolling_ball_dy * DRAG / rolling_ball_speed
    return Coordinate(rolling_ball_a_x, rolling_ball_a_y)
