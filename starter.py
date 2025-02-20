from core.configuration.starter import StarterConfig
from core.logger import Logger
from core.utils.script import Script


CONFIG = StarterConfig('cranberrypy.ini')

LOGGER = Logger(config=CONFIG, name=__name__)
LOGGER.setup_logger()


DOCKERFILE_PATH = 'Dockerfile'


def create_dockerfile():
    installer_command = 'pip install'
    if CONFIG.package_installer == 'uv':
        installer_command = 'uv pip install --system'

    docker_file_content = f'''
    FROM python:{CONFIG.python_version}
    WORKDIR /app
    COPY . .
    RUN pip install --upgrade pip
    {'RUN pip install uv' if CONFIG.package_installer == 'uv' else ''}
    RUN {installer_command} -r requirements.txt
    RUN {installer_command} -r ./temp/requirements.txt {CONFIG.install_kwargs}
    CMD ["python", "main.py"]
    '''

    with open(DOCKERFILE_PATH, 'w') as file:
        file.write(docker_file_content)

    LOGGER.info("Dockerfile created")


def start():
    script = Script(logger=LOGGER)
    script.add(create_dockerfile)
    script.add(
        command=f"cp {CONFIG.requirements_path} ./temp/requirements.txt",
        description="copy project requirements.txt"
    )
    script.add(
        command="docker build -t temporary-image .",
        description="docker build image",
    )
    script.add(
        command=(
            "docker run --name temporary-container"
            f" --mount type=bind,src={CONFIG.root_directory_path},dst={CONFIG.root_image_path}"
            " --mount type=bind,src=./temp/,dst=/app/temp/ temporary-image"
        ),
        description="docker run container",
        exception_break=False
    )
    script.add(
        command="docker rm temporary-container",
        description="docker remove container",
        exception_break=False
    )
    script.add(
        command="docker rmi temporary-image",
        description="docker remove image",
        exception_break=False
    )
    script.add(
        command=f"rm {DOCKERFILE_PATH}",
        description="remove Dockerfile",
        exception_break=False
    )
    script.add(
        command="rm ./temp/requirements.txt",
        description="remove project requirements.txt",
        exception_break=False
    )
    script.run()


if __name__ == "__main__":
    start()
