import streamlit as st
# import pandas as pd
# import numpy as np
# import matplotlib.pyplot as plt
import requests
from io import StringIO
from frontend_data import PreData
import json
import time
from stockfish import Stockfish

st.set_page_config(page_title='Chess Engine Detective', page_icon="🕵️‍♀️")
st.title('🔎 Chess Engine Detective')

# stockfish init
# stockfish = Stockfish(
#     '/home/vini/Personal/test_project/stockfish_14_linux_x64/stockfish_14_linux_x64/stockfish_14_x64',
#     parameters={"Threads": 2, 'Min Split Depth': 20, 'Ponder':True}
# )
# stockfish.set_elo_rating(2600)
# stockfish.set_skill_level(30)


# HEADER
# st.write('# CHESS FILES')
#st.write('## Human vs Engine Detection')
img = "https://images3.alphacoders.com/235/235755.jpg"
st.image(img)


# DATA
# @st.cache
# def get_data():
#     url_ep = 'http://127.0.0.1:8000/data'
#     res = requests.get(url_ep)
#     result = res.json()
#     df_players = pd.DataFrame(result['players'])
#     df_games = pd.DataFrame(result['games'])
#     # df_moves = pd.DataFrame(result['moves'])
#     return df_players, df_games #, df_moves

# df_players, df_games = get_data()


# SIDEBAR
# def sidebar():
#     """
#     sidebar dropdown player/games list
#     """
#     # title
#     st.sidebar.write('## Local Viewbar')
#     st.sidebar.write('### Computer vs player files')
#     # dropdown
#     add_selectbox = st.sidebar.selectbox(
#         "Select list view.",
#         ("players", "games")
#     )
#     if add_selectbox == 'players':
#         white = df_players['White'].unique()
#         black = df_players['Black'].unique()
#         players = np.concatenate((white, black))
#         st.sidebar.write(players)

#     if add_selectbox == 'games':
#         st.sidebar.write('See Mainscreen View')
#         st.write('### Local Games')
#         st.write(df_games)

# sidebar()


# def sidebar_player_search():
#     """
#     Local DB Player search with ranking progression graph
#     """
#     input_name = st.sidebar.text_input('Search Local DB Player Names', '')
#     if input_name:
#         white = df_games[df_games['White'] == input_name]
#         black = df_games[df_games['Black'] == input_name]
#         player = white.append(black)
#         if len(player) > 0:
#             st.sidebar.write('Mainscreen View')
#             st.write(f"### {input_name}'s games")
#             st.write(player)

#             if len(white) > 2 and len(black) > 2:
#                 # PLOT
#                 fig, ax = plt.subplots(figsize=(18,8))
#                 # player['Date'] = pd.to_datetime(player['Date'])
#                 # player.sort_values(by='Date', inplace=True)
#                 plt.subplot(1,2,1)
#                 plt.title('as White')
#                 plt.plot(white['White_Elo'])
#                 plt.grid()
#                 plt.subplot(1,2,2)
#                 plt.title('as Black')
#                 plt.plot(black['Black_Elo'])
#                 plt.grid()
#                 st.pyplot(fig)
#         else:
#             st.sidebar.write(f'Player name "{input_name}" not found.')

# sidebar_player_search()


#st.write('## Human vs Human?')

def dropdown():
    """
    sidebar dropdown white/black player list
    """
    # title
    st.sidebar.title('Select Player')
    # dropdown
    add_selectbox = st.sidebar.selectbox(
        "Which player do you want to verify?",
        ("White", "Black")
    )
    if add_selectbox == 'White':
        #st.sidebar.write('White player')
        player = "White"

    if add_selectbox == 'Black':
        #st.sidebar.write('Black player')
        player = "Black"

    return player

def get_evals(move_dict):
    stockfish = Stockfish(parameters={"Threads": 2,
                                      'Min Split Depth': 26,
                                      'Ponder':True})
    stockfish.set_elo_rating(2600)
    stockfish.set_skill_level(30)

    eval_list = []
    for i in move_dict["FEN_moves"]:
        stockfish.set_fen_position(i)
        try:
            eval_list.append(stockfish.get_evaluation()["value"])
        except ValueError:
            eval_list.append("NA")

    return eval_list

# UPLOAD PGN FILE
def upload_pgn():
    """
    PGN needs StringIO to be read so file can be read as a string. chess library loses strength here, hence stockfish.
    """
    st.write('### Load Your Game')

    uploaded_file = st.file_uploader("Feed the engine with PGN file")

    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.getvalue()
        # To convert to a string based IO:
        pgn = StringIO(bytes_data.decode("utf-8"))
        # print(type(stringio))

        player = dropdown()
        with st.spinner(text="Chasing this bot 🔎"):
            time.sleep(6)
        with st.spinner(text="Almost done 👀"):
            time.sleep(6)
        player_dict, game_dict, move_dict = PreData().import_data(pgn=pgn,import_lim=1)

        # eval_list = get_evals(move_dict)

        # CHESS.PGN
        # game = chess.pgn.read_game(pgn)
        # print(type(game))
        # board = game.board()
        # moves = list(game.mainline_moves())
        # variations = game.mainline()  # variation.comment no longer exists - REGEX vs Stockfish ?

        # evals = []
        # for move in moves:
        #     board.push(move)
        #     fen = board.fen()
        #     stockfish.set_fen_position(fen)
        #     eval = stockfish.get_evaluation()
        #     evals.append(float(eval['value']))

        #for move in moves:
        #    st.write(str(move))


        #PLOT GAME EVALS
        # st.write('Powered by Stockfish 14')
        # fig, ax = plt.subplots()
        # plt.title(f"{game.headers['White']} vs {game.headers['Black']}")
        # plt.plot(evals)
        # zeros = np.zeros(len(evals))
        # plt.plot(zeros)
        # plt.ylabel('CP Advantage')
        # plt.xlabel('Moves')
        # plt.grid()

        # fen_list = []
        # for i in range(len(move_dict["FEN_moves"])):
        #     fen = move_dict["FEN_moves"][i]
        #     fen_list.append(fen)

        #st.write(move_dict["Bitmap_moves"][0])

        params = {
        'Game_ID': move_dict["Game_ID"],
        "FEN_moves": move_dict["FEN_moves"],
        "Bitmap_moves": move_dict["Bitmap_moves"],
        "WhiteIsComp": move_dict["WhiteIsComp"],
        "turn": move_dict["turn"],
        "Castling_right": move_dict["Castling_right"],
        "EP_option": move_dict["EP_option"],
        "Pseudo_EP_option": move_dict["Pseudo_EP_option"],
        "Halfmove_clock": move_dict["Halfmove_clock"],
        #"Evaluation": move_dict["Evaluation"], #eval_list,
        "Player_color": player
        }

        url_ep = 'http://127.0.0.1:8000/predict'
        url_api = "https://cc-detector-z242n5ixpq-ew.a.run.app/predict"

        post = requests.post(url_api,json=params)
        result = post.json()
        pred = json.loads(result['prediction'])

        if pred > 0.7:
            st.error(f'⚠️The player might have used the support of a chess engine 🤖')
        else:
            st.success('✅Player is probably a human 💃')

upload_pgn()
