import os
import sys

link = sys.argv[1]
nombre_archivo = sys.argv[2]

id_index = link.index("=")

id = link[id_index+1:]

comando = "wget --no-check-certificate 'https://docs.google.com/uc?export=download&id={}' -O {}.py".format(id, nombre_archivo)

os.system(comando)

try:
    if(sys.argv[3] == "y"):
        os.system(f"python {nombre_archivo}.py")
except:
    pass