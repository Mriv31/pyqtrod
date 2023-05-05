# PyQtRod

Software for visualization and analysis of rod data


## Clone the GIT directory

Create an account on Gitlab physics just by connecting once to [Gitlab Physics](https://gitlab.physics.ox.ac.uk/) with your Physics credential.

Install [Git for windows](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

Clone the repository from the command line.

```
cd where_you_want_to_put_the_software
git clone https://gitlab.physics.ox.ac.uk/rieu/PyQtRod.git
```

You will be asked to enter your physics credential. If there are any access problem, ask me and I will add permission for you to clone.

## Update the GIT directory

To update any modification I will have made to the software, just enter from the command line :

```
cd where_you_want_to_put_the_software/PyQtRod
git pull
```

## Install Python

To run the software you will need a Python environment. Check what is available on physics self service or install Python 3.10 for windows. (https://docs.python.org/3/using/windows.html).

You can either install directly from Microsoft Store or the full installer on the [Python foundation](https://www.python.org/downloads/).

I recommend not to use the Anaconda environment](https://docs.anaconda.com/anaconda/install/windows/), since most recent modules will be harder to install.

## Install Python modules

Note : if in this part, in Windows, you get an error saying that windows can not find pip or python you need to add the Python path in your environment variables.

First upgrade the Python module manager pip :
```
pip install --upgrade pip
```

Several Python modules are needed to run the software. To do so open a command line console and enter :

```
cd where_you_want_to_put_the_software/PyQtRod
pip install -r requirements.txt
```

## Run PyQtRod

```
cd where_you_want_to_put_the_software/PyQtRod
python3 PyQtRod.py
```

## Load TDMS files

Click File "Load TDMS file"

## Summarize a folder speed and anisotropies

Click File "Summarize folder"

## Install Jupyter Notebook or Jupyter Lab for interactive data treatment
Execute from command-line :
```
pip install notebook
```
or, for Jupyter Lab,

```
pip install jupyterlab
```

## Launching jupyter notebook:
```
python -m notebook
```

or, for jupyterlab
```
python -m jupyterlab
```

You can find an example of jupyter notebook with treatment of Rod data in Examples.

## Troubleshoot

###Linux

OpenGL might not work perfectly (black screen on all openGL modules, 3D trajectories and AnisGL module).
It seems to be due to an incompatibility between PyOpenGL and Mesa (Intel drivers). It can be worked around if you have a nvidia card.
Either you only have a nvidia card and you shall not have that problem. If you have dual graphic cards, put the prime mode as "on demand" in NVIDIA settings, it will allow keep using the Intel card for common usage but ask for NVIDIA rendering for some applications.
```
sudo prime-query on-demand
```
Then execute the python application with env variable set to __GLX_VENDOR_LIBRARY_NAME=nvidia __NV_PRIME_RENDER_OFFLOAD=1.
```
__GLX_VENDOR_LIBRARY_NAME=nvidia __NV_PRIME_RENDER_OFFLOAD=1 python3 PyQtRod.py
```
If this does not work, you can also enforce the usage of nvidia graphic card all the time, but this will pump electricity.
```
sudo prime-query nvidia
```

## Authors and acknowledgment
TODO
## License
TODO
## Project status
If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
## For Martin 
