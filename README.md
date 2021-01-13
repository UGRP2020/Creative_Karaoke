# Creative_Karaoke

## Environment Setting
### 1. Install pipenv(python 3.8) and install modules
    $ sudo pip3 install pipenv
    $ cd Creative_Karaoke/
    $ pipenv shell
    $ pipenv install
### 2. Install magenta
Refer to https://github.com/magenta/magenta#manual-install-wo-anaconda

## Usage
    $ python main_program.py mode tempo genre filepath 
    

Mode: select tempo mode(0 = Fixed, 1 = Free).

Tempo: select tempo as bpm on fixed tempo mode.

Genre: select the genre of generated music(Jazz = 0, Disco = 1, Classical = 2, Rock = 3).

Filepath: path to the input wav file.
