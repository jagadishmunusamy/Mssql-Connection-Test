
from flask import Flask, jsonify, request
from decimal import Decimal
from mssql_login import connect_to_mssql, CONN_STR

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to HomePage",
                    "Connection_String" : CONN_STR})

# ---------- GET: list employees ----------
@app.route('/employees', methods=['GET'])
def get_employees():
    """GET The Employees Details"""
    conn = None
    try:
        conn = connect_to_mssql()
        cur = conn.cursor()
        cur.execute("SELECT * FROM employees")
        rows = cur.fetchall()
        columns = [col[0] for col in cur.description]

        result = []
        for row in rows:
            d = dict(zip(columns, row))
            # Convert Decimal -> float (or str)
            for k, v in d.items():
                if isinstance(v, Decimal):
                    d[k] = float(v)  # or: str(v)
            result.append(d)

        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if conn is not None:
            conn.close()

# ---------- POST: add employee ----------
@app.route('/employees', methods=['POST'])
def add_employee():
    """Adding New Employee"""
    conn = None
    try:
        data = request.get_json(silent=True) or {}
        name = data.get('name')
        department = data.get('department')
        salary = data.get('salary')

        # salary could be 0; check for None explicitly
        if not (name and department and salary is not None):
            return jsonify({"message": "missing required fields"}), 400

        conn = connect_to_mssql()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO employees (name, department, salary) VALUES (?, ?, ?)",
            (name, department, salary)
        )
        conn.commit()
        # Get the most recently added employee (by highest ID)
        cur.execute("SELECT TOP 1 * FROM employees ORDER BY id DESC")
        row = cur.fetchone()
        columns = [col[0] for col in cur.description]
        new_employee = dict(zip(columns, row))

        return jsonify({"message": f"Successfully added employee {new_employee}"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    print("Running on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
