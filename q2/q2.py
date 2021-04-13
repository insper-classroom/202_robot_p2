#!/usr/bin/python
# -*- coding: utf-8 -*-

# Este NÃO é um programa ROS

from __future__ import print_function, division 

import cv2
import os,sys, os.path
import numpy as np

print("Rodando Python versão ", sys.version)
print("OpenCV versão: ", cv2.__version__)
print("Diretório de trabalho: ", os.getcwd())

# Arquivos necessários
video = "jogovelha.mp4"


### Vindas do arquivo mirutils

def center_of_mass(mask):
    """ Retorna uma tupla (cx, cy) que desenha o centro do contorno"""
    M = cv2.moments(mask)
    # Usando a expressão do centróide definida em: https://en.wikipedia.org/wiki/Image_moment
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    return [int(cX), int(cY)]

def crosshair(img, point, size, color):
    """ Desenha um crosshair centrado no point.
        point deve ser uma tupla (x,y)
        color é uma tupla R,G,B uint8
    """
    x,y = point
    cv2.line(img,(x - size,y),(x + size,y),color,3)
    cv2.line(img,(x,y - size),(x, y + size),color,3)

### 

def gray_to_bgr(gray):
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def acha_contornos(canal_red, p1, p2):
    contornos, arvore = cv2.findContours(canal_red.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)     

    for c in contornos: 





def onde_velha(p1, p2, p):
    return (1,1)




def processa(bgr_in):
    bgr = bgr_in.copy() 
    g = bgr[:,:,1]

    limiar = 120

    g[g > limiar] = 255   
    g[g < limiar] = 0

    linhas, colunas = np.where(g == 255)

    min_linha = np.min(linhas)
    max_linha = np.max(linhas)

    min_col = np.min(colunas)
    max_col = np.max(colunas)

    x_min, x_max = min_col, max_col 
    y_min, y_max = min_linha, max_linha

    # os passos acima poderiam ter sido feitos no Gimp porque
    # a velha (grade) nao muda

    g_bgr = gray_to_bgr(g)

    cv2.rectangle(g_bgr, (x_min, y_min), (x_max, y_max), color=(0,255,0))

    saida = g_bgr


    r = bgr[:,:,2]

    limiar_red = 120

    r[r > limiar_red] = 255   
    r[r < limiar_red] = 0

    r_bgr = gray_to_bgr(r)

    saida = r_bgr

    matriz = acha_contornos(r)




    return saida
    





if __name__ == "__main__":

    # Inicializa a aquisição da webcam
    cap = cv2.VideoCapture(video)


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

        saida = processa(frame)


        # NOTE que em testes a OpenCV 4.0 requereu frames em BGR para o cv2.imshow
        cv2.imshow('saida', saida)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


