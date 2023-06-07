# mathmusic

Synth creator 

use the keys to play notes like a piano

make sure to install requirements using pip

# Setup

## Pip Installation Requirements

1. Make sure you have python3 and pip installed
2. navigate to the directory where you cloned the repo

```bash
 cd /path/to/mathmusic 
 ```
3. install virtualenv. This will allow you to create a virtual environment for the project. A virutal enviroment is a way to keep the dependencies for a project separate from the rest of your system. This is useful because it allows you to have different versions of the same package for different projects. 

```bash
pip install virtualenv
```

4. Create a virtual environment for the project. This will create a folder called venv in the mathmusic directory. 

```bash
virtualenv venv
```

5. Activate the virtual environment. This will allow you to install packages for the project without affecting the rest of your system. 

```bash
source venv/bin/activate
```

6. Install the requirements for the project. This will install all the packages needed to run the project. 

```bash
pip install -r requirements.txt
```

### **Note**: You should activate the virtual environment every time you want to run the project but you only need to install the requirements once. After you have installed the requirements, you can activate the virtual environment by running the following command:

```bash
source venv/bin/activate
```


### **Note**: To deactivate the virtual environment, run the following command:

```bash
deactivate
```

Alternatively you can run the setup script to do all the above after navigating to the project directory using the command:

```bash
source setup.sh
```
