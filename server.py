# A4 CIS*2750
# Martin Sergo W24 
import os, Physics, sys, json # sys used to get argv, os for file operations, Physics for phylib library access, json for post request data
from typing import Union
from subprocess import run, CalledProcessError, DEVNULL
from time import perf_counter

NUM_PADDED_ZEROES = 5
extension = "webm"
output_name = "svg_movie"
# web server imports
from http.server import HTTPServer, BaseHTTPRequestHandler
# from icecream import ic # for debugging
# used to parse the URL and extract form data for GET requests
from urllib.parse import urlparse, parse_qsl, parse_qs

def remove_video(video_file_name: str = "svg_movie", extension: str = "webm" ):
    if os.path.exists(f'{video_file_name}.{extension}'):
        os.remove(f"{video_file_name}.{extension}")
    return

def make_default_table() -> Physics.Table:
    
    def randomMillimeterOffset() -> float:
        return 4.0
        import random
        return random.random() + 1
    
    
    # Setup the table
    table_to_return = Physics.Table()  # Create a new table

    # Define the number of rows and balls per row
    import math
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
    
    HIGH_BALLS = tuple(i for i in range(9, 16))
    # exclude the 8 ball
    LOW_BALLS = tuple(i for i in range(1, 8))
    
    def __init__(self, gameName: str=None, player_one: str = None, player_two: str = None):
        from random import random
        super().__init__(gameName=gameName, player1Name=player_one, player2Name=player_two) # call Game class constructor
        # print(self.game_ID, self.game_Name, self.player1_name, self.player2_name) # inherited from superclass
        self.most_recent_table : Physics.Table = make_default_table() # initially the game will have the default table
        self.current_player : str = self.player1_name if random() > 0.5 else self.player2_name
        self.num_shots_made : int = 0
        self.set_High_low : bool = False
        self.previous_shot_max_index : int = 0
        self.player_1_score : int = 0
        self.player_2_score : int = 0
        self.cue_ball_sunk : bool = False
        self.cue_ball_sunk : bool = False
        self.eight_ball_sunk : bool = False
        self.eight_ball_sunk_invalid : bool = False
        self.eight_ball_sunk_valid : bool = False
        self.winner : str = None
        print(f"NEW ID: {self.game_ID}")
        self.open_cursor()
        return
    
    def switch_current_player(self) -> None:
        x = self.current_player
        self.current_player = self.player2_name if x == self.player1_name else self.player1_name
        print(f"switched to player: {self.current_player} from {x}")
        return

    def perform_shot(self, x_vel, y_vel) -> tuple[tuple[str]]:
        self.num_shots_made += 1
        self.cue_ball_sunk = False
        self.eight_ball_sunk = False
        self.extra_turn = False
        # perform the shot. Split the current player for when (LOW) or (HIGH) are appended (will not be in db)
        segments : tuple[Physics.Table] = super().shoot(gameName=self.game_Name, playerName=self.current_player.split(maxsplit=1)[0], table=self.most_recent_table, xvel=x_vel, yvel=y_vel)
        self.analyze_segments(segments)
        if self.cue_ball_sunk:
            print("CUE BALL HAS BEEN SUNK")
        print(f"number of segments: {len(segments)}")
        # self.database.database_to_file()
        num_tables = super().get_number_of_tables_for_shot() # this will go from 1 - num_tables
        previous_max_index = self.previous_shot_max_index
        svg_list = []
        print(f"using i range: ({previous_max_index} - {num_tables + previous_max_index})")
        for i in range(previous_max_index, previous_max_index + num_tables):
            table = self.database.readTable(i)
            svg_list.append((table.svg(), table.time))
        self.previous_shot_max_index += num_tables
        print(f"max shot changed from {self.previous_shot_max_index - num_tables} to {self.previous_shot_max_index}")
        # only update the most recent table to be the end of the shot when cue ball is still on the table
        
        self.most_recent_table = self.database.readTable(previous_max_index + num_tables - 1)
        if self.cue_ball_sunk:
            #insert the cue ball at starting position. If there happens to be a ball there, things will break.
            self.most_recent_table += Physics.StillBall(0, Physics.Coordinate(Physics.TABLE_WIDTH / 2.0, Physics.TABLE_LENGTH - Physics.TABLE_WIDTH / 2.0))
        if not self.extra_turn:
            self.switch_current_player()
        return tuple(svg_list)
    
    def analyze_segments(self, segments : tuple[Physics.Table]) -> None:
        previous_table = self.most_recent_table
        previous_balls = previous_table.balls_in_table()
        for segment in segments:
            segment_balls = segment.balls_in_table()
            # print(segment_balls)
            if len(segment_balls) != len(previous_balls):
                for previous_ball in previous_balls:
                    if not (previous_ball in segment_balls):
                        # print(f"ball {default_ball} not found in segment balls")
                        if previous_ball == 8:
                            print("SUNK 8 BALL")
                            self.eight_ball_sunk = True
                            if len(previous_balls) == 2:
                                # case for only cue ball and 8 ball
                                self.eight_ball_sunk_valid = True
                            else:
                                # should immediately end the game and make current player the loser
                                self.eight_ball_sunk_invalid = True
                            return
                        if previous_ball == 0:
                            self.cue_ball_sunk = True
                        # if the HIGH/LOW waas not yet set
                        if self.set_High_low is False:
                            if previous_ball in ServerGame.LOW_BALLS:
                                print("SETTING CURRENT PLAYER LOW")
                                self.set_high_low_values(" (LOW)")
                            else:
                                print("SETTING CURRENT PLAYER HIGH")
                                self.set_high_low_values(" (HIGH)")
                            return
                        
                        else:
                            if (self.current_player.endswith(" (LOW)") and previous_ball in ServerGame.LOW_BALLS) or \
                                (self.current_player.endswith(" (HIGH)") and previous_ball in ServerGame.HIGH_BALLS):
                                self.increase_player_score()
                            else:
                                opposite_player : str = self.player1_name if self.current_player == self.player1_name else self.player2_name
                                self.increase_player_score(player_to_increment_score=opposite_player)
                        
    def increase_player_score(self, player_to_increment_score : str = ''):
        if not player_to_increment_score:
            # have to do it at runtime
            player_to_increment_score = self.current_player
        if player_to_increment_score == self.player1_name.split(maxsplit=1)[0]:
            self.player_1_score += 1
        elif player_to_increment_score == self.player2_name.split(maxsplit=1)[0]:
            self.player_2_score += 1
        return    
        
    def set_high_low_values(self, high_or_low : str):
        if self.current_player == self.player1_name:
            self.player1_name += high_or_low
            self.current_player = self.player1_name
            self.player2_name += " (LOW)" if high_or_low == " (HIGH)" else " (HIGH)"
        else:
            self.player2_name += high_or_low
            self.current_player = self.player2_name
            self.player1_name += " (LOW)" if high_or_low == " (HIGH)" else " (HIGH)"
        self.increase_player_score()
        self.set_High_low = True # never need to set again
        return
    
    def open_cursor(self):
        return super().open_cursor()
    
    def __del__(self):
        # self.close()
        return

#################################################################################
class MyHandler(BaseHTTPRequestHandler):
    current_game : ServerGame = None
    
    # def log_message(self, format, *args):
    #     return
    
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

        elif path.startswith("table-") and path.endswith(".svg") and os.path.exists(filename):
            filename = path
            self.send_response(200)
            self.send_header("Content-type", "image/svg+xml")
            with open(filename, "rb") as file:
                content = file.read()
            self.send_header("Content-length", len(content))
            self.end_headers()
            self.wfile.write(content)
            
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
        
        elif path == "single_svg":
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
        
        elif path == "display_game":
            print("game display")
            if MyHandler.current_game is None:
                response_content = "<h1>NO GAME FOUND</h1>"
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.send_header("Content-length", len(response_content))
                self.end_headers()
                self.wfile.write(bytes(response_content, "utf-8"))    
                return

            game_name = MyHandler.current_game.game_Name
            player_one = MyHandler.current_game.player1_name
            player_two = MyHandler.current_game.player2_name
            current_table = MyHandler.current_game.most_recent_table
            # create game if it does not exist
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
                                    {self.box("Game Name: " + game_name)} <!--INSERT GAME NAME HERE-->
                                    {self.box("Player One: " + player_one)} <!--INSERT PLAYER ONE HERE-->
                                    {self.box("Player Two: " + player_two)} <!--INSERT PLAYER TWO HERE-->
                                    {self.box("Current Player: " + MyHandler.current_game.current_player)}<!--INSERT CURRENT PLAYER HERE-->
                                    {f'<div class="infoBox" id="time">Table time: {str(round(current_table.time, 2))}</div>'} <!--INSERT CURRENT TIME-->
                                </div> <!--for outer info box-->
                                </div> <!---for column 1-->
                                <div class="column">
                                <div id="svgTableDisplay">
                                    {current_table.svg()}<!--INSERT TABLE HERE-->
                                    <svg id="svgLayer"></svg>
                                </div> <!--for svg-->
                                </div> <!--for column 2-->
                                </div> <!--for row-->
                            </body>
                            </html>"""
            self.send_response(200)
            self.send_header("Content-type", "text/html")
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
            if MyHandler.current_game is None:
                MyHandler.current_game = ServerGame(gameName=game_name, player_one=player_one, player_two=player_two) # initializze the game if it does not exist
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
                                    {self.box("Game Name: " + game_name)} <!--INSERT GAME NAME HERE-->
                                    {self.box("Player One: " + player_one)} <!--INSERT PLAYER ONE HERE-->
                                    {self.box("Player Two: " + player_two)} <!--INSERT PLAYER TWO HERE-->
                                    {self.box("Current Player: " + MyHandler.current_game.current_player)}<!--INSERT CURRENT PLAYER HERE-->
                                    {f'<div class="infoBox" id="time">Table time: {str(round(current_table.time, 2))}</div>'} <!--INSERT CURRENT TIME-->
                                </div> <!--for outer info box-->
                                </div> <!---for column 1-->
                                <div class="column">
                                <div id="svgTableDisplay">
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
            print("RESET")
    
        elif path == "new_shot":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = json.loads(post_data) # parse the json object sent from the javascript file
            print(f"form JSON data: {form_data}")
            xvel: float = form_data.get("velocity").get("x_vel")
            yvel: float = form_data.get("velocity").get("y_vel")
            if not MyHandler.current_game:
                print("NO GAME. RESTART REQUIRED")
                return
            list_of_svgs = MyHandler.current_game.perform_shot(xvel, yvel)
            # print("Number of SVGs:", str(len(list_of_svgs)))
            json_content = [{"num_svgs": f'{len(list_of_svgs)}'}]
            for i, (svg, time) in enumerate(list_of_svgs):
                table_data = {
                    f"table-{i}": svg,  # Remove leading/trailing whitespace from SVG
                    f"table-{i}_time": time
                }
                json_content.append(table_data)
            json_content.append({"cue_ball_sunk": MyHandler.current_game.cue_ball_sunk})
            # json_content.append({"last_table": MyHandler.current_game.most_recent_table.svg()})
            # json_content.append({"last_table_time": MyHandler.current_game.most_recent_table.time})
            
            # Convert the JSON object to a string
            response_content = json.dumps(json_content)
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

    def reset_display_html(self) -> None:
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

    def box(self, string: str = None) -> str:
        return f'<div class="infoBox">{string}</div>'
    
def main() -> None:
    # if len(sys.argv) < 2:
    #     print("Need a command line argument!")
    #     # need to use exit instead of return
    #     sys.exit(1)  # Exit the script
    temp = Physics.Database(reset=True)
    temp.close()
    del temp
    from subprocess import DEVNULL
    remove_video()
    # port_num = int(sys.argv[1]) + int(5e4)
    port_num = 3000
    # d is for daemon
    httpd = HTTPServer(('localhost', port_num), MyHandler)
    # delete any SVG files currently existing
    print("Server listening in port: ", port_num)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nCanceled with Ctrl + C')
        httpd.shutdown()
        # MyHandler.current_game.close()

if __name__ == "__main__":
    main()
