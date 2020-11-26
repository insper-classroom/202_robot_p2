#!/usr/bin/python
# -*- coding: utf-8 -*-

# Este NÃO é um programa ROS

# Este é o gabarito. Pode ser visto em execução em https://youtu.be/xr3gu3wv2YI


from __future__ import print_function, division 

import cv2
import os,sys, os.path
import numpy as np

print("Rodando Python versão ", sys.version)
print("OpenCV versão: ", cv2.__version__)
print("Diretório de trabalho: ", os.getcwd())

# Arquivos necessários
model = "MobileNetSSD_deploy.caffemodel"
proto = "MobileNetSSD_deploy.prototxt.txt"

video = "animais_caixas.mp4"

def detect(frame):
    """
        Recebe - uma imagem colorida
        Devolve: objeto encontrado
    """
    image = frame.copy()
    (h, w) = image.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)

    # pass the blob through the network and obtain the detections and
    # predictions
    print("[INFO] computing object detections...")
    net.setInput(blob)
    detections = net.forward()

    results = []

    # loop over the detections
    for i in np.arange(0, detections.shape[2]):
        # extract the confidence (i.e., probability) associated with the
        # prediction
        confidence = detections[0, 0, i, 2]

        # filter out weak detections by ensuring the `confidence` is
        # greater than the minimum confidence


        if confidence > CONFIDENCE:
            # extract the index of the class label from the `detections`,
            # then compute the (x, y)-coordinates of the bounding box for
            # the object
            idx = int(detections[0, 0, i, 1])
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # display the prediction
            label = "{}: {:.2f}%".format(CLASSES[idx], confidence * 100)
            print("[INFO] {}".format(label))
            cv2.rectangle(image, (startX, startY), (endX, endY),
                COLORS[idx], 2)
            y = startY - 15 if startY - 15 > 15 else startY + 15
            cv2.putText(image, label, (startX, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

            results.append((CLASSES[idx], confidence*100, (startX, startY),(endX, endY) ))

    # show the output image
    return image, results

########### Funções da solução ###############

from numpy import array, uint8

def filter(HSV, menor, maior):
    cor1 = np.array(menor, dtype=np.uint8)
    cor2 = np.array(maior, dtype=np.uint8)
    return cv2.inRange(HSV, cor1, cor2)

def bounding_box(mask, bgr, color = (0,0,255)):
    """
        Recebe um mesmo frame em BGR e como máscara binária, encontra o maior contorno na máscara
        e desenha o contorno e a caixa envoltória na BGR
    """
    contornos, arvore = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
    cv2.drawContours(bgr, contornos, -1, [255, 255, 0], 3);
    maior = None
    maior_area = 0
    for c in contornos:
        area = cv2.contourArea(c)
        if area > maior_area:
            maior_area = area
            maior = c
    cv2.drawContours(bgr, [maior], -1, [0, 255, 255], 5);
    
    # Inicializando com valores fora da faixa que vai ser encontrada
    max_x = -1
    min_x = 10000
    max_y = -1
    min_y = 10000
    
    # imprimindo o contorno entendemos sua estrutura
    
    for p in maior:
        if p[0][0] > max_x:
            max_x = p[0][0]
        
        if p[0][0] < min_x:
            min_x = p[0][0]
            
        if p[0][1] < min_y:
            min_y = p[0][1]
        
        if p[0][1] > max_y:
            max_y = p[0][1]
    
    minp = (min_x, min_y)
    maxp = (max_x, max_y)
    
    cv2.rectangle(bgr, minp, maxp, color, 3)
    
    return minp, maxp
    
def result_in_mask(tupla_mobilenet, minp, maxp):
    """
        Recebe uma tupla de resultados da mobilenet, por exemplo
        ('cat', 98.16664457321167, (650, 237), (793, 436))
        
        e uma caixa definida por minp e maxp e diz se o animal da tupla está contido na caixa
    """
    t = tupla_mobilenet
    net_min = t[2]
    net_max = t[3]
    
    x = 0
    y = 1
    
    print(net_min, net_max, minp, maxp)
    
    if (net_min[x] > minp[x]) and (net_max[x] < maxp[x]) and (net_min[y] > minp[y]) and (net_max[y] < maxp[y]):
        return True
    else:
        return False    

az1 = np.array([110, 50,50], dtype=np.uint8)
az2 = np.array([120, 255, 255], dtype=np.uint8)
ver1 = np.array([53, 50,50], dtype=np.uint8)
ver2 = np.array([83, 255,255], dtype=np.uint8)

def text_cv(bgr, pos, text, fontscale=2, thickness=2):
    font = cv2.FONT_HERSHEY_SIMPLEX    
    color=(255,255,255)    
    mensagem = "{}".format(text)
    cv2.putText(bgr, mensagem, pos, font, fontscale, color, thickness, cv2.LINE_AA) 

def processa(bgr):
    res = detect(bgr)
    hsv = cv2.cvtColor(bgr,cv2.COLOR_BGR2HSV)
    green = filter(hsv, ver1, ver2)
    blue = filter(hsv, az1, az2)
    
    img = res[0]
    resultados = res[1]

    
    blue_box = bounding_box(blue, img, color = (255,0,0))
    green_box = bounding_box(green, img, color=(0,255,0))
    
    cat_blue = cat_green = dog_blue = dog_green = False

    for r in resultados:
        tupla = r
        if tupla[0] == "dog":
            dog_blue = result_in_mask(tupla, blue_box[0], blue_box[1])
            dog_green = result_in_mask(tupla, green_box[0], green_box[1])        
        if tupla[0] == "cat":
            cat_blue = result_in_mask(tupla, blue_box[0], blue_box[1])
            cat_green = result_in_mask(tupla, green_box[0], green_box[1])      
    
    checks = (cat_blue, cat_green, dog_blue, dog_green)
    msgs = ("Gato na caixa azul",  "Gato na caixa verde", "Cachorro na caixa azul", "Cachorro na caixa verde")
    
    x = 20
    y = 70
    for i in range(len(checks)):
        if checks[i]:
            text_cv(img, (x,y), msgs[i])
            y+=50
            print(msgs[i])
    return img


####



if __name__ == "__main__":

    # Inicializa a aquisição da webcam
    cap = cv2.VideoCapture(video)

    # cria a rede neural
    net = cv2.dnn.readNetFromCaffe(proto, model)

    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
        "sofa", "train", "tvmonitor"]   

    CONFIDENCE = 0.7
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))


    print("Se a janela com a imagem não aparecer em primeiro plano dê Alt-Tab")

    while(True):
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        if ret == False:
            #print("Codigo de retorno FALSO - problema para capturar o frame")
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
            #sys.exit(0)

        # Our operations on the frame come here
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        
        
        
        
        
        ### Aplicação da solução

        output = processa(frame)
        
        # NOTE que em testes a OpenCV 4.0 requereu frames em BGR para o cv2.imshow
        cv2.imshow('Resultado', output)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


