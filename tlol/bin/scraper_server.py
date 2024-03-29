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

import os

from queue import Queue
from threading import Thread
import argparse

from flask import Flask, request, jsonify, send_from_directory, after_this_request, Response
from tlol.replays.scraper import ReplayScraper

# Set up argparse
parser = argparse.ArgumentParser(description="League of Legends Replay Data Service")
parser.add_argument('--host', default='127.0.0.1', type=str, help='Host for replay scraping server')
parser.add_argument('--port', default=5000, type=int, help='Port for replay scraping server')
parser.add_argument('--game_dir', required=True, type=str, help='League of Legends game directory')
parser.add_argument('--replay_dir', required=True, type=str, help='League of Legends *.rofl replay directory')
parser.add_argument('--dataset_dir', required=True, type=str, help='JSON replay files output directory')
parser.add_argument('--scraper_dir', required=True, type=str, help='Path to the scraper program')

args = parser.parse_args()

app = Flask(__name__)
scraping_queue = Queue()
currently_scraping = ""

def get_queue_contents(queue):
    temp_list = []
    temp_queue = Queue()

    # Transfer all items to a temporary list and a temporary queue
    while not queue.empty():
        item = queue.get()
        temp_list.append(item)
        temp_queue.put(item)

    # Put items back into the original queue
    while not temp_queue.empty():
        queue.put(temp_queue.get())

    return temp_list

def check_existing_scraped_replay(game_id):
    full_path = os.path.join(args.dataset_dir, f"{game_id}.json")
    print("DOES IT EXIST?:", full_path)
    return os.path.exists(full_path)

@app.route('/api/scrape/add', methods=['POST'])
def scrape_add():
    try:
        game_id = request.json.get('game_id')

        if check_existing_scraped_replay(game_id):
            return jsonify({"message": f"Game {game_id} already exists!"}), 202
        else:
            replay_speed = request.json.get('replay_speed')
            end_time     = request.json.get('end_time')
            scrape_request = {
                "game_id": game_id,
                "replay_speed": replay_speed,
                "end_time": end_time
            }
            scraping_queue.put(scrape_request)
            return jsonify({"message": f"Game {game_id} added to the queue"}), 202
    except Exception as e:
        return jsonify({
            "error":
            f"Internal server error while adding game: {str(e)}"}
        ), 500
    
@app.route('/api/scrape/list', methods=['GET'])
def scrape_list():
    lst = os.listdir(args.dataset_dir)
    lst = [fi.replace(".json", "") for fi in lst]
    if lst:
        return jsonify(lst), 200
    else:
        return jsonify("No replays scraped!"), 200

@app.route('/api/scrape/queue', methods=['GET'])
def scrape_queue():
    lst = get_queue_contents(scraping_queue)
    return jsonify({"queue": lst}), 200

@app.route('/api/scrape/current', methods=['GET'])
def scrape_current():
    return jsonify(currently_scraping), 200

@app.route('/api/scrape/remove/<game_id>', methods=['DELETE'])
def scrape_remove(game_id):
    global scraping_queue
    try:
        # Create a temporary queue
        temp_queue = Queue()

        # Transfer all items except the one to remove to the temporary queue
        while not scraping_queue.empty():
            item = scraping_queue.get()
            if item['game_id'] != game_id:
                temp_queue.put(item)

        # Swap the queues
        scraping_queue = temp_queue

        return jsonify({"message": f"Game {game_id} removal requested"}), 200
    except Exception as e:
        return jsonify({"error": f"Error during removal of game {game_id}: {str(e)}"}), 500

@app.route('/api/scrape/download/<game_id>', methods=['GET'])
def scrape_download(game_id):
    directory = args.dataset_dir  # Replace with your directory path
    filename = f"{game_id}.json"  # Adjust based on how you store files
    full_path = os.path.join(directory, filename)
    
    if os.path.exists(full_path):
        chunk_size = 1024 * 1024 # MiB

        def generate():
            with open(full_path, 'rb') as file:
                while True:
                    data = file.read(chunk_size)
                    if not data:
                        break
                    yield data

        return Response(generate(), 
                        mimetype='application/zip',
                        headers={'Content-Disposition': f'attachment; filename={filename}'})
    else:
        return f"Scraped replay file: {game_id}, doesn't exist", 404

@app.route('/api/scrape/download_rofl/<game_id>', methods=['GET'])
def scrape_download_rofl(game_id):
    directory = args.replay_dir  # Replace with your directory path
    filename = f"{game_id}.rofl"  # Adjust based on how you store files
    full_path = os.path.join(directory, filename)
    
    if os.path.exists(full_path):
        chunk_size = 1024 * 1024 # MiB

        def generate():
            with open(full_path, 'rb') as file:
                while True:
                    data = file.read(chunk_size)
                    if not data:
                        break
                    yield data

        return Response(generate(), 
                        mimetype='application/zip',
                        headers={'Content-Disposition': f'attachment; filename={filename}'})
    else:
        return f"Original replay file: {game_id}, doesn't exist", 404

def process_queue():
    global currently_scraping
    while True:
        if not scraping_queue.empty():
            # Get scrape request info
            scrape_request = scraping_queue.get()
            replay_path = scrape_request["game_id"] + ".rofl"
            end_time = scrape_request["end_time"]
            replay_speed = scrape_request["replay_speed"]
            game_id = os.path.basename(replay_path).replace(".rofl", "")

            # Set server state info
            currently_scraping = scrape_request

            # Initialise scraping settings
            scraper = ReplayScraper(
                game_dir=args.game_dir,
                replay_dir=args.replay_dir,
                dataset_dir=args.dataset_dir,
                scraper_dir=args.scraper_dir,
                region="",
                replay_speed=replay_speed)
            full_replay_path = os.path.join(args.replay_dir, replay_path)
            metadata, _ = scraper.get_metadata(full_replay_path, path=True)
            seconds = (metadata["gameLength"] // 1000) - 1

            end_time = seconds \
                       if end_time == -1 or seconds <= end_time \
                       else end_time

            # Perform scraping using T_T-Pandoras-Box and Lol client in replay mode
            scraper.scrape(
                replay_path=replay_path,
                end_time=end_time,
                delay=2,
                scraper=True)
            
            # Update `currently_scraping` state
            currently_scraping = "Not currently scraping!"

if __name__ == "__main__":
    thread = Thread(target=process_queue)
    thread.daemon = True
    thread.start()
    app.run(debug=True, host=args.host, port=args.port)