from os import makedirs, path, listdir, system
from werkzeug.utils import secure_filename
from sys import argv, exit
import shutil


def create_file(sfilepath: str, dfilepath: str, props: dict):
    """Lee archivo original, reemplaza las variables y crea archivo de salida"""
    with open(sfilepath, "r") as fl:
        data = fl.read()
        for prop, value in props.items():
            data = data.replace(prop, value)
    with open(dfilepath, "w") as fl:
        fl.write(data)


def create_virtual_env(name: str, rootProject: str, rootApi: str):
    """
    Crea entorno virtual e instala las dependencias
    """
    rootApi = rootApi.replace(rootProject + '/', './')  # quita la carpeta raiz
    system("""
        cd {1};
        python3 -m venv {0}-venv;
        source {0}-venv/bin/activate;
        pip install --upgrade pip;
        pip install -r {2}/requirements.txt;
    """.format(name, rootProject, rootApi))


CDIR = path.basename(path.dirname(path.realpath(__file__)))
if '-d' in argv:  # si debe eliminar la aplicacion
    napp = secure_filename(argv[2]).lower().replace('_api', '') + '-project'
    if input('are you sure you want to delete the %s (Y/N): ' % napp).lower() == 'y':
        shutil.rmtree(napp)
    exit()
elif len(argv) == 2:
    napp = argv[1]  # nombre de la aplicacion
    acode = input('app code: ')
    if napp:
        napp = secure_filename(napp).lower().replace('_api', '')
        rootProject = napp + '-project'  # carpeta de proyecto
        rootPath = path.join(rootProject, napp + '_api')  # carpeta del api
        # crea carpetas
        for dname in ('', 'modules', 'resources', '__temp__'):
            print("creating > " + dname)
            makedirs(path.join(rootPath, dname))
        DRESOURCES = path.join(CDIR, 'resources')
        for name in listdir(DRESOURCES):
            print("creating > " + name)
            npath = path.join(DRESOURCES, name)
            if path.isdir(npath):  # si es directorio lo copia todo
                shutil.copytree(npath, path.join(rootPath, name), dirs_exist_ok=True)
            else:  # si es un archivo
                if name == 'const.py':
                    create_file(npath, path.join(rootPath, name), {'<<APPLICATION_CODE>>': acode})
                elif name == 'app.py':
                    create_file(npath, path.join(rootPath, name), {'<<API_NAME>>': napp})
                elif name == 'runServer.py':
                    create_file(npath, path.join(rootPath, name), {'<<API_NAME>>': napp})
                else:
                    shutil.copyfile(npath, path.join(rootPath, name))
        create_virtual_env(napp, rootProject, rootPath)  # crea entorno e instala dependencias
        print("happy coding 😎")
else:
    print("you need to specify the api name")
    exit()
