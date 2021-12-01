import chess
import chess.pgn
from player import set_player_dict, player_info_extractor
from game import set_game_dict, game_info_extractor
from move import set_move_dict, move_info_extractor,\
    bitmap_representer, castling_right, en_passant_opp, halfmove_clock
from io import StringIO

class PreData:
    def __init__(self) -> None:
        # Set list of Pieces
        self.PIECES=[
            chess.Piece.from_symbol('P'),
            chess.Piece.from_symbol('N'),
            chess.Piece.from_symbol('B'),
            chess.Piece.from_symbol('R'),
            chess.Piece.from_symbol('Q'),
            chess.Piece.from_symbol('K'),
            chess.Piece.from_symbol('p'),
            chess.Piece.from_symbol('n'),
            chess.Piece.from_symbol('b'),
            chess.Piece.from_symbol('r'),
            chess.Piece.from_symbol('q'),
            chess.Piece.from_symbol('k')
            ]

        #Set list of all squares on the board
        self.SQUARES = [i for i in range(64)]

        #Define move limit for data padding
        self.max_game_length = 100

    # def read_data(self):
    #     uploaded_file = upload_pgn()
    #     if uploaded_file is not None:
    #         bytes_data = uploaded_file.getvalue()
    #         # To convert to a string based IO:
    #         pgn = StringIO(bytes_data.decode("utf-8"))
    #         return pgn

    def import_data(
            self,
            pgn,
            #uploaded_file,
            import_lim=50):
        '''
        Takes a number of games to be read from a pgn file (Default: import_lim=50)
        as well as a data source.
        Returns three dictonaries (players, games, moves).
        '''

        #pgn = self.read_data(uploaded_file)

        # read file
        game_counter = 0
        games_parsed = 0
        move_counter = 0

        #preshape dataframes
        player_dict = set_player_dict()
        game_dict = set_game_dict()
        move_dict = set_move_dict()

        while True:  # keep reading games
            try:
                game = chess.pgn.read_game(pgn)
                board = game.board()
                moves = list(game.mainline_moves())
                variations = game.mainline()
                eval_log = {'evals': []}

                if "Annotator" in game.headers:
                    if game.headers["Annotator"] == "lichess.org":
                        eval_source = "lichess"
                    else:
                        eval_source = "other"

                if len(moves) > 5:
                    # Player info parsing
                    players = player_info_extractor(game=game,
                                                    player_dict=player_dict)

                    # Game info parsing
                    games = game_info_extractor(game=game,
                                                game_dict=game_dict,
                                                game_counter=game_counter)

                    #cycle through evals
                    for variation in variations:
                        eval = variation.comment
                        if "%eval" in eval:
                            eval = eval.split('[%eval ')[1].split(']')[0]
                            try:
                                eval_log['evals'].append(float(eval))
                            except ValueError:
                                eval_log['evals'].append("NA")
                        else:
                            eval_log['evals'].append("NA")

                    move_dict["Evaluation"].append(eval_log["evals"])

                    # Moves info parsing
                    white = True
                    for move in moves:
                        board.push(move)

                        # move_dict = move_dict_maker(game=game,
                        #                             board=board,
                        #                             move_dict=move_dict,
                        #                             white=white,
                        #                             pieces=self.PIECES)

                        #Extract GAME ID and FEN moves
                        move_dict = move_info_extractor(game=game,
                                                        board=board,
                                                        move_dict=move_dict,
                                                        game_counter=game_counter)

                        #Generate bitmap representation of FENs
                        move_dict = bitmap_representer(board=board,
                                                    pieces=self.PIECES,
                                                    squares=self.SQUARES,
                                                    move_dict=move_dict)

                        #Extract turn color and castling availablity
                        move_dict, white = castling_right(game=game,
                                                board=board,
                                                move_dict=move_dict,
                                                white=white)

                        #Identify (pseudo) en passant opportunity
                        move_dict = en_passant_opp(board=board,
                                                move_dict=move_dict)

                        #Extract Halfmove clock
                        move_dict = halfmove_clock(board=board,
                                                move_dict=move_dict)

                        move_counter += 1
                    games_parsed += 1

                game_counter += 1
                if game_counter == import_lim:  # number of games to read
                    break
            except AttributeError:  # no further games to read
                print('No further games to load.')
                break

        move_dict["Evaluation"] = self.flatten_list(move_dict["Evaluation"])

        #if eval_source == "lichess":
        #    move_dict["Evaluation"] = [i * 100 if i != "NA" else "NA" for i in move_dict["Evaluation"]]

        print(f'{game_counter} games read.')
        print(
            f'{games_parsed} games with a total number of {move_counter} moves parsed.'
        )
        return players, games, move_dict

    def flatten_list(self, _2d_list):
        flat_list = []
        # Iterate through the outer list
        for element in _2d_list:
            if type(element) is list:
                # If the element is of type list, iterate through the sublist
                for item in element:
                    flat_list.append(item)
            else:
                flat_list.append(element)
        return flat_list
