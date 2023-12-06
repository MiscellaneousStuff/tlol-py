# MIT License
# 
# Copyright (c) 2023 MiscellaneousStuff
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from queue import Queue
from threading import Thread
import argparse

from flask import Flask, request, jsonify, send_from_directory
from tlol.replays.scraper import ReplayScraper

# Set up argparse
parser = argparse.ArgumentParser(description="League of Legends Replay Data Service")
parser.add_argument('--host', default='127.0.0.1', type=str, help='Host for replay scraping server')
parser.add_argument('--port', default=5000, type=int, help='Port for replay scraping server')
parser.add_argument('--game_dir', required=True, type=str, help='League of Legends game directory')
parser.add_argument('--replay_dir', required=True, type=str, help='League of Legends *.rofl replay directory')
parser.add_argument('--dataset_dir', required=True, type=str, help='JSON replay files output directory')
parser.add_argument('--scraper_dir', required=True, type=str, help='Path to the scraper program')
parser.add_argument('--replay_speed', default=8, type=int, help='League client replay speed during scraping')

args = parser.parse_args()

app = Flask(__name__)
scraping_queue = Queue()
completed_games = {}  # To store completed game data

scraper = ReplayScraper(
        game_dir=args.game_dir,
        replay_dir=args.replay_dir,
        dataset_dir=args.dataset_dir,
        scraper_dir=args.scraper_dir,
        region="",
        replay_speed=args.replay_speed)

# Flask Endpoints
@app.route('/scrape_game', methods=['POST'])
def scrape_game():
    game_id = request.json.get('game_id')
    scraping_queue.put(game_id)
    return jsonify({"message": f"Game {game_id} added to the queue"}), 202

@app.route('/scraping_progress', methods=['POST'])
def scraping_progress():
    return jsonify(list(completed_games.keys())), 200

@app.route('/remove_game', methods=['POST'])
def remove_game():
    game_id = request.json.get('game_id')
    # Logic to remove the game from the queue or mark it as not needed
    return jsonify({"message": f"Game {game_id} removal requested"}), 200

@app.route('/download_game/<game_id>', methods=['POST'])
def download_game(game_id):
    directory = args.dataset_dir
    filename = f"{game_id}.json"  # Adjust based on how you store files
    return send_from_directory(directory, filename, as_attachment=True)

# Function to process the scraping queue
def process_queue():
    while True:
        if not scraping_queue.empty():
            game_id = scraping_queue.get()
            completed_games[game_id] = True

if __name__ == "__main__":
    thread = Thread(target=process_queue)
    thread.daemon = True
    thread.start()
    app.run(debug=True, host=args.host, port=args.port)