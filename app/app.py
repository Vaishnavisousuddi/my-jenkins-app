# app/app.py
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>Hello from Jenkins + EKS!</h1>
    <p>Deployed automatically by Jenkins Pipeline</p>
    <p>Version: 1.0</p>
    '''

@app.route('/health')
def health():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
