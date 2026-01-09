import time,paramiko,re

def cancelLoadpath():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('139.144.119.186', username='root',password="Koonchino002")
    stdin, stdout, stderr = ssh.exec_command('pkill -9 -f loadpath.py')
    print(stdout.read())
    ssh.close()

def runLoadpath():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('139.144.119.186', username='root',password="Koonchino002")
    stdin, stdout, stderr = ssh.exec_command(f'screen -r loadpath -X stuff "\n"')
    stdin, stdout, stderr = ssh.exec_command(f'screen -r loadpath -X stuff "cd /update\n"')
    stdin, stdout, stderr = ssh.exec_command(f'screen -r loadpath -X stuff "python3 loadpath.py\n"')
    print(stdout.read())
    ssh.close()

def getPidFromScreen():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('139.144.119.186', username='root',password="Koonchino002")
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
    ssh.connect('139.144.119.186', username='root',password="Koonchino002")

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
    ssh.connect('139.144.119.186', username='root',password="Koonchino002")
    stdin, stdout, stderr = ssh.exec_command(f'screen -r web -X stuff "cd /var/app/\n"')
    stdin, stdout, stderr = ssh.exec_command(f'screen -r web -X stuff "python3 manage.py runserver 0.0.0.0:8000\n"')

    # Print result
    print(stdout.read())

    # Close the SSH session
    ssh.close()

    # Connect to the server
    ssh.connect('139.144.119.186', username='root',password="Koonchino002")

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
    ssh.connect('139.144.119.186', username='root',password="Koonchino002")

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
    ssh.connect('139.144.119.186', username='root',password="Koonchino002")

    # Reboot server
    stdin, stdout, stderr = ssh.exec_command('sudo service mysql restart')

    # Close SSH session
    ssh.close()

def resetWeb():
        
    # Create an SSH client
    ssh = paramiko.SSHClient()
    
    # Allow server host to be known by local
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the server
    ssh.connect('139.144.119.186', username='root',password="Koonchino002")

    # Reboot server
    stdin, stdout, stderr = ssh.exec_command('sudo service apache2 restart')

    # Close SSH session
    ssh.close()

def startWeb():
    
    # Create an SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the server
    ssh.connect('139.144.119.186', username='root',password="Koonchino002")

    stdin, stdout, stderr = ssh.exec_command(f'screen -r web -X stuff "cd /var/app/\n"')
    stdin, stdout, stderr = ssh.exec_command(f'screen -r web -X stuff "python3 manage.py runserver 0.0.0.0:8000\n"')

    # Print result
    print(stdout.read())

    # Close the SSH session
    ssh.close()

def installParamiko():
    pyautogui.press('win')
    time.sleep(.5)
    pyautogui.typewrite('cmd')
    time.sleep(.5)
    pyautogui.press('enter')
    time.sleep(.5)
    pyautogui.typewrite('pip install paramiko')
    time.sleep(.5)
    pyautogui.press('enter')
    time.sleep(10)
    pyautogui.hotkey('alt','f4')

# cancelLoadpath()
#
# installParamiko()