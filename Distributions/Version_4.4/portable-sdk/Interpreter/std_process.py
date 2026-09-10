import subprocess
import os
import sys
import platform

# Corvus System Controls, Environment & Process Spawner Engine (v4.2)

class ProcessEngine:
    @staticmethod
    def run(command):
        try:
            res = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return {
                "stdout": res.stdout,
                "stderr": res.stderr,
                "exit_code": res.returncode,
                "success": res.returncode == 0
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
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
