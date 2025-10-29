from flask import Flask, render_template, request, jsonify
import threading
import logging
import os
from twitter_automation import TwitterAutomation

app = Flask(__name__)
bot = None
bot_thread = None

# Create a log file if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_bot', methods=['POST'])
def start_bot():
    global bot, bot_thread

    if bot is not None and bot_thread.is_alive():
        return jsonify({"status": "error", "message": "Bot is already running"})

    bot = TwitterAutomation()
    bot_thread = threading.Thread(target=bot.run)
    bot_thread.daemon = True
    bot_thread.start()

    return jsonify({"status": "success", "message": "Bot started successfully"})

@app.route('/stop_bot', methods=['POST'])
def stop_bot():
    global bot, bot_thread

    if bot is None or not bot_thread.is_alive():
        return jsonify({"status": "error", "message": "Bot is not running"})

    # Set the stop flag in the bot
    bot.stop()

    return jsonify({"status": "success", "message": "Bot stopping..."})

@app.route('/bot_status', methods=['GET'])
def bot_status():
    global bot, bot_thread

    if bot is None or bot_thread is None:
        return jsonify({"status": "stopped"})

    if bot_thread.is_alive():
        return jsonify({"status": "running"})
    else:
        return jsonify({"status": "stopped"})

@app.route('/get_logs', methods=['GET'])
def get_logs():
    try:
        with open('logs/twitter_bot.log', 'r') as f:
            logs = f.read()
        return jsonify({"status": "success", "logs": logs})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
