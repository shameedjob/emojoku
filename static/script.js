
let toastTimer = null;
function showToast(msg) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('show'), 1000);
}

function simColor(value) {
    const t = Math.min(value / 2, 1);
    if (t < 0.5) {
        const s = t / 0.5;
        const r = Math.round(129 + s * (179 - 129));
        const g = Math.round(131 + s * (159 - 131));
        const b = Math.round(132 + s * (59  - 132));
        return `rgb(${r},${g},${b})`;
    } else {
        const s = (t - 0.5) / 0.5;
        const r = Math.round(179 + s * (230 - 179));
        const g = Math.round(159 + s * (57  - 159));
        const b = Math.round(59  + s * (70  - 59 ));
        return `rgb(${r},${g},${b})`;
    }
}

function setCellScore(row, col, value) {
    const cell = document.getElementById(`cell${row}-${col}`);
    if (!cell) return;
    const score = cell.querySelector('.cell-score');
    if (!score) return;
    // value = value/2;
    score.textContent = value.toFixed(1);
    score.style.color = simColor(value);
}

function buildGridData() {
    const grid = [];
    for (let row = 0; row < 4; row++) {
        const rowData = [];
        for (let col = 0; col < 4; col++) {
            const cell = document.getElementById(`cell${row}-${col}`);
            const emojiEl = cell ? cell.querySelector('.emoji') : null;
            const labelEl = cell ? cell.querySelector('.emoji-label') : null;
            rowData.push({
                emoji:  emojiEl  ? emojiEl.textContent  : null,
                phrase: labelEl  ? labelEl.textContent  : null,
            });
        }
        grid.push(rowData);
    }
    return grid;
}

function buildShareText(score) {
    const rows = [];
    for (let row = 0; row < 4; row++) {
        let line = '';
        for (let col = 0; col < 4; col++) {
            const cell = document.getElementById(`cell${row}-${col}`);
            const emojiEl = cell ? cell.querySelector('.emoji') : null;
            line += emojiEl ? emojiEl.textContent : '⬛';
        }
        rows.push(line);
    }
    rows.push('');
    rows.push(`EMOJOKU — Score: ${score.toFixed(1)}/10.0`);
    return rows.join('\n');
}

function showEndGame(win, reason, score) {
    document.getElementById('endgame-title').textContent = win ? 'YOU WIN' : 'GAME OVER';
    document.getElementById('endgame-reason').textContent = reason;
    document.getElementById('endgame-score').textContent = `Final score: ${score.toFixed(1)}/10.0`;
    document.getElementById('copy-confirm').style.display = 'none';

    const grid = document.getElementById('endgame-grid');
    grid.innerHTML = '';
    for (let row = 0; row < 4; row++) {
        for (let col = 0; col < 4; col++) {
            const cell = document.getElementById(`cell${row}-${col}`);
            const emojiEl = cell ? cell.querySelector('.emoji') : null;
            const span = document.createElement('span');
            span.textContent = emojiEl ? emojiEl.textContent : '⬛';
            grid.appendChild(span);
        }
    }

    document.getElementById('endgame-overlay').classList.add('open');
}

function applyGridResult(data) {
    document.getElementById('similarity-value').textContent = data.score.toFixed(1);

    for (const [cellId, value] of Object.entries(data.cell_scores)) {
        const cell = document.getElementById(cellId);
        if (!cell) continue;
        const color = simColor(value);
        const score = cell.querySelector('.cell-score');
        if (score) {
            score.textContent = value.toFixed(1);
            score.style.color = color;
        }
        const input = cell.querySelector('.cell-input');
        if (input) input.style.borderColor = color;
    }

    if (data.duplicates) {
        showEndGame(false, 'You placed a duplicate emoji!', data.score);
    } else if (data.score >= 10.0) {
        showEndGame(false, 'Similarity reached 10.0 — too many similar emojis!', data.score);
    } else if (data.full) {
        showEndGame(true, 'You filled the grid without repeating!', data.score);
    }
}

function sendGrid() {
    fetch('/update_grid', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ grid: buildGridData() }),
    })
    .then(response => response.ok ? response.json() : null)
    .then(data => { if (data) applyGridResult(data); });
}

function insertEmoji(element, emoji, emojiLabel) {
  const h1 = document.createElement('h1');
  h1.className = 'emoji';
  h1.textContent = emoji;

  console.log(emoji)

  const p = document.createElement('p');
  p.className = 'emoji-label';
  p.textContent = emojiLabel;

  element.appendChild(h1);
  element.appendChild(p);
}

document.addEventListener("DOMContentLoaded", ()=>{
    var elements = document.getElementsByClassName('cell-input');
    for(let i = 0; i < elements.length; i++){
        elements[i].addEventListener('mouseenter', () => {
            const td = elements[i].closest('td');
            if (!td) return;
            const [row, col] = td.id.replace('cell', '').split('-').map(Number);
            for (let r = 0; r < 4; r++) {
                if (r !== row) document.getElementById(`cell${r}-${col}`)?.querySelector('.cell-input')?.classList.add('aoe-highlight');
            }
            for (let c = 0; c < 4; c++) {
                if (c !== col) document.getElementById(`cell${row}-${c}`)?.querySelector('.cell-input')?.classList.add('aoe-highlight');
            }
        });
        elements[i].addEventListener('mouseleave', () => {
            document.querySelectorAll('.cell-input.aoe-highlight').forEach(el => el.classList.remove('aoe-highlight'));
        });

        elements[i].addEventListener('click', ()=>{

            var test_phrase = document.getElementById('word-input').value
            document.getElementById('word-input').value = ''
            if (test_phrase){
                fetch(`/check_guess?phrase=${test_phrase}`).then(
                    response=>{
                        if (!response.ok) { showToast('Word not found'); return; }
                        return response.json();
                    }
                ).then(
                    data=>
                    {
                        insertEmoji(
                            elements[i], data.emoji, test_phrase
                        );
                        // elements[i].classList.add('correct');
                        sendGrid();
                    }
                )
            }
        })
    }

    fetch('/daily_puzzle').then(r => r.json()).then(puzzle => {
        puzzle.forEach(({row, col, emoji, phrase}) => {
            const cell = document.getElementById(`cell${row}-${col}`);
            if (!cell) return;
            const input = cell.querySelector('.cell-input');
            if (input && !input.querySelector('.emoji')) insertEmoji(input, emoji, phrase);
        });
        sendGrid();
    });

    document.getElementById('share-btn').addEventListener('click', () => {
        const score = parseFloat(document.getElementById('similarity-value').textContent);
        navigator.clipboard.writeText(buildShareText(score)).then(() => {
            const confirm = document.getElementById('copy-confirm');
            confirm.style.display = 'block';
            setTimeout(() => { confirm.style.display = 'none'; }, 2000);
        });
    });

    const overlay = document.getElementById('tutorial-overlay');
    document.getElementById('help-btn').addEventListener('click', () => {
        overlay.classList.add('open');
    });
    document.getElementById('tutorial-close').addEventListener('click', () => {
        overlay.classList.remove('open');
    });
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) overlay.classList.remove('open');
    });
});