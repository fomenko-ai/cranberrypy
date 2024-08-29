import subprocess

from core.configuration.config import Config
from core.logger import Logger

CONFIG = Config('cranberrypy.ini')

LOGGER = Logger(config=CONFIG, name=__name__)
LOGGER.setup_logger()


DOCKERFILE_PATH = 'Dockerfile'


def create_docker_files():
    docker_file_content = f'''
    FROM python:{CONFIG.python_version}
    WORKDIR /app
    COPY . .
    RUN pip install --upgrade pip
    RUN pip install -r requirements.txt
    RUN pip install -r ./temp/requirements.txt {CONFIG.install_kwargs}
    CMD ["python", "main.py"]
    '''

    with open(DOCKERFILE_PATH, 'w') as file:
        file.write(docker_file_content)

    LOGGER.info("Dockerfile created")


def start():
    copy_requirements_command = f"cp {CONFIG.requirements_path} ./temp/requirements.txt"
    build_command = f"docker build -t temporary-image ."
    run_command = (
        "docker run --name temporary-container"
        f" --mount type=bind,src={CONFIG.root_directory_path},dst={CONFIG.root_image_path}"
        " --mount type=bind,src=./temp/,dst=/app/temp/ temporary-image"
    )
    delete_container_command = "docker rm temporary-container"
    delete_image_command = "docker rmi temporary-image"
    delete_dockerfile_command = f"rm {DOCKERFILE_PATH}"
    delete_requirements_command = "rm ./temp/requirements.txt"

    try:
        LOGGER.info("Copy project requirements file...")
        subprocess.run(copy_requirements_command, shell=True, check=True)
        LOGGER.info("Requirements file copied successfully")
    except Exception as e:
        LOGGER.error("Failed to copy requirements file", e)

    try:
        LOGGER.info("Building docker image...")
        subprocess.run(build_command, shell=True, check=True)
        LOGGER.info("Image build successful")
    except Exception as e:
        LOGGER.error("Failed to build image", e)
        return

    try:
        LOGGER.info("Running docker image...")
        subprocess.run(run_command, shell=True, check=True)
        LOGGER.info("Image ran successfully")
    except Exception as e:
        LOGGER.error("Failed to run image", e)

    try:
        LOGGER.info("Deleting docker container...")
        subprocess.run(delete_container_command, shell=True, check=True)
        LOGGER.info("Container deleted successfully")
    except Exception as e:
        LOGGER.error("Failed to delete container", e)

    try:
        LOGGER.info("Deleting docker image...")
        subprocess.run(delete_image_command, shell=True, check=True)
        LOGGER.info("Image deleted successfully")
    except Exception as e:
        LOGGER.error("Failed to delete image", e)

    try:
        LOGGER.info("Deleting Dockerfile...")
        subprocess.run(delete_dockerfile_command, shell=True, check=True)
        LOGGER.info("Dockerfile deleted successfully")
    except Exception as e:
        LOGGER.error("Failed to delete dockerfile", e)

    try:
        LOGGER.info("Deleting project requirements file...")
        subprocess.run(delete_requirements_command, shell=True, check=True)
        LOGGER.info("Requirements file deleted successfully")
    except Exception as e:
        LOGGER.error("Failed to delete requirements file", e)


if __name__ == "__main__":
    create_docker_files()
    start()
