from flask import Flask, request, send_from_directory, render_template
from modules.getfiles import get_dir_files_data
import os

app = Flask(__name__, static_url_path='', template_folder='./')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    if os.path.exists('./static/%s' % path):
        return send_from_directory('./static/', path)
    print('File not found: /static/%s' % path)
    return ''

@app.route('/app.py')
def send_app():
    return send_from_directory('./', 'app.py')

@app.route('/files')
@app.route('/files/')
def send_files_data():
    return get_dir_files_data()

@app.route('/files/<path:path>')
def send_files_data_with_path(path):
    print(path)
    r = get_dir_files_data(path)
    print(r)
    return r

if __name__ == '__main__':
    app.run(port=80, threaded=True)
