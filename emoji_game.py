import emoji_parse
import model
import numpy
import datetime
import random

SIZE = 4

def get_daily_puzzle():
    today = datetime.date.today()
    seed = today.year * 10000 + today.month * 100 + today.day
    rng = random.Random(seed)
    available = list(emoji_parse.emoji_names.items())
    chosen = rng.sample(available, 2)
    positions = rng.sample([(r, c) for r in range(SIZE) for c in range(SIZE)], 2)
    return [
        {'row': row, 'col': col, 'emoji': emoji, 'phrase': name}
        for (emoji, name), (row, col) in zip(chosen, positions)
    ]

def check_phrase(phrase: str):
    display = emoji_parse.get_emoji_from_line(model.clean_phrase(phrase))
    return display


def analyze_grid(grid):
    cell_scores = {}
    duplicates = False

    vecs = {}
    for x in range(SIZE):
        for y in range(SIZE):
            cell = grid[x][y]
            if not cell or not cell.get('emoji'):
                continue
            vec = emoji_parse.emoji_map.get(cell['emoji'])
            if vec is not None:
                vecs[f'cell{x}-{y}'] = vec

    for x in range(SIZE):
        for y in range(SIZE):
            cell_id = f'cell{x}-{y}'
            if cell_id not in vecs:
                continue

            for xi in range(x + 1, SIZE):
                other_id = f'cell{xi}-{y}'
                if other_id not in vecs:
                    continue
                sim = float(model.cosine_similarity(vecs[cell_id], vecs[other_id]))
                cell_scores[cell_id] = cell_scores.get(cell_id, 0.0) + sim
                cell_scores[other_id] = cell_scores.get(other_id, 0.0) + sim

            for yi in range(y + 1, SIZE):
                other_id = f'cell{x}-{yi}'
                if other_id not in vecs:
                    continue
                sim = float(model.cosine_similarity(vecs[cell_id], vecs[other_id]))
                cell_scores[cell_id] = cell_scores.get(cell_id, 0.0) + sim
                cell_scores[other_id] = cell_scores.get(other_id, 0.0) + sim

    seen = {}
    for x in range(SIZE):
        for y in range(SIZE):
            cell = grid[x][y]
            if not cell or not cell.get('emoji'):
                continue
            emoji = cell['emoji']
            if emoji in seen:
                duplicates = True
            else:
                seen[emoji] = f'cell{x}-{y}'

    score = sum(cell_scores.values()) / 2
    full = all(
        grid[x][y] and grid[x][y].get('emoji')
        for x in range(SIZE) for y in range(SIZE)
    )
    return {'score': score, 'cell_scores': cell_scores, 'duplicates': duplicates, 'full': full}