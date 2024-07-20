#Imports
import tkinter as tk
from tkinter import ttk
import requests
import socket
import datetime
import webbrowser

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

        #Networking Data
        start_time = datetime.datetime.now()
        response = requests.get(url, headers=headers, timeout=5)
        end_time = datetime.datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000
        first_byte = response.elapsed.total_seconds() * 1000
        last_byte = first_byte

        #Status Code
        if 200 <= response.status_code < 404:
            result_label.config(text="Server is working!", fg=color_success, font=('Helvetica', 36, 'bold'))
            log_website(url, "Successful", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), color_success)
        else:
            result_label.config(text=f"Server returned status code: {response.status_code}", fg=color_failure, font=('Helvetica', 36, 'bold'))
            log_website(url, "Fail", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), color_failure)

        #Data in GUI
        ip_label.config(text=f"IP Address: {ip}", font=('Helvetica', 24))
        location_label.config(text=f"Location: {location}", font=('Helvetica', 24))
        response_time_label.config(text=f"Response Time: {response_time:.2f} ms", font=('Helvetica', 24))
        first_byte_label.config(text=f"First Byte: {first_byte:.2f} ms", font=('Helvetica', 24))
        last_byte_label.config(text=f"Last Byte: {last_byte:.2f} ms", font=('Helvetica', 24))

        # Update the visit button URL
        visit_button.config(command=lambda: webbrowser.open(url))

    except requests.exceptions.RequestException as e:
        result_label.config(text="Server is not working! " + str(e), fg=color_failure, font=('Helvetica', 36, 'bold'))
        log_website(url, "Fail", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), color_failure)

def log_website(url, status, time_checked, status_color):
    #Log website data in new tab
    log_text = f"{url:<60} {status:<15} {time_checked}\n"
    website_log.insert(tk.END, log_text)
    website_log.tag_add(status, f"{tk.END}-2l+60c", f"{tk.END}-2l+75c")
    website_log.tag_config(status, foreground=status_color)

def rgb_to_hex(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

# Colour Palette
color_bg = rgb_to_hex(34, 40, 49)
color_fg = rgb_to_hex(238, 238, 238)
color_button = rgb_to_hex(255, 211, 105)
color_entry_bg = rgb_to_hex(57, 62, 70)
color_success = 'green'
color_failure = 'red'

# Create main application window
app = tk.Tk()
app.title("Website Availability Checker")
app.configure(bg=color_bg)

# Fullscreen mode
app.attributes('-fullscreen', True)

# Create a Notebook for tabs
notebook = ttk.Notebook(app)

# Create frames for each tab
check_frame = tk.Frame(notebook, bg=color_bg)
log_frame = tk.Frame(notebook, bg=color_bg)

notebook.add(check_frame, text='Check Website')
notebook.add(log_frame, text='Checked Websites')

notebook.pack(expand=1, fill='both')

# Input frame in check tab
input_frame = tk.Frame(check_frame, bg=color_bg)
input_frame.pack(pady=20)

# URL entry
url_label = tk.Label(input_frame, text="Enter Website URL:", bg=color_bg, fg=color_fg, font=('Helvetica', 24))
url_label.grid(row=0, column=0, padx=5)
url_entry = tk.Entry(input_frame, width=60, bg=color_entry_bg, fg=color_fg, insertbackground=color_fg, font=('Helvetica', 24))
url_entry.grid(row=0, column=1, padx=5)

# Check button
check_button = tk.Button(input_frame, text="Search", command=lambda: check_website(url_entry.get()), bg=color_button, fg=color_bg, font=('Helvetica', 24))
check_button.grid(row=0, column=2, padx=5)

# Visit button
visit_button = tk.Button(check_frame, text="Visit Website", command=lambda: webbrowser.open(url_entry.get()), bg=color_button, fg=color_bg, font=('Helvetica', 24))
visit_button.pack(pady=10)

# Result label
result_label = tk.Label(check_frame, text="", bg=color_bg, fg=color_fg, font=('Helvetica', 36, 'bold'))
result_label.pack(pady=20)

# Network Info Labels
network_info_frame = tk.Frame(check_frame, bg=color_bg)
network_info_frame.pack(pady=20)

ip_label = tk.Label(network_info_frame, text="IP Address: ", bg=color_bg, fg=color_fg, font=('Helvetica', 24))
ip_label.pack(anchor='w')
location_label = tk.Label(network_info_frame, text="Location: ", bg=color_bg, fg=color_fg, font=('Helvetica', 24))
location_label.pack(anchor='w')
response_time_label = tk.Label(network_info_frame, text="Response Time: ", bg=color_bg, fg=color_fg, font=('Helvetica', 24))
response_time_label.pack(anchor='w')
first_byte_label = tk.Label(network_info_frame, text="First Byte: ", bg=color_bg, fg=color_fg, font=('Helvetica', 24))
first_byte_label.pack(anchor='w')
last_byte_label = tk.Label(network_info_frame, text="Last Byte: ", bg=color_bg, fg=color_fg, font=('Helvetica', 24))
last_byte_label.pack(anchor='w')

# Log text widget in log tab
website_log = tk.Text(log_frame, bg=color_entry_bg, fg=color_fg, font=('Helvetica', 18), wrap='none')
website_log.pack(expand=1, fill='both', padx=10, pady=10)

# Add a scrollbar to the log text widget
scrollbar = tk.Scrollbar(log_frame, command=website_log.yview)
website_log.config(yscrollcommand=scrollbar.set)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Exit button to close fullscreen mode and quit
exit_button = tk.Button(app, text="Exit Fullscreen", command=lambda: app.attributes('-fullscreen', False), bg=color_button, fg=color_bg, font=('Helvetica', 24))
exit_button.pack(pady=10)

# Run the application
app.mainloop()
