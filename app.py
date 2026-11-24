"""
Name: AyeThiriPyoneNaing
Student ID: 8625teet
Module: 5FTC2067 Artificial Intelligence Principles
Project: Dice Tic-Tac-Toe with Expectiminimax AI
"""

import random
import streamlit as st

# Each of the 9 squares is assigned a target die face (1-6)
CELL_NUMBERS = [1, 2, 3, 4, 5, 6, 1, 2, 3]

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),  # Horizontal rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),  # Vertical columns
    (0, 4, 8), (2, 4, 6)              # Diagonals
]


def check_winner(board):
    """
    Determines whether a player has achieved three-in-a-row or if the board is full.
    Parameters:
        board (list[str]): 9-element list storing 'X' (Human), 'O' (AI), or ' ' (Empty).
    Returns:
        str or None: 'X', 'O', 'Draw', or None if the game is still active.
    """
    for idx_a, idx_b, idx_c in WIN_LINES:
        if board[idx_a] != ' ' and board[idx_a] == board[idx_b] == board[idx_c]:
            return board[idx_a]
    if ' ' not in board:
        return 'Draw'
    return None


def get_valid_moves(board, dice_roll):
    """
    Returns all legal square indices for the given die roll.
    If all squares matching dice_roll are taken, any empty square becomes legal.
    Parameters:
        board (list[str]): Current 9-element game board state.
        dice_roll (int): Rolled die value between 1 and 6.
    Returns:
        list[int]: Valid board indices (0-8) for the current turn.
    """
    matching_cells = [
        idx for idx, mark in enumerate(board)
        if mark == ' ' and CELL_NUMBERS[idx] == dice_roll
    ]
    if matching_cells:
        return matching_cells
    return [idx for idx, mark in enumerate(board) if mark == ' ']


def evaluate_board(board):
    """
    Scores a board state from the AI's ('O') perspective using tactical heuristics.
    Parameters:
        board (list[str]): Current 9-element game board state.
    Returns:
        float: Positive score favors AI ('O'), negative favors Human ('X').
    """
    winner = check_winner(board)
    if winner == 'O':
        return 100.0
    if winner == 'X':
        return -100.0
    if winner == 'Draw':
        return 0.0

    heuristic_score = 0.0
    for idx_a, idx_b, idx_c in WIN_LINES:
        line = [board[idx_a], board[idx_b], board[idx_c]]
        if line.count('O') == 2 and line.count(' ') == 1:
            heuristic_score += 10.0
        elif line.count('X') == 2 and line.count(' ') == 1:
            heuristic_score -= 12.0  # Prioritize blocking immediate human wins
        elif line.count('O') == 1 and line.count(' ') == 2:
            heuristic_score += 2.0

    if board[4] == 'O':
        heuristic_score += 3.0  # Bonus for controlling the center cell (index 4)
    return heuristic_score


def expectiminimax(board, depth, node_type, dice_roll=None):
    """
    Recursively computes expected utility across decision nodes (MAX/MIN) and dice chance nodes.
    Parameters:
        board (list[str]): Current 9-element game board state.
        depth (int): Remaining search depth in plies.
        node_type (str): 'MAX', 'MIN', 'CHANCE_MAX', or 'CHANCE_MIN'.
        dice_roll (int or None): Specific die face (1-6) when evaluating MAX or MIN nodes.
    Returns:
        float: Expected utility value of the board state.
    """
    if check_winner(board) is not None or depth == 0:
        return evaluate_board(board)

    if node_type == 'CHANCE_MAX':
        expected_value = 0.0
        for roll in range(1, 7):
            expected_value += (1.0 / 6.0) * expectiminimax(board, depth, 'MAX', roll)
        return expected_value

    if node_type == 'CHANCE_MIN':
        expected_value = 0.0
        for roll in range(1, 7):
            expected_value += (1.0 / 6.0) * expectiminimax(board, depth, 'MIN', roll)
        return expected_value

    if node_type == 'MAX':
        best_value = -float('inf')
        for move in get_valid_moves(board, dice_roll):
            board[move] = 'O'
            val = expectiminimax(board, depth - 1, 'CHANCE_MIN')
            board[move] = ' '
            best_value = max(best_value, val)
        return best_value

    best_value = float('inf')
    for move in get_valid_moves(board, dice_roll):
        board[move] = 'X'
        val = expectiminimax(board, depth - 1, 'CHANCE_MAX')
        board[move] = ' '
        best_value = min(best_value, val)
    return best_value


def choose_ai_move(board, dice_roll, depth=2):
    """
    Evaluates all legal moves for the AI's rolled die and picks the highest-utility square.
    Parameters:
        board (list[str]): Current 9-element game board state.
        dice_roll (int): Die value rolled by the AI (1-6).
        depth (int): Lookahead depth for Expectiminimax search.
    Returns:
        tuple[int, dict]: Selected board index (0-8) and dictionary of move scores.
    """
    valid_moves = get_valid_moves(board, dice_roll)
    move_scores = {}
    best_move = valid_moves.__getitem__(0)

    best_score = -float('inf')

    for move in valid_moves:
        board[move] = 'O'
        score = expectiminimax(board, depth, 'CHANCE_MIN')
        board[move] = ' '
        move_scores[move] = round(score, 2)
        if score > best_score:
            best_score = score
            best_move = move

    return best_move, move_scores


def run_benchmark(num_games=30, depth=2):
    """
    Simulates automated games between Expectiminimax AI ('O') and a Random agent ('X').
    Parameters:
        num_games (int): Number of full matches to simulate.
        depth (int): Search depth used by the Expectiminimax AI.
    Returns:
        dict: Win counts for AI, Random opponent, and Draws.
    """
    results = {"Expectiminimax AI (O)": 0, "Random Agent (X)": 0, "Draw": 0}
    for _ in range(num_games):
        sim_board = [' '] * 9
        turn = 'X'
        while True:
            roll = random.randint(1, 6)
            moves = get_valid_moves(sim_board, roll)
            if turn == 'X':
                chosen = random.choice(moves)
                sim_board[chosen] = 'X'
                turn = 'O'
            else:
                chosen, _ = choose_ai_move(sim_board, roll, depth=depth)
                sim_board[chosen] = 'O'
                turn = 'X'
            outcome = check_winner(sim_board)
            if outcome == 'O':
                results["Expectiminimax AI (O)"] += 1
                break
            if outcome == 'X':
                results["Random Agent (X)"] += 1
                break
            if outcome == 'Draw':
                results["Draw"] += 1
                break
    return results


def init_session():
    """
    Initializes or resets Streamlit session state variables for a fresh match.
    Parameters:
        None
    Returns:
        None
    """
    st.session_state.board = [' '] * 9
    st.session_state.dice_roll = random.randint(1, 6)
    st.session_state.winner = None
    st.session_state.ai_analysis = {}
    st.session_state.status_msg = f"Your turn! Rolled a {st.session_state.dice_roll}."


# --- STREAMLIT WEB INTERFACE ---
st.set_page_config(page_title="Dice Tic-Tac-Toe AI", page_icon="🎲", layout="centered")
st.title("🎲 Dice Tic-Tac-Toe (Expectiminimax AI)")
st.caption("Name: [AyeThiriPyoneNaing] | Student ID: [8625teet] | Module: 5FTC2067")

if 'board' not in st.session_state:
    init_session()

with st.sidebar:
    st.header("⚙️ AI Settings & Testing")
    search_depth = st.selectbox("AI Lookahead Depth", options=(1, 2), index=1)

    if st.button("📊 Run 30-Game AI Benchmark"):
        bench = run_benchmark(num_games=30, depth=search_depth)
        st.write("**Benchmark Results (30 Games):**")
        st.json(bench)

col_status, col_reset = st.columns((3, 1))
with col_status:
    if st.session_state.winner == 'X':
        st.success("🎉 You (X) win!")
    elif st.session_state.winner == 'O':
        st.error("🤖 Expectiminimax AI (O) wins!")
    elif st.session_state.winner == 'Draw':
        st.warning("🤝 Match ended in a Draw!")
    else:
        st.info(f"🎲 Rolled Die: **{st.session_state.dice_roll}** — {st.session_state.status_msg}")

with col_reset:
    if st.button("🔄 New Game", use_container_width=True):
        init_session()
        st.rerun()

legal_moves = [] if st.session_state.winner else get_valid_moves(
    st.session_state.board, st.session_state.dice_roll
)

for row in range(3):
    cols = st.columns(3)
    for col in range(3):
        cell_idx = row * 3 + col
        mark = st.session_state.board[cell_idx]
        target_die = CELL_NUMBERS[cell_idx]
        btn_label = mark if mark != ' ' else f"Die: {target_die}"

        if cols[col].button(
            btn_label,
            key=f"btn_{cell_idx}",
            disabled=(cell_idx not in legal_moves),
            use_container_width=True
        ):
            st.session_state.board[cell_idx] = 'X'
            st.session_state.winner = check_winner(st.session_state.board)

            if st.session_state.winner is None:
                ai_roll = random.randint(1, 6)
                ai_choice, scores = choose_ai_move(
                    st.session_state.board, ai_roll, depth=search_depth
                )
                st.session_state.board[ai_choice] = 'O'
                st.session_state.ai_analysis = {
                    "AI Die Roll": ai_roll,
                    "Chosen Square": f"Cell {ai_choice + 1}",
                    "Expected Values": {
                        f"Cell {k + 1} (Die {CELL_NUMBERS[k]})": v for k, v in scores.items()
                    }
                }
                st.session_state.winner = check_winner(st.session_state.board)
                if st.session_state.winner is None:
                    st.session_state.dice_roll = random.randint(1, 6)
                    st.session_state.status_msg = (
                        f"AI rolled {ai_roll} -> Cell {ai_choice + 1}. "
                        f"Your roll: {st.session_state.dice_roll}."
                    )
            st.rerun()

