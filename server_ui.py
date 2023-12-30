import tkinter as tk
import paramiko,re,time
from tkinter import font

def cancelLoadpath():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('139.162.28.194', username='root',password="Chino002")
    stdin, stdout, stderr = ssh.exec_command('pkill -9 -f loadpath.py')
    print(stdout.read())
    ssh.close()

def runLoadpath():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('139.162.28.194', username='root',password="Chino002")
    stdin, stdout, stderr = ssh.exec_command(f'screen -r loadpath -X stuff "\n"')
    stdin, stdout, stderr = ssh.exec_command(f'screen -r loadpath -X stuff "cd /update\n"')
    stdin, stdout, stderr = ssh.exec_command(f'screen -r loadpath -X stuff "python3 loadpath.py\n"')
    print(stdout.read())
    ssh.close()

def getPidFromScreen():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('139.162.28.194', username='root',password="Chino002")
    stdin, stdout, stderr = ssh.exec_command('screen -d')
    screen = str(stdout.read())
    screen = (re.findall('\d{4}\.pts',screen))
    screen= [i.split('.pts')[0] for i in screen]
    screen.sort()
    ssh.close()
    return screen

def startServer():

    # Create an SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the server
    ssh.connect('139.162.28.194', username='root',password="Chino002")

    # Open a new SSH session
    channel = ssh.invoke_shell()

    # Start a new session screen named "web"
    channel.send("screen -S web\n")

    # Wait for the command to complete
    while not channel.recv_ready():
        time.sleep(0.1)

    # Close the SSH session
    ssh.close()

    # Delay time for .5 sec
    time.sleep(.5)

    # Re connect to server and access to screen web for deploy website
    ssh.connect('139.162.28.194', username='root',password="Chino002")
    stdin, stdout, stderr = ssh.exec_command(f'screen -r web -X stuff "cd /var/app/\n"')
    stdin, stdout, stderr = ssh.exec_command(f'screen -r web -X stuff "python3 manage.py runserver 0.0.0.0:8000\n"')

    # Print result
    print(stdout.read())

    # Close the SSH session
    ssh.close()

    # Connect to the server
    ssh.connect('139.162.28.194', username='root',password="Chino002")

    # Open a new SSH session
    channel = ssh.invoke_shell()

    # Start a new session screen named "web"
    channel.send("screen -S loadpath\n")

    # Wait for the command to complete
    while not channel.recv_ready():
        time.sleep(0.1)

    # Close the SSH session
    ssh.close()

    # Delay .5 sec
    time.sleep(.5)

    # Run Loadpath function
    runLoadpath()

def shutDownserver():
    
    # Create an SSH client
    ssh = paramiko.SSHClient()
    
    # Allow server host to be known by local
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the server
    ssh.connect('139.162.28.194', username='root',password="Chino002")

    # Reboot server
    stdin, stdout, stderr = ssh.exec_command('sudo reboot')

    # Close the SSH session
    ssh.close()

def resetSQL():
        
    # Create an SSH client
    ssh = paramiko.SSHClient()
    
    # Allow server host to be known by local
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the server
    ssh.connect('139.162.28.194', username='root',password="Chino002")

    # Reboot server
    stdin, stdout, stderr = ssh.exec_command('sudo service mysql restart')

    # Close SSH session
    ssh.close()

def startWeb():
    
    # Create an SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the server
    ssh.connect('139.162.28.194', username='root',password="Chino002")

    stdin, stdout, stderr = ssh.exec_command(f'screen -r web -X stuff "cd /var/app/\n"')
    stdin, stdout, stderr = ssh.exec_command(f'screen -r web -X stuff "python3 manage.py runserver 0.0.0.0:8000\n"')

    # Print result
    print(stdout.read())

    # Close the SSH session
    ssh.close()

# startWeb()
# startServer()

def print_selection():
    if selected.get() == 'เปิดออโต้ดึงข้อมูล':
        runLoadpath()
    if selected.get() == 'เปิดเซิฟเวอร์':
        startServer()
    if selected.get() == 'ปิดเซิฟเวอร์':
        shutDownserver()
    if selected.get() == 'รีเซ็ทดาต้าเบส':
        resetSQL()
    if selected.get() == 'รีเว็บ':
        startWeb()
    label['text'] = 'Done !!'

# Create the root window with a specified height and width
HEIGHT = 300
WIDTH = 400
root = tk.Tk()
root.geometry(f"{WIDTH}x{HEIGHT}")
my_font = font.Font(family="Arial", size=16)

# Create a StringVar to store the selected value
selected = tk.StringVar()

# Create a selection box with options "a", "b", and "c"
# Set the height and width of the selection box
label = tk.Label(root, text="", fg='#FF0000',
font=my_font)

SELECTION_BOX_HEIGHT = 2
SELECTION_BOX_WIDTH = 14
selection_box = tk.OptionMenu(root, selected, "เปิดออโต้ดึงข้อมูล", "เปิดเซิฟเวอร์", "ปิดเซิฟเวอร์","รีเซ็ทดาต้าเบส","รีเว็บ")
selection_box.config(height=SELECTION_BOX_HEIGHT, width=SELECTION_BOX_WIDTH)
selection_box.configure(font=my_font)
# Create a submit button
# Set the height and width of the button

helv20 = font.Font(family='Arial', size=12)
menu = root.nametowidget(selection_box.menuname)  # Get menu widget.
menu.config(font=helv20)
BUTTON_HEIGHT = 2
BUTTON_WIDTH = 10
submit_button = tk.Button(root, text="Submit", command=print_selection)
submit_button.config(height=BUTTON_HEIGHT, width=BUTTON_WIDTH)
submit_button.configure(font=my_font)

# Place the selection box and submit button in the root window
selection_box.pack()
submit_button.pack()
label.pack()

# Start the event loop
root.mainloop()

# Function to be called when the submit button is clicked
