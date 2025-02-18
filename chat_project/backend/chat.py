from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Создаём базу данных и таблицу
def init_db():
    with sqlite3.connect("chat.db") as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS messages (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL,
                            message TEXT NOT NULL,
                            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

init_db()

# Получение сообщений
@app.route("/chat", methods=["GET"])
def get_messages():
    with sqlite3.connect("chat.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, message FROM messages ORDER BY time DESC LIMIT 10")
        messages = [{"username": row[0], "message": row[1]} for row in cursor.fetchall()]
    return jsonify(messages)

# Отправка сообщения
@app.route("/chat", methods=["POST"])
def send_message():
    data = request.json
    username = data.get("username", "Аноним")
    message = data.get("message", "").strip()
    
    if not message:
        return jsonify({"error": "Сообщение пустое"}), 400
    
    with sqlite3.connect("chat.db") as conn:
        conn.execute("INSERT INTO messages (username, message) VALUES (?, ?)", (username, message))
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
