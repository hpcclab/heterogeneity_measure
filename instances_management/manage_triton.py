"""
TODO: Add docstring
"""
import subprocess
from colors import colors


def get_container_id(instance_public_ip, private_key_path, name="tritonserver"):
    cmd = f'ssh -o StrictHostKeyChecking=no -i {private_key_path}  ubuntu@{instance_public_ip} '
    cmd += f'docker ps -aqf "name=^{name}$"'
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if p.returncode == 0:
        container_id = p.stdout.strip()
        if container_id:
            return container_id
        else:
            print(f"{colors.BOLD}{colors.YELLOW}WARNING:{colors.RESET} {name}{colors.RESET} " +
                  f"{colors.BOLD}{colors.YELLOW}container is not running!{colors.RESET}")
            return None
    else:
        print(f"{colors.BOLD}{colors.RED}Error:{colors.RESET} {colors.RED}{p.stderr}" +
              f"{colors.RESET}")
        return None


def is_tmux_session_exist(instance_public_ip, private_key_path):
    cmd = f'ssh -o StrictHostKeyChecking=no -i {private_key_path}  ubuntu@{instance_public_ip} '
    cmd += '\'tmux ls -F "#S"\''
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if p.returncode == 0:
        session_names = p.stdout.strip().split('\n')
        for session_name in session_names:
            if session_name == 'tritonserver':
                is_session_exist = True
                break
        if is_session_exist:
            print(f'{colors.BOLD}{colors.YELLOW}WARNING: {colors.RESET}{colors.YELLOW}' +
                  f'tritonserver tmux session is already running.{colors.RESET}')
            return is_session_exist
    else:
        print(f"{colors.BOLD}{colors.RED}Error:{colors.RESET} {colors.RED}{p.stderr}" +
              f"{colors.RESET}")
        return None


def send_model_repository(instance_public_ip, private_key_path):
    cmd = "scp -r -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "
    cmd += f"-i {private_key_path} "
    cmd += "../triton "
    cmd += f"ubuntu@{instance_public_ip}:/home/ubuntu/"

    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if p.returncode == 0:
        print(f'{colors.BOLD}{colors.GREEN}{instance_public_ip}: ' +
              f'Model repository sent successfully.{colors.RESET}')
    else:
        print(f"{colors.BOLD}{colors.RED}Error:{colors.RESET} {colors.RED}{p.stderr}" +
              f"{colors.RESET}")
        return None


def send_prometheus_source(instance_public_ip, private_key_path):
    cmd = "scp -r -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "
    cmd += f"-i {private_key_path} "
    cmd += "../prometheus "
    cmd += f"ubuntu@{instance_public_ip}:/home/ubuntu/"

    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if p.returncode == 0:
        print(f'{colors.BOLD}{colors.GREEN}{instance_public_ip}: ' +
              f'Prometheus directory sent successfully.{colors.RESET}')
    else:
        print(f"{colors.BOLD}{colors.RED}Error:{colors.RESET} {colors.RED}{p.stderr}" +
              f"{colors.RESET}")
        return None


def start_tritonserver(instance_public_ip, private_key_path, gpus=0,
                       path_to_models="/home/ubuntu/triton/model_repository"):

    container_id = get_container_id(instance_public_ip, private_key_path)
    if container_id is not None:
        kill_tritonserver(instance_public_ip, private_key_path)
    print(f'{colors.BOLD}Starting tritonserver container ...{colors.RESET}')
    cmd = f"ssh -o StrictHostKeyChecking=no -i {private_key_path}  ubuntu@{instance_public_ip} "
    cmd += '"tmux new -d -s tritonserver'
    cmd += ' && tmux send-keys -t tritonserver:0 '
    cmd += "'docker run --name tritonserver --shm-size=256m "
    if gpus:
        # cmd += '--gpus=all --min-supported-compute-capability=5.2 '
        cmd += '--gpus=all '
    cmd += '--rm -p8000:8000 -p8001:8001 -p8002:8002 -v '
    cmd += f'{path_to_models}:/models nvcr.io/nvidia/tritonserver:23.04-py3 '
    cmd += "tritonserver --model-repository=/models' "
    cmd += 'C-m"'
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if p.returncode == 0:
        print(f'\t{colors.BOLD}{colors.GREEN}:: Tritonserver container successfully started!' +
              f'{colors.RESET}')
    else:
        print(f"{colors.BOLD}{colors.RED}Error:{colors.RESET} {colors.RED}{p.stderr}" +
              f"{colors.RESET}")


def kill_tritonserver(instance_public_ip, private_key_path):

    print(f'Terminating previously running Tritonserver container ...{colors.RESET}')
    cmd = f"ssh -o StrictHostKeyChecking=no -i {private_key_path}  ubuntu@{instance_public_ip} "
    cmd += "'docker rm -f tritonserver'"
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if p.returncode == 0:
        print(f'\t{colors.BOLD}{colors.CYAN}' +
              f':: Triton container [{colors.RESET}{colors.MAGENTA}tritonserver{colors.RESET}' +
              f'{colors.BOLD}{colors.CYAN}] killed successfully.{colors.RESET}')
    else:
        print(f"{colors.BOLD}{colors.RED}Error:{colors.RESET} {colors.RED}{p.stderr}" +
              f"{colors.RESET}")

    is_session_exist = is_tmux_session_exist(instance_public_ip, private_key_path)
    if is_session_exist:
        print(f'Killing Tritonserver tmux session ...{colors.RESET}')
        cmd = f"ssh -o StrictHostKeyChecking=no -i {private_key_path}  ubuntu@{instance_public_ip} "
        cmd += '"tmux kill-session -t tritonserver"'
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if p.returncode == 0:
            print(f'\t{colors.BOLD}{colors.CYAN}:: Tritonserver tmux session killed ' +
                  f'successfully.{colors.RESET}')
        else:
            print(f"{colors.BOLD}{colors.RED}Error:{colors.RESET} {colors.RED}{p.stderr}" +
                  f"{colors.RESET}")


if __name__ == "__main__":
    instance_public_ip = "3.15.137.80"
    private_key_path = "PATH_TO_AWS_KEY"
    start_tritonserver(instance_public_ip, private_key_path, gpus=0)
