import os
os.system("sudo pigpiod")

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pigpio as GPIO
import spidev
import csv
import time
import brailfun

# Use a service account
cred = credentials.Certificate(r'/home/pi/rillo-web-firebase-adminsdk-n5611-e48238a56c.json')
firebase_admin.initialize_app(cred)


db = firestore.client()
braille_cell = brailfun.NewCell(power=5, time_on=3, time_off=1, signal_type=1)
pigpio_controller = braille_cell.pi
braille_cell.init()
spi = spidev.SpiDev()
spi.open(0,0) 

print("inicializando")

# Variables
nivel_bateria = 0
t_sleep = 20               # 5 minutos de inactividad para entrar al modo sleep
t_shutdown = 10           # 30 minutos en modo sleep para apagarse
t_activated = time.time()
t_lectura_bateria = 60      # Se mide el nivel de batería cada 60 segundos
canal_input_bateria = 0     # canal del MCP3008 en el cual ingresa la señal del nivel de bateria, 0 por defecto
modo_actual = "analogico"   # Modo en el que se encuentra rillo (puede ser digital, analogico o sleep)
stop_parpadeo_led = False   # Esta variable nos indica si los leds deben dejar de parpadear (solo parpadean cuando rillo tiene la batería baja)

#Leer variables de vibración del csv
with open('variables_rillo.csv') as csvDataFile:
        csvReader = csv.reader(csvDataFile)
        for row in csvReader:
            if row[0] == 'intensidad':
                braille_cell.power = float(row[1])
            elif row[0] == 'tiempo_on':
                braille_cell.time_on = float(row[1])
            elif row[0] == 'tiempo_off':
                braille_cell.time_off = float(row[1])
            elif row[0] == 'signnal':
                braille_cell.signal_type = int(row[1])


#Pines
pin_indicador_encendido = 25        #pin 22
pin_boton_activacion = 6            #pin 31
pin_boton_bateria = 5               #pin 29
pin_led_rgb_g = 16                  #pin 36
pin_led_rgb_b = 13                  #pin 33
pin_leds_camara = 12                #pin 37

pigpio_controller.set_mode(pin_indicador_encendido, GPIO.OUTPUT)
pigpio_controller.set_mode(pin_boton_activacion, GPIO.INPUT)
pigpio_controller.set_mode(pin_boton_bateria, GPIO.INPUT)
pigpio_controller.set_mode(pin_led_rgb_g, GPIO.OUTPUT)
pigpio_controller.set_mode(pin_led_rgb_b, GPIO.OUTPUT)
pigpio_controller.set_mode(pin_leds_camara, GPIO.OUTPUT)   

pigpio_controller.set_glitch_filter(pin_boton_activacion, 500)
pigpio_controller.set_glitch_filter(pin_boton_bateria, 500)

pigpio_controller.write(pin_indicador_encendido, 1)
pigpio_controller.write(pin_led_rgb_g, 1)
pigpio_controller.write(pin_led_rgb_b, 1)
pigpio_controller.write(pin_leds_camara, 1)


#Excepcion
class apagadox(Exception): pass

# funciones
def saludo():
    print("saludo")
    
    r_braille = [1, 2, 3, 5]
    current_braille_parameters = braille_cell.parameters()
    braille_cell.parameters(4, 0.5, 0.5, 1)
    for punto in r_braille:
        celda_braille = [0, 0, 0, 0, 0, 0]
        celda_braille[punto] = 1
        braille_cell.trigger(celda_braille)
    braille_cell.parameters(current_braille_parameters["power"], current_braille_parameters["time_on"], current_braille_parameters["time_off"], current_braille_parameters["signal_type"])

def apagado_automatico():
    print("rillo out")
    braille_cell.close()
    spi.close()
    os.system('sudo killall pigpiod')
    ############################################################ os.system('sudo shutdown -h now')

def potencia_leds_camara(potencia):
    """ Esta funcion sirve para cambiar la potencia de la salida pwm de los leds de la camara
        potencia_pwn, es un entero que recibe un valor entre 0 y 255 """

    global pin_leds_camara

    pigpio_controller.write(pin_leds_camara, potencia)

def parpadeo_leds():
    """Esta función está hecha para ser llamada por un thread de forma tal que el led de activacion parpadee cuando la batería tenga un nivel de carga bajo"""

    global modo_actual, stop_parpadeo_led

    cambio_luz = True

    while True:
        if modo_actual == "analogico":
            led_activacion("verde")

        elif modo_actual == "digital":
            led_activacion("azul")

        elif modo_actual == "sleep":
            cambio_luz = not(cambio_luz)

            if cambio_luz:
                led_activacion("verde")
            else:
                led_activacion("azul")

        else:
            print("error modo_actual esta mal definido en la funcion parpadeo_leds, se esperan los valores analogico o digital")
        
        if modo_actual == "sleep":
            time.sleep(1)
            led_activacion("off")
            time.sleep(2)
        else:
            time.sleep(0.5)
            led_activacion("off")
            time.sleep(0.5)

        if stop_parpadeo_led:
            if modo_actual == "analogico":
                led_activacion("verde")

            elif modo_actual == "digital":
                led_activacion("azul")

            elif modo_actual == "sleep":
                led_activacion("off")
             
            else:
                print("error modo_actual esta mal definido en la funcion parpadeo_leds, se esperan los valores analogico o digital")
            break

def medir_bateria():
    """ Esta función mide el nivel de voltaje de la bateria, si este esta por debajo del nivel indicado hace parpadear el led de indicacion"""
    print("funcion medir bateria")
    
    global nivel_bateria, canal_input_bateria, stop_parpadeo_led

    spi.max_speed_hz = 1350000
    adc = spi.xfer2([1,(8+canal_input_bateria)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]

    nivel_bateria = data*5.0/1023
    
    try:
        doc_ref = db.collection(u'rillo-main').document(u'nivel-bateria')
        doc_ref.update({
            u'bateria': nivel_bateria
        })
    except:
        print("error, no puede acceder a la base de datos al enviar el nivel de la bateria")

    if nivel_bateria >= 3.4:

        stop_parpadeo_led = True
    
    elif nivel_bateria < 3.4:

        stop_parpadeo_led = False

    elif nivel_bateria <= 3.2:

        raise apagadox

    else:
        print("error, led bateria, nivel medido no identificado")

    return nivel_bateria
   
def modo_activo(gpio, level, tick):
    print("modo activacion")

    global t_activated, modo_actual, interrupcion_activo, stop_parpadeo_led

    stop_parpadeo_led = True

    t_activated = time.time()    
    modo_actual = "analogico"
    interrupcion_activo.cancel()
    del(interrupcion_activo)     

def modo_analogico():
    #En este modo Rillo recibe y procesa datos desde la camara
    print("modo analogico")

    #encender camara %?
    print("camara encendida")

    try:
        doc_ref = db.collection(u'rillo-main').document(u'funciones')
        doc_ref.update({
            u'conectado': False
        })
    except:
        print("error, imposible acceder a la base de datos al tratar de escribir el nivel de bateria estando en el modo digital")

    global t_sleep, t_lectura_bateria, modo_actual

    modo_actual = "analogico"

    potencia_leds_camara(0)
    braille_cell.trigger([1,0,0,0,0,0])
    led_activacion('verde')      

    t_ini_ejecucion = time.time()
    t_ini_bateria = t_ini_ejecucion
    t_bateria = 0
    t_ejecucion = 0
   

    while t_ejecucion <= t_sleep:
        
        try:
            doc_ref = db.collection(u'rillo-main').document(u'funciones').get()
            funciones = doc_ref.to_dict()

            if funciones['recibido']:
                pass
            else:
                modo_digital()
        
        except:
            print("error, no se puede acceder a la base de datos en el modo analogico")


        #Lectura camara %?
        #print("leyendo camera, return 2 variables, [movimiento (boolean), letra (String)")
        #lectura_camara = detectar_letra() %?
        lectura_camara = [0, "a"]

        try:
            pass
            braille_cell.writer(lectura_camara[1])
        except:
            pass
        
        if lectura_camara[0]:
            t_ini_ejecucion = time.time()
        
        #Revisar si en la base de datos hubo un cambio, si lo hubo entrar al modo digital      
        
        if t_bateria >= t_lectura_bateria:
            
            t_ini_bateria = time.time()
            medir_bateria()
        
        print(t_ejecucion)
        t_ejecucion = time.time() - t_ini_ejecucion
        t_bateria = time.time() - t_ini_bateria
    
    modo_sleep()

def modo_digital():
    print("modo digital")
    #En este modo Rillo recibe y envia datos a un servidor de firebase que se comunica con la app

    #apagar camara %?
    print("camara apagada")

    try:
        doc_ref = db.collection(u'rillo-main').document(u'funciones')
        doc_ref.update({
            u'conectado': True
            
        })
    except:
        print("error, no puede acceder a la base de datos al tratar de escribir el nivel de bateria estando en el modo digital")
            
    global t_sleep, modo_actual

    modo_actual = "digital"

    potencia_leds_camara(1)
    braille_cell.trigger([0,0,0,0,0,1])
    led_activacion('azul')
    
    t_ini_ejecucion = time.time()
    t_ini_bateria = t_ini_ejecucion
    t_bateria = 0
    t_ejecucion = 0
    

    while t_ejecucion <= t_sleep:
        
        try:
            doc_ref = db.collection(u'rillo-main').document(u'funciones').get()
            funciones = doc_ref.to_dict()
        except:
            print("error, no se puede acceder a la base de datos en el modo digital")

        if funciones['recibido']:
            pass
        else:
            representar_datos(funciones['funcion'], funciones['dato'])
            t_ini_ejecucion = time.time()
       
        if funciones['conectado']:
            pass
        else:
            modo_analogico()

        if t_bateria >= t_lectura_bateria:
                        
            try:
                doc_ref = db.collection(u'rillo-main').document(u'nivel-bateria')
                doc_ref.update({
                    u'bateria': nivel_bateria
                })
            except:
                print("error, no puede acceder a la base de datos al tratar de escribir el nivel de bateria estando en el modo digital")
            
            t_ini_bateria = time.time()

        t_ejecucion = time.time() - t_ini_ejecucion
        t_bateria = time.time() - t_ini_bateria

    modo_sleep()

def modo_sleep():
    """ En este modo se apaga la camara, los leds de la camara y """
    print("modo sleep")
    # apagar_camara() %?
    print("camara apagada") 

    global t_lectura_bateria, t_shutdown, modo_actual, interrupcion_activo, stop_parpadeo_led

    modo_actual = "sleep"
    potencia_leds_camara(1)
    
    t_ejecucion = 0
    t_ini = time.time()
    t_ini_bateria = t_ini
    t_bateria = 0

    interrupcion_activo = pigpio_controller.callback(pin_boton_activacion, 1, modo_activo)

    while (t_ejecucion <= t_shutdown) and modo_actual == "sleep":

        try:
            doc_ref = db.collection(u'rillo-main').document(u'funciones').get()
            funciones = doc_ref.to_dict()

            if funciones['recibido']:
                pass
            else:
                stop_parpadeo_led = True
                modo_digital()
        
        except:
            print("error, no se puede acceder a la base de datos en el modo sleep")


        if t_bateria >= t_lectura_bateria:
                        
            try:
                doc_ref = db.collection(u'rillo-main').document(u'nivel-bateria')
                doc_ref.update({
                    u'bateria': nivel_bateria
                })
            except:
                print("error, no puede acceder a la base de datos al tratar de escribir el nivel de bateria estando en el modo digital")
            
            t_ini_bateria = time.time()
        
        t_ejecucion = time.time() - t_ini
        t_bateria = time.time() - t_ini_bateria
        
    if modo_actual == "sleep":
        raise apagadox

    elif modo_actual == "analogico":

        try:
            modo_analogico()
            
        except apagadox:
            apagado_automatico()

    else:
        print("Error, el modo actual es distinto de los valores digital, analogico o sleep en la funcion modo_sleep()")
    
def led_activacion(color_led):
    # print("Led activacion")
    # Hay 4 colores verde, azul, cian y off

    if color_led == 'verde':
        pigpio_controller.write(pin_led_rgb_g, 0)
        pigpio_controller.write(pin_led_rgb_b, 1)
    
    elif color_led == 'azul':
        pigpio_controller.write(pin_led_rgb_g, 1)
        pigpio_controller.write(pin_led_rgb_b, 0)

    elif color_led == 'off':
        pigpio_controller.write(pin_led_rgb_g, 1)
        pigpio_controller.write(pin_led_rgb_b, 1)

    else:
        print("error: led_activacion, color led no identificado")

def boton_nivel_bateria(gpio, level, tick):

    """ Esta funcion es activada por una interrupcion dada por el boton del dispositivo, lo que hace es representar el nivel de la batería
        en 3 estados, alto, medio o bajo, haciendo vibrar la celda braille"""

    nivel_bateria = medir_bateria()

    print(f"\nnivel de bateria: {nivel_bateria}\n")

    niveles_bateria_braille = [[0, 0, 1, 0, 0, 1], [0, 1, 0, 0, 1, 0], [1, 0, 0, 1, 0, 0]]

    current_braille_parameters = braille_cell.parameters()
    braille_cell.parameters(4, 0.5, 0.5, 1)
    if nivel_bateria >= 3.7:
        for n_bateria in niveles_bateria_braille:
            braille_cell.trigger(n_bateria)
    
    elif nivel_bateria >= 3.5:

        for n_bateria in range(0,2):
            braille_cell.trigger(niveles_bateria_braille[n_bateria])

    elif nivel_bateria >= 3.3:

        braille_cell.trigger(niveles_bateria_braille[0])

    else:
        print("error, boton nivel bateria, nivel medido no identificado")

    braille_cell.parameters(current_braille_parameters["power"], current_braille_parameters["time_on"], current_braille_parameters["time_off"], current_braille_parameters["signal_type"])


def datos_recibidos():
    try:
        doc_ref = db.collection(u'rillo-main').document(u'funciones')
        doc_ref.update({
            u'recibido': 1
        })
    except:
        print("error, no puede acceder a la base de datos al confirmar que se recibió un dato")
    
def representar_datos(funcion, datos):
    print("representar datos")
    

    if funcion == 'escribir':
        braille_cell.writer(datos)
        datos_recibidos()

    elif funcion == 'perfil_vibracion':
        braille_cell.power = datos[0]
        braille_cell.time_on = datos[1]
        braille_cell.time_off = datos[2]
        braille_cell.signal_type = datos[3]

        datos_csv = [['intensidad', braille_cell.power],['tiempo_on',braille_cell.time_on], ['tiempo_off', braille_cell.time_off], ['signnal', braille_cell.signal_type]]

        with open('variables_rillo.csv', 'w', newline='') as myFile:
            writer = csv.writer(myFile)
            writer.writerows(datos_csv)

        
        braille_cell.trigger([0,0,0,0,0,1])

        datos_recibidos()

    elif funcion == 'generador':
        braille_cell.generator()
        datos_recibidos()

    elif funcion == 'celda':
        braille_cell.trigger(datos)
        datos_recibidos()

    elif funcion == "nope":
        datos_recibidos()

    else:
        print("error, funcion no identificada en la lectura de datos digitales")

#interrupciones
interrupcion_bateria = pigpio_controller.callback(pin_boton_bateria, GPIO.RISING_EDGE, boton_nivel_bateria)
saludo()

try:

    modo_analogico()

except apagadox:
    
    apagado_automatico()