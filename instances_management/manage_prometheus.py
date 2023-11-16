"""
TODO: Add docstring
"""
import subprocess
from colors import colors


def is_tmux_session_exist(instance_public_ip, private_key_path):
    is_session_exist = False
    cmd = f'ssh -o StrictHostKeyChecking=no -i {private_key_path}  ubuntu@{instance_public_ip} '
    cmd += '\'tmux ls -F "#S"\''
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if p.returncode == 0:
        session_names = p.stdout.strip().split('\n')
        for session_name in session_names:
            if session_name == 'prometheus':
                is_session_exist = True
                break
        if is_session_exist:
            print(f'{colors.BOLD}{colors.YELLOW}WARNING: {colors.RESET}{colors.YELLOW}' +
                  f'prometheus tmux session is already running.{colors.RESET}')
            return is_session_exist
    else:
        print(f"{colors.BOLD}{colors.RED}Error:{colors.RESET} {colors.RED}{p.stderr}" +
              f"{colors.RESET}")
        return None


def start_prometheus(instance_public_ip, private_key_path):
    kill_prometheus(instance_public_ip, private_key_path)
    print('Starting prometheus ...')
    cmd = f"ssh -o StrictHostKeyChecking=no -i {private_key_path}  ubuntu@{instance_public_ip} "
    cmd += '"tmux new -d -s prometheus'
    cmd += ' && tmux send-keys -t prometheus:0 '
    cmd += "'cd /home/ubuntu/prometheus && "
    cmd += "./prometheus --config.file=prometheus.yml' C-m\""
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if p.returncode == 0:
        print(f'\t{colors.BOLD}{colors.GREEN}:: prometheus successfully started!' +
              f'{colors.RESET}')
    else:
        print(f"{colors.BOLD}{colors.RED}Error:{colors.RESET} {colors.RED}{p.stderr}" +
              f"{colors.RESET}")


def kill_prometheus(instance_public_ip, private_key_path):
    print('Killing prometheus ...')
    cmd = f"ssh -o StrictHostKeyChecking=no -i {private_key_path}  ubuntu@{instance_public_ip} "
    cmd += '"kill \$(sudo lsof -t -i:9090)"'
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if p.returncode == 0:
        print(f'\t{colors.BOLD}{colors.CYAN}:: prometheus process (port 9090) successfully ' +
              f'killed!{colors.RESET}')
    else:
        print(f"{colors.BOLD}{colors.RED}Error:{colors.RESET} {colors.RED}{p.stderr}" +
              f"{colors.RESET}")

    is_session_exist = is_tmux_session_exist(instance_public_ip, private_key_path)
    if is_session_exist:
        cmd = f"ssh -i {private_key_path}  ubuntu@{instance_public_ip} "
        cmd += '"tmux kill-session -t prometheus"'
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if p.returncode == 0:
            print(f'\t{colors.BOLD}{colors.CYAN}:: prometheus tmux session killed successfully.' +
                  f'{colors.RESET}')
        else:
            print(f"{colors.BOLD}{colors.RED}Error:{colors.RESET} {colors.RED}{p.stderr}" +
                  f"{colors.RESET}")


if __name__ == "__main__":
    instance_public_ip = "18.224.25.0"
    private_key_path = "PATH_TO_AWS_KEY"

    kill_prometheus(instance_public_ip, private_key_path)
