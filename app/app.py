from flask import Flask, jsonify, request
import pymysql
import os

app = Flask(__name__)


def get_db_connection():
    return pymysql.connect(
        host=os.environ.get('DB_HOST', 'db'),
        user=os.environ.get('DB_USER', 'flaskuser'),
        password=os.environ.get('DB_PASSWORD', ''),
        database=os.environ.get('DB_NAME', 'ticketdb'),
        cursorclass=pymysql.cursors.DictCursor
    )


@app.route('/health')
def health():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('SELECT 1')
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute('SELECT * FROM tickets ORDER BY created_at DESC')
            tickets = cursor.fetchall()
        conn.close()
        for ticket in tickets:
            if ticket.get('created_at'):
                ticket['created_at'] = str(ticket['created_at'])
        return jsonify(tickets)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    try:
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({'error': 'title is required'}), 400
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                'INSERT INTO tickets (title, description, status) VALUES (%s, %s, %s)',
                (data['title'], data.get('description', ''), data.get('status', 'open'))
            )
            conn.commit()
            ticket_id = cursor.lastrowid
        conn.close()
        return jsonify({'id': ticket_id, 'message': 'Ticket created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
