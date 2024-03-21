# A4 CIS*2750
# Martin Sergo W24 
import os, Physics, sys, json # sys used to get argv, os for file operations, Physics for phylib library access, json for post request data
from typing import Union
from subprocess import run, CalledProcessError, DEVNULL
NUM_PADDED_ZEROES = 5
extension = "webm"
output_name = "svg_movie"
# web server imports
from http.server import HTTPServer, BaseHTTPRequestHandler
# from icecream import ic # for debugging
# used to parse the URL and extract form data for GET requests
from urllib.parse import urlparse, parse_qsl, parse_qs

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
    return 4.0
    import random
    return random.random() + 1

def remove_svgs(dir_name: str = "tables"):
    path = f"{os.getcwd()}{f'/{dir_name}/'}"
    list_of_files = os.listdir(path)
    for file in list_of_files:
        if file.endswith(".svg"):
            os.remove(os.path.join(path, file))

def generate_animation(directory : str = "/tables"):
    supress_output = True
    # print(os.path.exists(os.getcwd() + "/tables/"))
    if os.path.exists(os.getcwd() + f"{directory}/") and os.listdir(os.getcwd() + f"{directory}/"):
        command_for_animation_using_ffmpeg = f'ffmpeg -y -framerate 100 -i \
                                .{directory}/table%0{NUM_PADDED_ZEROES}d.svg -vf "crop=687.5:1362.5:12.5:12.5"\
                                -c:v libvpx-vp9 -pix_fmt yuv420p -s 540x1080 -b:v 2M -crf 8 -c:a libvorbis {output_name}.{extension}'
        try:
            print("attempting to generate video...")
            if supress_output:
                run(command_for_animation_using_ffmpeg, shell=True, check=True, stdout=DEVNULL, stderr=DEVNULL)
            else:
                run(command_for_animation_using_ffmpeg, shell=True, check=True)
            print("Animation generated successfully.")
        except CalledProcessError as e:
            print("Error occurred while generating animation:", e)
    return

def write_svg(table_id, table, directory: str = "tables/"):
    if not table:
        return
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(os.path.join(directory, f"table{table_id:0{NUM_PADDED_ZEROES}d}.svg"), "w") as fp:
        fp.write(table.svg())


class ServerGame(Physics.Game):
    import random

    def __init__(self, gameName: str=None, player_one: str = None, player_two: str = None):
        super().__init__(gameName=gameName, player1Name=player_one, player2Name=player_two) # call Game class constructor
        # print(self.game_ID, self.game_Name, self.player1_name, self.player2_name) # inherited from superclass
        self.most_recent_table : Physics.Table = make_default_table() # initially the game will have the default table
        self.current_player : str = self.player1_name if ServerGame.random.random() > 0.5 else self.player2_name
        self.num_shots_made : int = 0
        self.set_High_low : bool = False
        return
    
    def switch_current_player(self):
        self.current_player = self.player2_name if self.current_player == self.player1_name else self.player1_name
        print(f"switched to player: {self.current_player}")
        return

    def perform_shot(self, x_vel, y_vel) -> int:
        # returns the NUMBER OF TABLES generated from the shot
        self.num_shots_made += 1
        end_tables: tuple[Physics.Table] = super().shoot(gameName=self.game_Name, playerName=self.current_player, table=self.most_recent_table, xvel=x_vel, yvel=y_vel)
        # perform the shot
        print(f"end_tables length: {len(end_tables)}")
        # print("END TABLES:", *(str(i) for i in end_tables))
        # for i, table in enumerate(end_tables):
        #     # table = super().readTable()
        #     write_svg(i,table)
        self.database.database_to_file()
        num_tables = super().get_number_of_tables_for_shot(self.num_shots_made) # this will go from 1 - num_tables
        # print(f"\n{num_tables} in all\n")
        remove_svgs(dir_name='special2')
        for i in range(num_tables):
            write_svg(i, self.database.readTable(i), directory="special2/")
        generate_animation(directory="/special2")
        self.most_recent_table = self.database.readTable(num_tables - 1)
        write_svg(0, self.most_recent_table, directory="special/")
        self.switch_current_player()
        return num_tables

    def read_time(self, time : float) -> Union[Physics.Table, None]:
        x = self.database.current_cursor.execute("SELECT 1 FROM TTable WHERE TTable.TIME = ?;", (time,)).fetchone()
        if x:
            x = x[0] - 1
        else:
            print("FATAL MATCH ERROR")
            sys.exit(1)
        return self.database.readTable(x)
    
    def open_cursor(self):
        return super().open_cursor()

#################################################################################
class MyHandler(BaseHTTPRequestHandler):
    current_game : ServerGame = None
    
    def log_message(self, format, *args):
        return
    
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
        
        elif path in "single_svg":
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            if "time" in query_params:
                time = float(query_params["time"][0])  # Assuming only one time parameter
                print("Time parameter:", time)
                # Your code to handle the time parameter goes here
                MyHandler.current_game.open_cursor()

                if (response_content := MyHandler.current_game.read_time(time)):
                    write_svg(int(100 * time), response_content)
                    response_content : str = response_content.svg()
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "text")
                    self.send_header("Content-length", len(response_content))
                    self.end_headers()
                    self.wfile.write(bytes(response_content, "utf-8"))
                self.send_response(200)
                self.send_header("Content-type", "image/svg+xml")
                self.send_header("Content-length", len(response_content))
                self.end_headers()
                self.wfile.write(bytes(response_content, "utf-8"))
            else:
                self.send_response(404)
                self.send_header("Content-type", "text")
                self.send_header("Content-length", len(response_content))
                self.end_headers()
                self.wfile.write(bytes(response_content, "utf-8"))
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
            game_name = form_data.get("game_name", 'NAME NOT FOUND').strip()
            player_one = form_data.get("player_one", 'NAME NOT FOUND').strip()
            player_two = form_data.get("player_two", 'NAME NOT FOUND').strip()
            # create game if it does not exist
            if MyHandler.current_game is None:
                MyHandler.current_game = ServerGame(gameName=game_name, player_one=player_one, player_two=player_two) # initializze the game
                current_table = MyHandler.current_game.most_recent_table
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
            print("recieved shot request!")
            print(f"form JSON data: {form_data}")
            xvel: float = form_data.get("velocity").get("x_vel")
            yvel: float = form_data.get("velocity").get("y_vel")
            if not MyHandler.current_game:
                print("NO GAME")
                return
            number_of_svgs_to_flash = MyHandler.current_game.perform_shot(xvel, yvel)
            print("did shot math:", str(number_of_svgs_to_flash))
            response_content = f"{{\"total_time\": {round(MyHandler.current_game.most_recent_table.time, 2)}}}"
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Content-length", len(response_content))
            self.end_headers()
            self.wfile.write(bytes(response_content, "utf-8"))
        
        else:
            self.send_response(404)
            response_content = f"404: requested file \"{self.path}\" not found"
            self.send_header("content-length", len(response_content))
            self.send_header("content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(response_content, "utf-8"))
        
        return

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

def remove_video(video_file_name: str = "svg_movie", extension: str = "webm" ):
    if os.path.exists(f'{video_file_name}.{extension}'):
        os.remove(f"{video_file_name}.{extension}")
    return

def main() -> None:
    # if len(sys.argv) < 2:
    #     print("Need a command line argument!")
    #     # need to use exit instead of return
    #     sys.exit(1)  # Exit the script
    from subprocess import DEVNULL
    temp = Physics.Database(reset=True) # reset the database in case it has data
    del temp
    remove_video()
    # port_num = int(sys.argv[1]) + int(5e4)
    port_num = 3000
    # d is for daemon
    httpd = HTTPServer(('localhost', port_num), MyHandler)
    # delete any SVG files currently existing
    print("Server listing in port: ", port_num)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nCanceled with Ctrl + C')
        httpd.shutdown()

if __name__ == "__main__":
    main()
