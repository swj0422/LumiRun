#!/usr/bin/env python3
"""
逐光成长系统 - 核心部署逻辑
提供跨平台的部署功能抽象
"""
import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Callable


class DeployLogger:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.step_count = 0

    def step(self, message: str):
        self.step_count += 1
        print(f"[STEP {self.step_count}] {message}")

    def info(self, message: str):
        print(f"[INFO] {message}")

    def success(self, message: str):
        print(f"[OK] {message}")

    def warn(self, message: str):
        print(f"[WARN] {message}")

    def error(self, message: str):
        print(f"[ERROR] {message}", file=sys.stderr)


class DeployConfig:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir).resolve()
        self.venv_dir = self.project_dir / ".venv"
        self.backend_dir = self.project_dir / "backend"
        self.frontend_dir = self.project_dir / "frontend"
        self.pypi_mirror = "https://mirrors.aliyun.com/pypi/simple/"
        self.npm_mirror = "https://registry.npmmirror.com/"
        self.min_python_version = (3, 10)
        self.min_node_version = (18, 0, 0)

    def get_env_file_path(self, service: str) -> Path:
        if service == "backend":
            return self.backend_dir / ".env"
        elif service == "frontend":
            return self.frontend_dir / ".env.local"
        else:
            raise ValueError(f"Unknown service: {service}")

    def get_python_exe(self) -> Path:
        if os.name == 'nt':
            return self.venv_dir / "Scripts" / "python.exe"
        return self.venv_dir / "bin" / "python"


class CommandExecutor:
    def __init__(self, logger: DeployLogger, config: DeployConfig):
        self.logger = logger
        self.config = config

    def run_command(
        self,
        command: List[str],
        cwd: Optional[Path] = None,
        env: Optional[Dict[str, str]] = None,
        check: bool = True,
        retry_with_mirror: bool = False,
        mirror_command: Optional[Callable[[], List[str]]] = None
    ) -> bool:
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                check=check
            )
            if result.stdout:
                print(result.stdout.strip())
            return True
        except subprocess.CalledProcessError as e:
            if retry_with_mirror and mirror_command:
                self.logger.warn("Command failed, trying with mirror...")
                mirror_cmd = mirror_command()
                return self.run_command(
                    mirror_cmd,
                    cwd=cwd,
                    env=env,
                    check=check,
                    retry_with_mirror=False
                )
            else:
                self.logger.error(f"Command failed: {' '.join(str(c) for c in command)}")
                if e.stderr:
                    print(e.stderr.strip(), file=sys.stderr)
                return False

    def install_python_deps(self) -> bool:
        self.logger.info("Installing Python dependencies...")
        python_exe = str(sys.executable)
        requirements_file = self.config.backend_dir / "requirements.txt"

        def make_mirror_command():
            return [
                python_exe, "-m", "pip", "install",
                "-r", str(requirements_file),
                "-i", self.config.pypi_mirror,
                "--trusted-host", "mirrors.aliyun.com"
            ]

        return self.run_command(
            [python_exe, "-m", "pip", "install", "-r", str(requirements_file)],
            retry_with_mirror=True,
            mirror_command=make_mirror_command
        )

    def install_node_deps(self) -> bool:
        self.logger.info("Installing Node.js dependencies...")

        def make_mirror_command():
            return ["npm", "config", "set", "registry", self.config.npm_mirror]

        self.run_command(make_mirror_command(), check=False)
        return self.run_command(
            ["npm", "install", "--loglevel=error"],
            cwd=self.config.frontend_dir
        )

    def build_frontend(self) -> bool:
        self.logger.info("Building frontend project...")
        return self.run_command(
            ["npm", "run", "build", "--loglevel=error"],
            cwd=self.config.frontend_dir,
            check=False
        )


class EnvironmentChecker:
    def __init__(self, logger: DeployLogger, config: DeployConfig):
        self.logger = logger
        self.config = config

    def check_python(self) -> bool:
        self.logger.info("Checking Python installation...")
        try:
            result = subprocess.run(
                [sys.executable, "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            version_str = result.stdout.strip().split()[-1]
            self.logger.success(f"Python {version_str} installed")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.error(
                f"Python {self.config.min_python_version[0]}.{self.config.min_python_version[1]}+ not found! "
                f"Please install Python first."
            )
            return False

    def check_node(self) -> bool:
        self.logger.info("Checking Node.js installation...")
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
            version_str = result.stdout.strip().replace('v', '')
            self.logger.success(f"Node.js v{version_str} installed")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.error(
                f"Node.js {self.config.min_node_version[0]}+ not found! "
                f"Please install Node.js first."
            )
            return False


class Deployer:
    def __init__(self, project_dir: str, verbose: bool = False):
        self.logger = DeployLogger(verbose)
        self.config = DeployConfig(project_dir)
        self.executor = CommandExecutor(self.logger, self.config)
        self.checker = EnvironmentChecker(self.logger, self.config)

    def create_directories(self) -> bool:
        self.logger.step("Creating directory structure...")
        directories = [
            self.config.project_dir / "logs",
            self.config.backend_dir / "uploads"
        ]
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                self.logger.success(f"Created {directory.relative_to(self.config.project_dir)}")
            except OSError as e:
                self.logger.error(f"Failed to create {directory}: {e}")
                return False
        return True

    def create_virtualenv(self) -> bool:
        if not self.config.venv_dir.exists():
            self.logger.info("Creating Python virtual environment...")
            if not self.executor.run_command(
                [sys.executable, "-m", "venv", str(self.config.venv_dir)]
            ):
                return False
        else:
            self.logger.success("Virtual environment already exists")
        return True

    def setup_backend_env(self) -> bool:
        self.logger.step("Configuring backend environment...")
        if not self.create_virtualenv():
            return False
        return self.executor.install_python_deps()

    def setup_frontend_env(self) -> bool:
        self.logger.step("Configuring frontend environment...")
        if not self.executor.install_node_deps():
            return False
        return self.executor.build_frontend()

    def setup_env_files(self) -> bool:
        self.logger.step("Configuring environment variables...")
        env_files = [
            ("backend", ".env.example", ".env"),
            ("frontend", ".env.example", ".env.local")
        ]
        for service, example_file, env_file in env_files:
            service_dir = self.config.backend_dir if service == "backend" else self.config.frontend_dir
            example_path = service_dir / example_file
            env_path = service_dir / env_file
            if not env_path.exists():
                try:
                    shutil.copy(example_path, env_path)
                    self.logger.success(f"Created {env_file} for {service}")
                except OSError as e:
                    self.logger.error(f"Failed to create {env_file}: {e}")
                    return False
            else:
                self.logger.success(f"{env_file} already exists for {service}")
        return True

    def init_database(self) -> bool:
        self.logger.step("Initializing database...")
        self.logger.info("Creating database tables...")
        python_exe = self.config.get_python_exe()
        if not self.executor.run_command(
            [str(python_exe), str(self.config.backend_dir / "init_db.py")],
            cwd=self.config.backend_dir
        ):
            return False
        self.logger.info("Initializing roles, users and permissions...")
        return self.executor.run_command(
            [str(python_exe), str(self.config.backend_dir / "init_data.py")],
            cwd=self.config.backend_dir
        )

    def deploy(self) -> bool:
        print("=" * 60)
        print("  LumiRun System - Core Deployment")
        print("=" * 60)
        print()
        self.logger.step("Checking system environment...")
        if not self.checker.check_python():
            return False
        if not self.checker.check_node():
            return False
        if not self.create_directories():
            return False
        if not self.setup_backend_env():
            return False
        if not self.setup_frontend_env():
            return False
        if not self.setup_env_files():
            return False
        if not self.init_database():
            return False
        print()
        print("=" * 60)
        print("  DEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print()
        print("Default Accounts:")
        print("admin@example.com / admin / Password123")
        print("manager@example.com / manager / Password123")
        print("member@example.com / member / Password123")
        print()
        print("Security: Please change default passwords after first login!")
        print()
        return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="LumiRun System Deployment")
    parser.add_argument(
        "--project-dir",
        default=str(Path(__file__).parent),
        help="Project directory path"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    args = parser.parse_args()
    deployer = Deployer(args.project_dir, args.verbose)
    success = deployer.deploy()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()