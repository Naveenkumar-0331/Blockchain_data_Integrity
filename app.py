from flask import Flask, render_template,jsonify, request, redirect, url_for
from blockchain import Blockchain, hash_student_record
import json

app = Flask(__name__)
edu_chain = Blockchain()
edu_chain.load_chain()

def load_blockchain():
    with open("blockchain_data.json","r") as f:
        return json.load(f)
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_record():
    name = request.form['name']
    roll = request.form['roll']
    gpa = request.form['gpa']
    record_hash = hash_student_record(name, roll, gpa)
    edu_chain.add_block(record_hash)
    edu_chain.save_chain()
    return redirect(url_for('view_chain'))

@app.route('/view')
def view_chain():
    return render_template('view.html', chain=edu_chain.chain)

@app.route('/verify', methods=['GET', 'POST'])
def verify_record():
    if request.method == 'POST':
        name = request.form['name']
        roll = request.form['roll']
        gpa = request.form['gpa']
        verified = edu_chain.verify_student_record(name, roll, gpa)
        return render_template('verify.html', verified=verified)
    return render_template('verify.html', verified=None)

@app.route('/visualize')
def visualize_blockchain():
    chain = load_blockchain()

    # Verify integrity of each block (except Genesis)
    for i in range(len(chain)):
        if i == 0:
            chain[i]['valid'] = True  # Genesis block always valid
        else:
            # Compare previous block's stored hash with current block's prev_hash
            prev_hash_stored = chain[i - 1].get('hash')
            current_prev_hash = chain[i].get('prev_hash')

            if current_prev_hash == prev_hash_stored:
                chain[i]['valid'] = True
            else:
                chain[i]['valid'] = False

    return render_template('visualize.html', chain=chain)



if __name__ == '__main__':
    app.run(debug=True)
