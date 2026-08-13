import sqlite3
from flask import Flask, jsonify, render_template_string, request

app = Flask(__name__)
DB_FILE = 'output/network_events.db'

def query_db(query, args=(), one=False):
    """Safely queries the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

# --- API Route: Get all risks or filter by device/risk level ---
@app.route('/api/risks', methods=['GET'])
def get_risks():
    device = request.args.get('device')
    risk_level = request.args.get('risk_level')
    
    query = "SELECT * FROM risk_summary WHERE 1=1"
    params = []
    
    if device:
        query += " AND Device LIKE ?"
        params.append(f"%{device}%")
    if risk_level:
        query += " AND Risk_Level = ?"
        params.append(risk_level)
        
    rows = query_db(query, params)
    return jsonify([dict(ix) for ix in rows])

# --- UI Route: Simple Live Dashboard ---
@app.route('/')
def dashboard():
    rows = query_db("SELECT * FROM risk_summary ORDER BY Risk_Level DESC")
    
    # HTML template embedded as a string for easy, single-file assessment run
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Vodafone Network Governance Dashboard</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
    </head>
    <body class="bg-light container py-5">
        <div class="d-flex align-items-center mb-4">
            <h1 class="h2 text-danger fw-bold">🔴 Vodafone Network Governance Portal</h1>
        </div>
        <div class="card shadow-sm">
            <div class="card-header bg-danger text-white fw-bold">Active Device Operational Risks</div>
            <div class="card-body">
                <table class="table table-striped align-middle">
                    <thead>
                        <tr>
                            <th>Device</th>
                            <th>Event Category</th>
                            <th>Description</th>
                            <th>Risk Level</th>
                            <th>First Detected</th>
                            <th>Remediation Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for row in rows %}
                        <tr>
                            <td><strong>{{ row['Device'] }}</strong></td>
                            <td>{{ row['Event'] }}</td>
                            <td>{{ row['Event_Detail'] }}</td>
                            <td>
                                <span class="badge {% if row['Risk_Level'] == 'Critical' %}bg-danger{% elif row['Risk_Level'] == 'High' %}bg-warning text-dark{% else %}bg-info{% endif %}">
                                    {{ row['Risk_Level'] }}
                                </span>
                            </td>
                            <td>{{ row['First_Seen'] }}</td>
                            <td><small class="text-muted">{{ row['Recommendation'] }}</small></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_template, rows=rows)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
