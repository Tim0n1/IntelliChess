from stockfish import Stockfish

engine = Stockfish(path='stockfish_15.1_win_x64_avx2/stockfish-windows-2022-x86-64-avx2.exe')
engine.set_fen_position('r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R')
print(engine.get_board_visual())
print('best move ', engine.get_best_move())