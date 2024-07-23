from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import requests
import socket
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for flashing messages

def check_website(url):
    try:
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        domain = url.split('//')[-1].split('/')[0]
        ip = socket.gethostbyname(domain)
        location_info = requests.get(f'http://ipinfo.io/{ip}/json').json()
        location = location_info.get('city', 'Unknown') + ', ' + location_info.get('region', 'Unknown') + ', ' + location_info.get('country', 'Unknown')

        start_time = datetime.datetime.now()
        response = requests.get(url, headers=headers, timeout=5)
        end_time = datetime.datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000
        first_byte = response.elapsed.total_seconds() * 1000
        last_byte = first_byte

        if 200 <= response.status_code <= 403:
            status = "Server is working!"
            status_color = "green"
        else:
            status = f"Server returned status code: {response.status_code}"
            status_color = "red"

        return {
            "status": status,
            "status_color": status_color,
            "ip": ip,
            "location": location,
            "response_time": response_time,
            "first_byte": first_byte,
            "last_byte": last_byte,
            "url": url
        }

    except requests.exceptions.RequestException as e:
        return {
            "status": "Server not found",
            "status_color": "red",
            "ip": "N/A",
            "location": "N/A",
            "response_time": "N/A",
            "first_byte": "N/A",
            "last_byte": "N/A",
            "url": url
        }

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        result = check_website(url)
        flash(result)
        return redirect(url_for('index'))
    return render_template('index.html')

@app.route('/log')
def log():
    # Here you can read from a file or database to display the log
    return render_template('log.html')

@app.route('/automation', methods=['GET', 'POST'])
def automation():
    if request.method == 'POST':
        urls = request.form['urls'].strip().split('\n')
        schedule_time = request.form['schedule_time']
        # Schedule the checks (implement your scheduling logic)
        flash('Checks scheduled successfully!', 'success')
        return redirect(url_for('automation'))
    return render_template('automation.html')

if __name__ == '__main__':
    app.run(debug=True)
