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

# Create the items table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
    ItemID TEXT PRIMARY KEY,
    ItemDescription TEXT NOT NULL
);
''')

# Create the pawn transactions table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pawn_transactions (
    PawnTransactionID TEXT PRIMARY KEY,
    CustomerID TEXT NOT NULL,
    ItemID TEXT NOT NULL,
    PawnDate DATE NOT NULL,
    LoanAmount REAL NOT NULL,
    InterestRate REAL NOT NULL,
    DueDate DATE NOT NULL,
    -- Add other relevant fields as needed
    FOREIGN KEY (CustomerID) REFERENCES customers (CustomerID),
    FOREIGN KEY (ItemID) REFERENCES items (ItemID)
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
app.secret_key = 'pluk'

def get_db_connection():
    conn = sqlite3.connect('gold_pawning.db')
    conn.row_factory = sqlite3.Row  # Access data by column name
    return conn

#Pawn Funtions

@app.route('/add_pawn_transaction', methods=['GET', 'POST'])
def add_pawn_transaction():
    conn = get_db_connection()
    customers = conn.execute('SELECT customer_id, first_name, last_name FROM customers').fetchall()
    items = conn.execute('SELECT ItemID, ItemDescription FROM items').fetchall()
    conn.close()

    if request.method == 'POST':
        pawn_transaction_id = request.form['pawn_transaction_id']
        customer_id = request.form['customer_id']
        item_id = request.form['item_id']
        pawn_date = request.form['pawn_date']
        loan_amount = request.form['loan_amount']
        interest_rate = request.form['interest_rate']
        due_date = request.form['due_date']

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO pawn_transactions (PawnTransactionID, CustomerID, ItemID, PawnDate, LoanAmount, InterestRate, DueDate) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (pawn_transaction_id, customer_id, item_id, pawn_date, loan_amount, interest_rate, due_date)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('pawn_transaction_list'))

    return render_template('add_pawn_transaction.html', customers=customers, items=items)

@app.route('/pawn_transactions')
def pawn_transaction_list():
    conn = get_db_connection()
    pawn_transactions = conn.execute('SELECT * FROM pawn_transactions').fetchall()
    conn.close()
    return render_template('pawn_transaction_list.html', pawn_transactions=pawn_transactions)


# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        employee = conn.execute(
            'SELECT * FROM employees WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()
        conn.close()

        if employee:
            session['logged_in'] = True
            session['employee_id'] = employee['employee_id']  # Use employee_id
            # You can also store other relevant data in the session
            return redirect(url_for('index'))  # Redirect to the main page
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('employee_id', None)
    return redirect(url_for('login'))

# Example of a protected route
@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
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