from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# SQLite setup: create a database and table if they don't exist
def init_db():
    conn = sqlite3.connect('sensor_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temperature REAL,
            do_concentration REAL
        )
    ''')
    conn.commit()
    conn.close()

# POST endpoint to receive sensor data
@app.route('/collect-sensor-data/', methods=['POST'])
def collect_sensor_data():
    try:
        # Get the data from the request
        data = request.get_json()

        # Extract temperature and DO concentration
        temperature = data.get('temperature')
        do_concentration = data.get('do_concentration')

        # Save data to SQLite
        conn = sqlite3.connect('sensor_data.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO data (temperature, do_concentration) VALUES (?, ?)",
                       (temperature, do_concentration))
        conn.commit()
        conn.close()

        return jsonify({"status": "success", "message": "Data stored successfully!"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# GET endpoint to fetch and display data in HTML
@app.route('/')
def index():
    # Fetch data from SQLite
    conn = sqlite3.connect('sensor_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM data")
    rows = cursor.fetchall()
    conn.close()

    # HTML template for displaying the data in a table
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Sensor Data</title>
        <style>
            table {
                width: 60%;
                margin: 20px auto;
                border-collapse: collapse;
            }
            th, td {
                padding: 8px;
                text-align: center;
                border: 1px solid #ddd;
            }
            th {
                background-color: #f2f2f2;
            }
        </style>
    </head>
    <body>
        <h1 style="text-align:center;">Sensor Data</h1>
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Temperature (°C)</th>
                    <th>Dissolved Oxygen (mg/L)</th>
                </tr>
            </thead>
            <tbody>
                {% for row in data %}
                    <tr>
                        <td>{{ row[0] }}</td>
                        <td>{{ row[1] }}</td>
                        <td>{{ row[2] }}</td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    </body>
    </html>
    """

    # Render the HTML page with data
    return render_template_string(html_content, data=rows)

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True, host='0.0.0.0', port=8081)
