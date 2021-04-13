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
    
    m00 = M["m00"]

    if m00 == 0:
        m00 = 1

    cX = int(M["m10"] / m00)
    cY = int(M["m01"] / m00)
    return [int(cX), int(cY)]

def crosshair(img, point, size, color):
    """ Desenha um crosshair centrado no point.
        point deve ser uma tupla (x,y)
        color é uma tupla R,G,B uint8
    """
    x,y = point
    cv2.line(img,(x - size,y),(x + size,y),color,3)
    cv2.line(img,(x,y - size),(x, y + size),color,3)

def morpho_limpa(mask, tamanho):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(tamanho,tamanho))
    mask = cv2.morphologyEx( mask, cv2.MORPH_OPEN, kernel )
    mask = cv2.morphologyEx( mask, cv2.MORPH_CLOSE, kernel )    
    return mask

def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)

    # return the edged image
    return edged

### 

def gray_to_bgr(gray):
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


def acha_contornos(canal_red, p1, p2):

    matriz = np.zeros((3,3), dtype=np.uint8)

    contornos, arvore = cv2.findContours(canal_red.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)     

    temp = gray_to_bgr(canal_red)

    for c in contornos: 
        x,y = center_of_mass(c)
        lin, col = onde_velha(p1, p2, (x,y))

        matriz[lin][col] = 1

        crosshair(temp, (x,y), 9, (255,0,0))

    cv2.drawContours(temp, contornos, -1, [0, 0, 255], 3)

    cv2.imshow("contornos", temp)

    return matriz


def onde_terco(minimo, maximo, valor):
    passo = (maximo - minimo)/3
    posicao = int((valor - minimo)/passo) 
    return posicao


def onde_velha(p1, p2, p):
    linha = onde_terco(p1[0], p2[0], p[0])
    coluna = onde_terco(p1[1], p2[1], p[1])
    return (linha,coluna)

def refina_circulos(red, matriz, p1, p2):
    mat = matriz.copy()
    mask_limiar = red
    bordas = auto_canny(mask_limiar)
    circles=cv2.HoughCircles(image=bordas,method=cv2.HOUGH_GRADIENT,dp=2.5,minDist=40,param1=50,param2=100,minRadius=5,maxRadius=150)
    mask_limiar_rgb = cv2.cvtColor(mask_limiar, cv2.COLOR_GRAY2RGB)
    bordas_rgb = cv2.cvtColor(bordas, cv2.COLOR_GRAY2RGB)

    output =  bordas_rgb

    if circles is not None:        
        circles = np.uint16(np.around(circles))
        for i in circles[0,:]:
            # draw the outer circle

            x = i[0]
            y = i[1]

            c = (x, y)

            cv2.circle(output,(i[0],i[1]),i[2],(0,255,0),2)
            # draw the center of the circle
            cv2.circle(output,(i[0],i[1]),2,(0,0,255),3)    
            
            # Aqui dentro - corrige a matriz
            lin, col = onde_velha(p1, p2, c)
            mat[lin][col] = 2 # 2 e codigo para bolinha
    cv2.imshow("transformada de hough", output)
    return mat



def processa(bgr_in):
    bgr = bgr_in.copy() 
    g = bgr[:,:,1]

    limiar = 120

    g[g > limiar] = 255   
    g[g < limiar] = 0

    g = morpho_limpa(g, 3)

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

    pmin = (x_min, y_min)
    pmax = (x_max, y_max)

    cv2.rectangle(g_bgr, pmin , pmax, color=(0,255,0))

    saida = g_bgr


    r = bgr[:,:,2]

    limiar_red = 120

    r[r > limiar_red] = 255   
    r[r < limiar_red] = 0

    r = morpho_limpa(r, 3)

    r_bgr = gray_to_bgr(r)

    saida = r_bgr

    matriz = acha_contornos(r, pmin, pmax)

    matriz = refina_circulos(r, matriz, pmin, pmax)

    print("matriz") 
    print(matriz.T)
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


