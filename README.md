# GlyFix

https://glyfix.scicore.unibas.ch/


<img src="https://glyfix.scicore.unibas.ch/assets/icons/icon.png"  width="200" height="200">

GlyFix is a powerful tool designed to simplify and streamline the management of AI-generated annotations. 

It offers an intuitive interface that enables users to easily view, correct, and refine every aspect of the character annotation process.

# Online tool
You can reach the tool at the address
https://glyfix.scicore.unibas.ch/


# Local Machine
## Prepare your Machine
To prepare your machine, the only requirement is to install Python. You can easily download the installer from the official website: https://www.python.org/downloads/

## Download The Application
You can download the tool by clicking on the green `<> Code` button at the top right corner of this page and selecting the `Download ZIP` option.

Next, extract the ZIP archive to a location on your computer.

## Run the Application

### Windows
If you are using a Windows machine, you can run the application by executing the `run.bat` file.

### Other Operating Systems
For other operating systems, open a terminal in the folder containing all the files of the tool and run the following command:

1 . Prepare the environment:
```terminal
python .\src\create_file_docs.py
```
2 . Run the application:
```terminal
python3 -m http.server 5500
```

After running the command, open a browser and navigate to the following page:

```
http://localhost:5500
```

## Demo Video
You can find a video that explains how to run the software and how to use it at the following link:

 https://drive.google.com/file/d/1lGTcM2a7SqhyR420whAY-tVoYiSx4A4n/view?usp=sharing
