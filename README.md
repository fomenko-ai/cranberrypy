![](https://files.fikus.me/hell/cf885d395efa26fb23a68eae0032ca56b01f4d46.jpg)

A service for automating documentation of Python projects.

## Functionality
* Building dependency diagrams similar to UML
* Generating documentation text using AI
* Chatting with AI in the context of the entire project or a single module


## Components

**Python:**
* [ast](https://docs.python.org/3/library/ast.html) (code analysis)
* [pydeps](https://github.com/thebjorn/pydeps) (building a dependency graph) 
* [langchain](https://python.langchain.com/docs/introduction/) (generating project documentation)

**JavaScript:**
* [GoJS](https://gojs.net/latest/index.html) (visualizing project dependency diagrams)

**Docker** (running the main service module, which performs data preparation)

**LLM** (project documentation generation):
* MaziyarPanahi/Mistral-7B-Instruct-v0.3-GGUF 
* gemini-1.5-pro 


## Main files, modules and directories

* `cranberrypy.ini` - configuration file.

* `main.py` - analyzes a project code and prepares data for visualization of diagrams and working with AI.

* `core/diagrams/app/viewer.js` - building dependency diagrams.

* `index.html` - launching `viewer.js` and displaying diagrams

* `chat.py` - chat with AI, works in two modes: 
    * chat with the context of the entire project or a separate module 
    * generating documentation for the selected module

* `core/assistant/ai.py` - preparing LLM, context of project data and dynamic formation of a query for generating documentation based on the code of the selected module.

* `starter.py` - creating a Dockerfile, preparing a container for Cranberrypy and the project under study, installing project dependencies, launching `main.py`.

* `temp` - directory for temporary files.

* `temp/saved` - saved data about projects 

* `temp/source/source_key` - source key, the file contains the name of the last project for which `main.py` was launched.

* `examples` - typical examples of module dependencies, used to check the visualization of diagrams and unit tests

## Working with the service

### Filling out the configuration file

In the `cranberrypy.ini` file, you need to fill in the fields:

* `project_path` - absolute path to the project

* `excluded_paths` - paths or directories of the project that need to be excluded during analysis 

* `python_version` - project version

* `requirements_path` - absolute path to the project file (if the path is different from project_path) 

* `install_kwargs` - additional arguments for the command `pip install -r ...` when installing project dependencies (if needed)

* `root_directory_path` - any shared directory for the Cranberrypy service and your project

**Example:**

```ini
[main]
project_path = /home/aleksei/path_to/my_project/
excluded_paths =
    venv
    venv39
    .git
    /home/aleksei/path_to/my_project/venv
    /home/aleksei/path_to/my_project/venv39
    /home/aleksei/path_to/my_project/.git

[starter]
python_version = 3.9
requirements_path = /home/aleksei/path_to/my_project/requirements.txt
install_kwargs = --trusted-host example.host --extra-index-url  http://example.host/lib/python
root_directory_path = /home/aleksei/path_to/
root_image_path = /app/temp/projects/
```


### Code analysis and data preparation

Use the `main.py` module. There are two ways to run the module - automatically and manually.

#### Automatically 

With the automatic option, you need to check if Docker is working.

If Docker is installed and working, run the `starter.py` script. The script will create a Dockerfile, prepare a container, install dependencies, and run `main.py`. 

The finished data is saved in the `temp/saved` directory.

The name of the project, as the last data source for main.py, will be written to `source_key`.

#### Manually 

The manual method is recommended if you need to run main.py multiple times.

1. Create a virtual environment.
2. Install Cranberrypy dependencies in the `requirements.txt` file. 
3. Install project dependencies.
4. Run `main.py`.

The finished data is saved in the `temp/saved` directory.

The name of the project, as the last data source for `main.py`, will be written to `source_key`.


### Visualizing dependency diagrams

Cranberrypy uses the GoJS framework.

To view the project dependency diagrams, open the `index.html` file in a browser.

#### Examples of dependency visualization

Inheritance

![Inheritance](https://files.fikus.me/hell/5ef7591936b386826b1d7bc06f4d48ff395e4113.png)

Composition

![Composition](https://files.fikus.me/hell/efc09d770b5991db2ae8399af640b5e2a55e6b67.png)

Call

![Call](https://files.fikus.me/hell/b18791ef6afd4cafe29760bf5fe5a50bdca9d808.png)

Usage

![Usage](https://files.fikus.me/hell/95c18b16e712904bffa61ffe660ae1e367779757.png)

The code of the examples is located in the directory `examples`.

By right-clicking in an empty field, you can select the required project folder.

By right-clicking on a module, you can display the module's dependencies or view classes.

By right-clicking on a class, you can display the class's dependencies.

***To reduce response time and be able to work with the service in the absence of the Internet, [you can download the go.js file](https://gojs.net/latest/download.html). Specify the path to the file in `index.html`.***

You can quickly check the correctness of the visualization of dependencies by running Cranberrypy on the directory `examples`.

### Generating documentation text

1. In a virtual environment, install the Cranberrypy dependencies in the `ai_requirements.txt` file. 

2. If you plan to use Gemini, [generate an API key](https://aistudio.google.com/app/apikey) and fill in the `google_api_key` field in the `cranberrypy.ini` file

   If you plan to use Mistral, you do not need to fill in the `google_api_key` field.

3. Run `chat.py`.

   The first time you run it, the AI data will be prepared, which may take about 5 minutes. When you run it again, the already prepared data will be used.

4. After starting the chat, you need to enter the absolute path of the module. 

   Copy the file *(Ctrl + Shift + C)*, and paste the path into the terminal.


Documentation is generated according to a given template:
* brief description of the module
* description of classes, methods
* description of module dependencies

If necessary, in `chat.py` you can change the `SYSTEM_PROMPT` or switch flags in the `generate_documentation` method.

### Chatting with AI

1. To activate the query sending function, uncomment line 26 in the `chat.py` module. 

2. Enter a query.

3. Optional, but if you need to get a more accurate answer for a specific module or several modules of the project, copy and send the absolute path of the module.

***The chat only responds to the query and does not save the history of previous queries in context.***

### Chat with persistent context

The feature allows you to enter queries in AI with a constant set of context data.

1. To activate the persistent context, uncomment line 27 in the `chat.py` module. 

2. Specify the module paths in the `chat_with_persistent_context` method.

3. Enter a query.

***The chat only responds to the query and does not save the history of previous queries in context.***

### Current context

If you have made changes to your project code and want to quickly generate documentation or get a response from AI, use methods with current context:
* `chat_with_current_context`
* `generate_documentation_with_current_context`

***As the current context it uses only the module code.***

### Switching between projects

To change the data source in the `temp/source/source_key` file, specify the name of the project you need.

You can view the list of available projects in `temp/saved`. 

## Authors

* Aleksander Gulin 
* Aleksander Melnikov 
* Aleksei Fomenko

## Contacts

Send questions, comments and suggestions to [fal@exante.eu](mailto:fal@exante.eu)

![](https://files.fikus.me/hell/525814da3b75f41107aac5e7f15fadd5267a6132.jpg)
