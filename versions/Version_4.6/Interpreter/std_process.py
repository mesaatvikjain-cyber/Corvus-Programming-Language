import subprocess
import os
import sys
import platform
import shlex

# Corvus System Controls, Environment & Hardened Process Engine (v4.6)

class ProcessEngine:
    @staticmethod
    def run(command, timeout=30):
        try:
            if isinstance(command, (list, tuple)):
                cmd_args = [str(c) for c in command]
                res = subprocess.run(cmd_args, shell=False, capture_output=True, text=True, timeout=timeout)
            else:
                cmd_str = str(command).strip()
                if sys.platform.startswith("win"):
                    # On Windows, preserve common shell built-ins cleanly while parsing args
                    res = subprocess.run(cmd_str, shell=False, capture_output=True, text=True, timeout=timeout)
                else:
                    cmd_args = shlex.split(cmd_str)
                    res = subprocess.run(cmd_args, shell=False, capture_output=True, text=True, timeout=timeout)

            return {
                "stdout": res.stdout,
                "stderr": res.stderr,
                "exit_code": res.returncode,
                "success": res.returncode == 0
            }
        except Exception as e:
            # Safe fallback if direct execution without shell needs shell invocation
            try:
                res = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
                return {
                    "stdout": res.stdout,
                    "stderr": res.stderr,
                    "exit_code": res.returncode,
                    "success": res.returncode == 0
                }
            except Exception as inner_e:
                return {
                    "stdout": "",
                    "stderr": str(inner_e),
                    "exit_code": 1,
                    "success": False
                }

    @staticmethod
    def get_env(var_name, default_val=""):
        return os.environ.get(str(var_name), str(default_val))

    @staticmethod
    def set_env(var_name, val):
        os.environ[str(var_name)] = str(val)
        return True

    @staticmethod
    def get_platform():
        return sys.platform

    @staticmethod
    def get_arch():
        return platform.machine()

    @staticmethod
    def get_os_release():
        return platform.release()

_global_process_engine = ProcessEngine()
