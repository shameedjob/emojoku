from flask import Flask,render_template, request, jsonify
import emoji_game
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/daily_puzzle', methods=['GET'])
def daily_puzzle():
    return jsonify(emoji_game.get_daily_puzzle()), 200

@app.route('/check_guess', methods=['GET'])
def check_phrase():
    phrase = request.args.get('phrase')
    guess = emoji_game.check_phrase(phrase)
    print(phrase, guess)
    if guess:
        return jsonify({'emoji': guess}), 200
    else:
        return jsonify({}), 400

@app.route('/update_grid', methods=['POST'])
def update_grid():
    grid = request.get_json().get('grid', [])
    result = emoji_game.analyze_grid(grid)
    print(result)
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)