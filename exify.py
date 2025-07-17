import shutil
import subprocess
import os
from pathlib import Path
from time import sleep

def exify(path):
    try:

        subprocess.run(['python','-m','PyInstaller',path+".py",'--onefile'],check=True)
        if os.path.exists(f"{path}.exe"):
            if os.path.exists('./Previous exe versions'):
                n = len(list(Path('./Previous exe versions').rglob('*.*')))
                os.rename(f"{path}.exe",f"./{path}{n}.exe")
                shutil.move(f"{path}{n}.exe",'./Previous exe versions')
            else:
                os.mkdir('Previous exe versions')    
                os.rename(f"{path}.exe",f"./{path}0.exe")
                shutil.move(f"{path}0.exe",'./Previous exe versions')
   

        shutil.move(f"./dist/{path}.exe",'./')
        shutil.rmtree('build')
        shutil.rmtree('dist')
        os.remove(f"{path}.spec")
    except Exception as e:
        print(f'An error occured: {e}')
        sleep(7.5)

if __name__ == '__main__':
    path = input('Enter the path of the file to exify( without .py): ').strip()
    exify(path) 
    