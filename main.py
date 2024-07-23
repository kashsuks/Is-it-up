# Imports
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import socket
import datetime
import webbrowser
import threading
import time
from plyer import notification

def check_website(url):
    try:
        # Ensure the URL starts with http:// or https://
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        # Extract domain and get its IP address
        domain = url.split('//')[-1].split('/')[0]
        ip = socket.gethostbyname(domain)
        
        # Fetch location info based on IP address
        location_info = requests.get(f'http://ipinfo.io/{ip}/json').json()
        location = location_info.get('city', 'Unknown') + ', ' + location_info.get('region', 'Unknown') + ', ' + location_info.get('country', 'Unknown')

        # Measure response time and other network metrics
        start_time = datetime.datetime.now()
        response = requests.get(url, headers=headers, timeout=5)
        end_time = datetime.datetime.now()
        response_time = (end_time - start_time).total_seconds() * 1000
        first_byte = response.elapsed.total_seconds() * 1000
        last_byte = first_byte

        # Check response status code
        if 200 <= response.status_code <= 403:
            result_label.config(text="Server is working!", fg=color_success, font=('Helvetica', 36, 'bold'))
            log_website(url, "Successful", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), color_success)
            visit_button.pack(pady=10)  # Show visit button if server is working
        else:
            result_label.config(text=f"Server returned status code: {response.status_code}", fg=color_failure, font=('Helvetica', 36, 'bold'))
            log_website(url, "Fail", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), color_failure)
            visit_button.pack_forget()  # Hide visit button if server returned error

        # Update network info labels
        ip_label.config(text=f"IP Address: {ip}", font=('Helvetica', 24))
        location_label.config(text=f"Location: {location}", font=('Helvetica', 24))
        response_time_label.config(text=f"Response Time: {response_time:.2f} ms", font=('Helvetica', 24))
        first_byte_label.config(text=f"First Byte: {first_byte:.2f} ms", font=('Helvetica', 24))
        last_byte_label.config(text=f"Last Byte: {last_byte:.2f} ms", font=('Helvetica', 24))

        # Update the visit button URL
        visit_button.config(command=lambda: webbrowser.open(url))

    except requests.exceptions.RequestException as e:
        # Handle exceptions and set a simplified error message
        error_message = "Server not found"
        result_label.config(text=error_message, fg=color_failure, font=('Helvetica', 36, 'bold'))
        log_website(url, "Fail", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), color_failure)
        visit_button.pack_forget()  # Hide visit button if there's an error

        # Clear network info labels
        ip_label.config(text="IP Address: ", font=('Helvetica', 24))
        location_label.config(text="Location: ", font=('Helvetica', 24))
        response_time_label.config(text="Response Time: ", font=('Helvetica', 24))
        first_byte_label.config(text="First Byte: ", font=('Helvetica', 24))
        last_byte_label.config(text="Last Byte: ", font=('Helvetica', 24))

def log_website(url, status, time_checked, status_color):
    # Log website check results in the log tab
    website_log.config(state=tk.NORMAL)  # Allow editing
    log_text = f"{url:<60} {status:<15} {time_checked}\n"
    website_log.insert(tk.END, log_text)
    website_log.tag_add(status, f"{tk.END}-2l+60c", f"{tk.END}-2l+75c")
    website_log.tag_config(status, foreground=status_color)
    website_log.config(state=tk.DISABLED)  # Disable editing to prevent user modifications

def rgb_to_hex(r, g, b):
    return f'#{r:02x}{g:02x}{b:02x}'

def save_urls_to_file(urls):
    with open('urls.txt', 'w') as file:
        for url in urls:
            file.write(url + '\n')

def load_urls_from_file():
    try:
        with open('urls.txt', 'r') as file:
            return file.read().strip().split('\n')
    except FileNotFoundError:
        return []

def save_schedule_to_file(schedule_time):
    with open('schedule.txt', 'w') as file:
        file.write(schedule_time)

def load_schedule_from_file():
    try:
        with open('schedule.txt', 'r') as file:
            return file.read().strip()
    except FileNotFoundError:
        return ""

def send_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10
    )

def schedule_check():
    urls = url_entry_automation.get("1.0", tk.END).strip().split("\n")
    schedule_time = schedule_entry.get()

    def check_at_scheduled_time():
        while True:
            now = datetime.datetime.now()
            scheduled_hour, scheduled_minute = map(int, schedule_time.split(":"))
            if now.hour == scheduled_hour and now.minute == scheduled_minute:
                status_summary = ""
                for url in urls:
                    status = check_website_status(url)
                    status_summary += f"{url} - {status}\n"
                
                # Send notification
                send_notification("Website Status Check", status_summary)
                
                # Display the status summary in a new window
                status_window = tk.Toplevel(app)
                status_window.title("Status Summary")
                status_window.configure(bg=color_bg)
                status_label = tk.Label(status_window, text=status_summary, bg=color_bg, fg=color_fg, font=('Helvetica', 18))
                status_label.pack(pady=20)
                
                time.sleep(60)  # Wait for 1 minute to avoid multiple notifications

    threading.Thread(target=check_at_scheduled_time, daemon=True).start()
    messagebox.showinfo("Scheduled", f"Website checks scheduled at {schedule_time}")
    save_urls_to_file(urls)  # Save the URLs to file
    save_schedule_to_file(schedule_time)  # Save the schedule time to file

def check_website_status(url):
    try:
        response = requests.get(url)
        if 200 <= response.status_code < 400:
            return "Server is working"
        else:
            return f"Error {response.status_code}"
    except requests.RequestException:
        return "Server not found"

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
automation_frame = tk.Frame(notebook, bg=color_bg)

notebook.add(check_frame, text='Check Website')
notebook.add(log_frame, text='Checked Websites')
notebook.add(automation_frame, text='Automation')

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

# Result labels
result_label = tk.Label(check_frame, text="", bg=color_bg, fg=color_fg, font=('Helvetica', 36))
result_label.pack(pady=20)
ip_label = tk.Label(check_frame, text="IP Address: ", bg=color_bg, fg=color_fg, font=('Helvetica', 24))
ip_label.pack()
location_label = tk.Label(check_frame, text="Location: ", bg=color_bg, fg=color_fg, font=('Helvetica', 24))
location_label.pack()
response_time_label = tk.Label(check_frame, text="Response Time: ", bg=color_bg, fg=color_fg, font=('Helvetica', 24))
response_time_label.pack()
first_byte_label = tk.Label(check_frame, text="First Byte: ", bg=color_bg, fg=color_fg, font=('Helvetica', 24))
first_byte_label.pack()
last_byte_label = tk.Label(check_frame, text="Last Byte: ", bg=color_bg, fg=color_fg, font=('Helvetica', 24))
last_byte_label.pack()

# Website log
website_log = tk.Text(log_frame, height=30, state=tk.DISABLED, bg=color_bg, fg=color_fg, font=('Courier', 14))
website_log.pack(pady=20, padx=20)

# Automation tab
automation_label = tk.Label(automation_frame, text="Enter URLs (one per line):", bg=color_bg, fg=color_fg, font=('Helvetica', 24))
automation_label.pack(pady=10)

url_entry_automation = tk.Text(automation_frame, height=10, bg=color_entry_bg, fg=color_fg, insertbackground=color_fg, font=('Helvetica', 24))
url_entry_automation.pack(pady=10)

schedule_label = tk.Label(automation_frame, text="Schedule Time (HH:MM):", bg=color_bg, fg=color_fg, font=('Helvetica', 24))
schedule_label.pack(pady=10)

schedule_entry = tk.Entry(automation_frame, width=10, bg=color_entry_bg, fg=color_fg, insertbackground=color_fg, font=('Helvetica', 24))
schedule_entry.pack(pady=10)

# Display the last scheduled time when opening the automation tab
last_schedule_time = load_schedule_from_file()
if last_schedule_time:
    schedule_entry.insert(0, last_schedule_time)

schedule_button = tk.Button(automation_frame, text="Schedule Check", command=schedule_check, bg=color_button, fg=color_bg, font=('Helvetica', 24))
schedule_button.pack(pady=10)

# Load the URLs from the file when opening the automation tab
loaded_urls = load_urls_from_file()
if loaded_urls:
    url_entry_automation.insert(tk.END, "\n".join(loaded_urls))

# Run the application
app.mainloop()
