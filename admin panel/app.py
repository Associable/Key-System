from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import datetime
import secrets

app = Flask(__name__)

# Configure the MongoDB URI and secret key
app.config["MONGO_URI"] = ""
app.secret_key = secrets.token_hex(16)

# Initialize PyMongo
mongo = PyMongo(app)

# Ensure the 'yes' collection is accessed properly
db = mongo.cx["no"]
collection = db["yes"]

@app.route('/')
def index():
    keys = collection.find()
    return render_template('index.html', keys=keys)

@app.route('/add', methods=['POST'])
def add_key():
    key = request.form.get('key')
    user = request.form.get('user')
    duration = int(request.form.get('duration'))
    hwid = request.form.get('hwid', '')

    key_document = {
        'key': key,
        'user': user,
        'duration': duration,
        'hwid': hwid,
        'redeemed': False,
        'active': True,
        'generated_time': datetime.datetime.utcnow()
    }
    collection.insert_one(key_document)
    return redirect(url_for('index'))

@app.route('/delete/<key_id>', methods=['POST'])
def delete_key(key_id):
    collection.delete_one({'_id': ObjectId(key_id)})
    return redirect(url_for('index'))

@app.route('/edit/<key_id>', methods=['GET', 'POST'])
def edit_key(key_id):
    if request.method == 'POST':
        key = request.form.get('key')
        user = request.form.get('user')
        duration = int(request.form.get('duration'))
        hwid = request.form.get('hwid', '')

        collection.update_one(
            {'_id': ObjectId(key_id)},
            {"$set": {
                'key': key,
                'user': user,
                'duration': duration,
                'hwid': hwid
            }}
        )
        return redirect(url_for('index'))
    else:
        key_document = collection.find_one({'_id': ObjectId(key_id)})
        return render_template('edit.html', key=key_document)

if __name__ == '__main__':
    app.run(debug=True)
