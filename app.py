import sqlite3

# Connect to the database (creates a new database if it doesn't exist)
conn = sqlite3.connect('gold_pawning.db') 
cursor = conn.cursor()

# Create a table for customers (if it doesn't exist)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone TEXT,
    address TEXT NOT NULL,
    id_card TEXT NOT NULL,
    id_card_photo TEXT NOT NULL
);
''')

# Create the employees table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    phone TEXT,
    position TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);
''')

# Commit the changes
conn.commit()

# Fetch all customers
cursor.execute("SELECT * FROM customers")
customers = cursor.fetchall()
print(customers)

# Close the connection
conn.close()

from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('gold_pawning.db')
    conn.row_factory = sqlite3.Row  # Access data by column name
    return conn

@app.route('/')
def home():
    return render_template('index.html')

# Customer section
# ... (other code) ...

# Customer management routes
@app.route('/customers')
def customer_list():
    conn = get_db_connection()
    customers = conn.execute('SELECT * FROM customers').fetchall()
    conn.close()
    return render_template('customer_list.html', customers=customers)

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        first_name = request.form['first_name']  # New field
        last_name = request.form['last_name']  # New field
        phone = request.form['phone']  # New field
        address = request.form['address']  # New field
        id_card = request.form['id_card']  # New field
        id_card_photo = request.form['id_card_photo']  # New field

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO customers ( first_name, last_name, phone, address, id_card, id_card_photo) VALUES ( ?, ?, ?, ?, ?, ?)',
            ( first_name, last_name, phone, address, id_card, id_card_photo)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('customer_list'))

    return render_template('add_customer.html')

@app.route('/customers/<string:customer_id>/edit', methods=['GET', 'POST'])  # Changed to string
def edit_customer(customer_id):
    conn = get_db_connection()

    if request.method == 'POST':
        first_name = request.form['first_name']  # New field
        last_name = request.form['last_name']  # New field
        phone = request.form['phone']  # New field
        address = request.form['address']  # New field
        id_card = request.form['id_card']  # New field
        id_card_photo = request.form['id_card_photo']  # New field

        conn.execute(
            'UPDATE customers SET  first_name = ?, last_name = ?, phone = ?, address = ?, id_card = ?, id_card_photo = ? WHERE customer_id = ?',
            ( first_name, last_name, phone, address, id_card, id_card_photo, customer_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('customer_list'))

    customer = conn.execute('SELECT * FROM customers WHERE customer_id = ?', (customer_id,)).fetchone()
    conn.close()
    return render_template('edit_customer.html', customer=customer)

@app.route('/customers/<string:customer_id>/delete', methods=['POST'])  # Changed to string
def delete_customer(customer_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM customers WHERE customer_id = ?', (customer_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('customer_list'))

# ... (other code) ...

# Employee management routes
# ... (other code) ...

# Employee management routes
@app.route('/employees')
def employee_list():
    conn = get_db_connection()
    employees = conn.execute('SELECT * FROM employees').fetchall()
    conn.close()
    return render_template('employee_list.html', employees=employees)

@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        first_name = request.form['first_name']  # New field
        last_name = request.form['last_name']  # New field
        phone = request.form['phone']  # New field
        position = request.form['position']  # New field
        username = request.form['username']
        password = request.form['password']  # In a real app, hash the password!

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO employees (first_name, last_name, phone, position, username, password) VALUES ( ?, ?, ?, ?, ?, ?)',
            ( first_name, last_name, phone, position, username, password)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('employee_list'))

    return render_template('add_employee.html')

@app.route('/employees/<string:employee_id>/edit', methods=['GET', 'POST'])  # Changed to string
def edit_employee(employee_id):
    conn = get_db_connection()

    if request.method == 'POST':
        
        first_name = request.form['first_name']  # New field
        last_name = request.form['last_name']  # New field
        phone = request.form['phone']  # New field
        position = request.form['position']  # New field
        username = request.form['username']
        password = request.form['password']  # In a real app, hash the password!

        conn.execute(
            'UPDATE employees SET  first_name = ?, last_name = ?, phone = ?, position = ?, username = ?, password = ? WHERE employee_id = ?',
            (first_name, last_name, phone, position, username, password, employee_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('employee_list'))

    employee = conn.execute('SELECT * FROM employees WHERE employee_id = ?', (employee_id,)).fetchone()
    conn.close()
    return render_template('edit_employee.html', employee=employee)

@app.route('/employees/<string:employee_id>/delete', methods=['POST'])  # Changed to string
def delete_employee(employee_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM employees WHERE employee_id = ?', (employee_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('employee_list'))


# Similar routes for items, transactions, and employees
if __name__ == '__main__':
    app.run(debug=True)