# A2 CIS*2750
# Martin Sergo W24 
import os, Physics, json # sys used to get argv, os for file operations, Physics for phylib library access, json for post request data
NUM_PADDED_ZEROES = 5
# web server imports
from http.server import HTTPServer, BaseHTTPRequestHandler
# from icecream import ic # for debugging
# used to parse the URL and extract form data for GET requests
from urllib.parse import urlparse, parse_qsl

def make_default_table() -> Physics.Table:
# Setup the table
    table_to_return = Physics.Table()  # Create a new table

    # Define the number of rows and balls per row
    import math
    balls_per_row = (1, 2, 3, 4, 5)
    ball_ordering = [1, 2, 9, 3, 8, 10, 4, 14, 7, 11, 12, 6, 15, 13, 5]

    root_3 = math.sqrt(3.0)
    for row in range(5):
        for ball in range(row + 1):
            x = Physics.TABLE_WIDTH / 2.0 + (ball - (row + 1) / 2.0) * (Physics.BALL_DIAMETER + randomMillimeterOffset())
            y = Physics.TABLE_WIDTH / 2.0 - root_3 / 2.0 * (Physics.BALL_DIAMETER + randomMillimeterOffset()) * row
            current_ball_number = ball_ordering.pop(0)
            pos = Physics.Coordinate(x, y)
            sb = Physics.StillBall(current_ball_number, pos)
            table_to_return += sb

    # Add cue ball
    pos = Physics.Coordinate(Physics.TABLE_WIDTH / 2.0, Physics.TABLE_LENGTH - Physics.TABLE_WIDTH / 2.0)
    sb = Physics.StillBall(0, pos)
    table_to_return += sb
    return table_to_return

def randomMillimeterOffset() -> float:
    return 0.0
    import random
    return random.random() + 1

class ServerGame(Physics.Game):
    import random
    most_recent_table = make_default_table()

    def __init__(self, gameName: str=None, player_one: str = None, player_two: str = None):
        super().__init__(gameName=gameName, player1Name=player_one, player2Name=player_two) # call Game class constructor
        # print(self.game_ID, self.game_Name, self.player1_name, self.player2_name) # inherited from superclass
        self.most_recent_table : Physics.Table = ServerGame.most_recent_table # initially the game will have the default table
        self.current_player = self.player1_name if ServerGame.random.random() > 0.5 else self.player2_name
        self.num_shots_made = 0
        return
    
    def set_random_player(self):
        return
    
    def switch_current_player(self):
        self.current_player = self.player2_name if self.current_player == self.player1_name else self.player1_name
        print(f"switched to player: {self.current_player}")
        return

    def perform_shot(self, x_vel, y_vel) -> int:
        # returns the NUMBER OF TABLES generated from the shot
        self.num_shots_made += 1
        super().shoot(gameName=self.game_Name, playerName=self.current_player, table=self.most_recent_table, xvel=x_vel, yvel=y_vel) # perform the shot
        self.switch_current_player()
        self.database.database_to_file()
        num_tables = super().get_number_of_tables_for_shot(self.num_shots_made)
        print(f"\n{num_tables} in all\n")
        self.most_recent_table = self.database.readTable(num_tables-1)
        return num_tables

#################################################################################
class MyHandler(BaseHTTPRequestHandler):
    current_game : ServerGame = None
    def do_GET(self):
        # parse the URL to get the path and form data
        path = urlparse(self.path).path[1:]

        if not path and os.path.exists("index.html"):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            
            with open("index.html", "rb") as file:
                content = file.read()
            self.send_header("Content-length", len(content))
            self.end_headers()
            self.wfile.write(content)
            MyHandler.current_game = None

        elif path.startswith("table-") and path.endswith(".svg"):    
            filename = path
            # print("name of file: "+filename)
            if os.path.exists(filename):
                self.send_response(200)
                self.send_header("Content-type", "image/svg+xml")
                with open(filename, "rb") as file:
                    content = file.read()
                self.send_header("Content-length", len(content))
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                content = "404: requested file %s not found" % (self.path if self.path != '' else "index.html")
                self.send_header("Content-length", len(content))
                self.end_headers()
                print(self.path)
                self.wfile.write(bytes(content, "utf-8"))
        
        elif path.endswith(".css") and os.path.exists(path):
            self.send_response(200)
            self.send_header("Content-type", "text/css")
            with open(path, 'rb') as file:
                content = file.read()
            self.send_header("Content-length", len(content))
            self.end_headers()
            self.wfile.write(content)

        elif path.endswith(".js") and os.path.exists(path):
            self.send_response(200)
            self.send_header("Content-type", "text/javascript")
            with open(path, 'rb') as file:
                content = file.read()
            self.send_header("Content-length", len(content))
            self.end_headers()
            self.wfile.write(content)
        
        else:
            self.send_response(404)
            self.send_header("Content-type", "text/html")
            content = "404: requested file %s not found" % (self.path[1:] if self.path != '' else "index.html")
            self.send_header("Content-length", len(content))
            self.end_headers()
            print(self.path)
            self.wfile.write(bytes(content, "utf-8"))

    def do_POST(self):
        path  = urlparse(self.path).path[1:]
        # receive form data from shoot.html
        if path == "display.html":
            import math, random
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = dict(parse_qsl(post_data))

            if len(form_data) != 3:
                self.send_response(404)
                response_content = '<H3>Form fields are not fully filled. Try again.</H3>\
                <a href ="#" onclick=window.history.back(); return false, title = "return">back to previous page</a>'
                self.send_header("Content-type", "text/html")
                self.send_header("Content-length", len(response_content))
                self.end_headers()
                self.wfile.write(bytes(response_content, "utf-8"))
                return
            # delete any SVGs currently existing
            delete_SVGs_in_pwd()
            current_table = ServerGame.most_recent_table
            write_svg(0, current_table)
            game_name = form_data.get("game_name", 'NAME NOT FOUND').strip()
            player_one = form_data.get("player_one", 'NAME NOT FOUND').strip()
            player_two = form_data.get("player_two", 'NAME NOT FOUND').strip()
            # create game if it does not exist
            if MyHandler.current_game is None:
                MyHandler.current_game = ServerGame(gameName=game_name, player_one=player_one, player_two=player_two) # initializze the game
            response_content = f"""<!DOCTYPE html>
                            <html lang="en">
                            <head>
                                <meta charset="UTF-8">
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                <title>Make a shot!</title>
                                <link rel="stylesheet" href="style.css">
                            </head>
                            <body>
                                <div class="row">
                                <div class="column">
                                <div class="outerInfoBox">
                                    {box("Game Name: " + game_name)}<!--INSERT GAME NAME HERE-->
                                    {box("Player One: " + player_one)}<!--INSERT PLAYER ONE HERE-->
                                    {box("Player Two: " + player_two)}<!--INSERT PLAYER TWO HERE-->
                                    {box("Current Player: " + MyHandler.current_game.current_player)}<!--INSERT CURRENT PLAYER HERE-->
                                    {box("Table time: " + str(current_table.time))}<!--INSERT CURRENT TIME-->
                                </div> <!--for outer info box-->
                                </div> <!---for column 1-->
                                <div class="column">
                                <div class="svgTableDisplay">
                                    {current_table.svg()}<!--INSERT TABLE HERE-->
                                    <svg id="svgLayer"></svg>
                                </div> <!--for svg-->
                                </div> <!--for column 2-->
                                </div> <!--for row-->
                                <script src="game.js"></script> <!--script should be at the end-->
                            </body>
                            </html>"""
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-length", len(response_content))
            self.end_headers()
            self.wfile.write(bytes(response_content, "utf-8"))
        
        elif path == "new_shot":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = json.loads(post_data) # parse the json object sent from the javascript file
            # print("recieved shot request!")
            # print(f"form data: {form_data}")
            xvel: float = form_data.get("velocity").get("x_vel")
            yvel: float = form_data.get("velocity").get("y_vel")
            
            number_of_svgs_to_flash = MyHandler.current_game.perform_shot(xvel, yvel)
            print("did shot math:", str(number_of_svgs_to_flash))
            with open("display.html", "r") as file:
                lines = file.readlines()
            for i in range(number_of_svgs_to_flash):
                current_table = MyHandler.current_game.database.readTable(i)
                table_svg = current_table.svg()
                write_svg(i+1, current_table)
            player_one_text = f'<div class = "infoBox">Player one: {MyHandler.current_game.player1_name}</div>'
            player_two_text = f"<h2>Player two: {MyHandler.current_game.player2_name}</h2>"
            game_name_text = f"<h2>Game name: {MyHandler.current_game.game_Name}</h2>"
            current_player_text = f"<h2>Current Player: {MyHandler.current_game.current_player}<h2><br>"

            # Iterate over the lines and modify as needed
            modified_lines = []
            for line in lines:
                if "<!--INSERT TABLE HERE-->" in line:
                    modified_lines.append(table_svg)
                elif "<!--INSERT PLAYER ONE HERE-->" in line:
                    modified_lines.append(player_one_text)
                elif "<!--INSERT PLAYER TWO HERE-->" in line:
                    modified_lines.append(player_two_text)
                elif "<!--INSERT GAME NAME HERE-->" in line:
                    modified_lines.append(game_name_text)
                elif "<!--INSERT CURRENT PLAYER HERE-->" in line:
                    modified_lines.append(current_player_text)
                else:
                    modified_lines.append(line)  # Keep the original line

            # Write the modified lines back to the file
            with open("display.html", "w") as file:
                file.writelines(modified_lines)
            # Write the updated content back to the file
            # reset_display_html() # reset the file again
            response_content = ''
            for line in modified_lines:
                response_content += line
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-length", len(response_content))
            self.end_headers()
            self.wfile.write(bytes(response_content, "utf-8"))
            return
        
        else:
            self.send_response(404)
            response_content = f"404: requested file \"{self.path}\" not found"
            self.send_header("content-length", len(response_content))
            self.send_header("content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(response_content, "utf-8"))
        return

def write_svg(table_id, table):
    if not table:
        return
    directory = "tables/"
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(os.path.join(directory, f"table{table_id:0{NUM_PADDED_ZEROES}d}.svg"), "w") as fp:
        fp.write(table.svg())

# no need to make this a class method
def delete_SVGs_in_pwd() -> None:
    from re import match
    # Define the file name pattern to match
    svg_pattern = r"^table-\d+\.svg$"
    # Get a list of all files in the current directory
    files_in_directory = os.listdir()
    # print(str(svg_pattern))
    # Iterate over the files and delete those matching the svg pattern
    for file_name in files_in_directory:
        if match(svg_pattern, file_name):
            os.remove(file_name)
            # print("removed file:" + file_name)
    return

def reset_display_html() -> None:
    content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Make a shot!</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="row">
    <div class="column">
    <div class="outerInfoBox">
        <!--INSERT GAME NAME HERE-->
        <!--INSERT PLAYER ONE HERE-->
        <!--INSERT PLAYER TWO HERE-->
        <!--INSERT CURRENT PLAYER HERE-->
        <!--INSERT CURRENT TIME-->
    </div> <!--for outer info box-->
    </div> <!---for column 1-->
    <div class="column">
    <div class="svgTableDisplay">
        <!--INSERT TABLE HERE-->
        <svg id="svgLayer"></svg>
    </div> <!--for svg-->
    </div> <!--for column 2-->
    </div> <!--for row-->
    <script src="game.js"></script> <!--script should be at the end-->
</body>
</html>"""
    with open("display.html", 'w') as file:
        file.write(content)
    return

def box(string: str = None) -> str:
    return f'<div class="infoBox">{string}</div>'

def main() -> None:
    # if len(sys.argv) < 2:
    #     print("Need a command line argument!")
    #     # need to use exit instead of return
    #     sys.exit(1)  # Exit the script
    temp = Physics.Database(reset=True) # reset the database in case it has data
    del temp

    # port_num = int(sys.argv[1]) + int(5e4)
    port_num = 3000
    # d is for daemon
    httpd = HTTPServer(('localhost', port_num), MyHandler)
    # delete any SVG files currently existing
    delete_SVGs_in_pwd()
    print("Server listing in port: ", port_num)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nCanceled with Ctrl + C')
        httpd.shutdown()

if __name__ == "__main__":
    main()

