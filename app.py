from flask import Flask, render_template, request, redirect, flash, url_for
from bson import ObjectId
import pymongo
from pymongo import MongoClient
import pandas as pd

app = Flask(__name__)
app.secret_key = 'jsdhgjsgdf/jshdg@sajdhf#shdajma'

connection_string = 'mongodb://localhost:27017/employee_data'
client = MongoClient(connection_string)
db = client.get_database("employee_data")
collection = db.get_collection("employee")

@app.route('/')
def index():
    # Fetch all data from employee database
    all_employee = list(db.employee.find())
    check_empty = len(list(all_employee))
    return render_template('index.html',all_employee=all_employee,check_empty=check_empty)


@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        # Read the Excel file
        employee_data = pd.read_excel(file)
        # Convert the data to JSON format
        data_json = pd.DataFrame.to_dict(employee_data, orient='records')
        # Create a unique index on the 'email' field
        db.employee.create_index([('Email', pymongo.ASCENDING)], unique=True)
        for document in data_json:
            if "First_Name" in document and "Last_Name" in document and "Email" in document and "Phone" in document:
                try:
                    db.employee.insert_one(document)
                except pymongo.errors.DuplicateKeyError:
                    pass
            else:
                flash('Invalid File Structure', 'info')
                return redirect(url_for('index'))
        return redirect(url_for('index'))


@app.route('/delete_employee/<employeeId>', methods=['POST'])
def delete_employee(employeeId):
    # Delete the document with the specified email
    collection.delete_one({'_id': ObjectId(employeeId)})
    return redirect(url_for('index'))


@app.route('/update_employee/<employeeId>', methods=['POST'])
def update_employee(employeeId):
    # Get data from the request
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    # Update employee data
    db.employee.update_one(
        {'_id': ObjectId(employeeId)},
        {'$set': {'First_Name': first_name, 'Last_Name': last_name, 'Email': email, 'Phone': phone}}
    )
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
