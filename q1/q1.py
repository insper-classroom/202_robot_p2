#!/usr/bin/python
# -*- coding: utf-8 -*-

# Este NÃO é um programa ROS

# Esta solução pode ser vista em:
# https://youtu.be/BHu6OodU-iY


from __future__ import print_function, division 

import cv2
import os,sys, os.path
import numpy as np

print("Rodando Python versão ", sys.version)
print("OpenCV versão: ", cv2.__version__)
print("Diretório de trabalho: ", os.getcwd())

# Arquivos necessários
# Baixe e salve na mesma pasta que este arquivo
# https://github.com/Insper/robot20/raw/master/media/relogio.mp4
video = "relogio.mp4"


### Início do código vindo do notebook que está no gabarito em
# https://github.com/insper-classroom/202_robot_p1/blob/solution/q1/Q1.ipynb

import math

def crosshair(img, point, size, color, width=5):
    """ 
        Função vinda da aula 2
        Desenha um crosshair centrado no point.
        point deve ser uma tupla (x,y)
        color é uma tupla R,G,B uint8
    """
    x,y = point
    cv2.line(img,(x - size,y),(x + size,y),color,width)
    cv2.line(img,(x,y - size),(x, y + size),color,width)

def filter(HSV, menor, maior):
    cor1 = np.array(menor, dtype=np.uint8)
    cor2 = np.array(maior, dtype=np.uint8)
    return cv2.inRange(HSV, cor1, cor2)

# Não precisa do filtro vermelho para resolver a questão!
def filter_red(hsv):
    menor = [0, 50, 100]
    maior = [4, 255,255]
    return filter(hsv, menor, maior)    
    
def filter_purple(hsv):
    menor = [125, 50, 50]
    maior = [145, 255,255]
    return filter(hsv, menor, maior)     
    
def filter_orange(hsv):
    menor = [8, 50, 50]
    maior = [34, 255,255]
    return filter(hsv, menor, maior)

def dist(p1, p2):
    """Função distância simples"""
    return np.sqrt(math.pow((p1[0] - p2[0]),2) + math.pow((p1[1]-p2[1]), 2))

def mais_perto_primeiro(referencia, p1, p2):
    """ Aceita 3 pontos: referencia e p1 e p2 e devolve dois pontos com o mais próximo da referencia primeiro"""
    if dist(referencia, p1) < dist(referencia, p2):
        return p1,p2
    else:
        return p2,p1
    

def apply_hough(gray, color_bgr =(255, 0, 0), centro=(305, 246), output_img=None):
    """
        Função hough modificada que devolve os pontos do segmento de reta sempre com o mais distante do centro primeiro
    """
    hough_img = gray
    lines = cv2.HoughLinesP(hough_img, 10, math.pi/180.0, 100, np.array([]), 45, 5)
   
    #if lines is None or len(lines)==0:
    #    return []
    
    a,b,c = lines.shape
    
    
    lines_out = []

                           
    for i in range(a):
        # Faz uma linha ligando o ponto inicial ao ponto final, com a cor vermelha (BGR)
        p1 = (lines[i][0][0], lines[i][0][1])
        p2 = (lines[i][0][2], lines[i][0][3])

        if output_img is not None:
            cv2.line(output_img, p1, p2, color_bgr , 1, cv2.LINE_AA)
            
        lines_out.append(mais_perto_primeiro(centro, p1,p2))
        
    return lines_out
        

def media_segundo_ponto(lista_p1_p2):
    """
        Devolve a média do segundo ponto das tuplas encontradas por hough
    """
    l = lista_p1_p2
    #print(l)
    x = y = 0
    for segmento in l:
        x+=segmento[1][0]
        y+=segmento[1][1]
    n = len(l)
    return int(x/n), int(y/n)
    

def media_crosshair(lista, imagem_bgr, color_cross):
    """
        A partir de uma lista de pontos recebida a partir de hough e desenha um crosshair 
    """
    c = media_segundo_ponto(lista)
    crosshair(imagem_bgr, c, 10, color_cross)
    return c

def delta(centro, ponteiro):
    """
        Recebe o centro da imagem e a ponta do ponteiro e calcula os deltas verticais e horizontais conforme
        imagem presente no gabarito
    """
    x = 0
    y = 1
    delta_horizontal = ponteiro[x] - centro[x]
    delta_vertical = ponteiro[y] - centro[y]
    return delta_horizontal, delta_vertical

def angulo(delta_vertical, delta_horizontal):
    """A partir do delta horizontal e vertical calcula o angulo"""
    # A tangente é a conversão simples que acha o angulo a partir da posicao das 3h
    # Para somar 90 graus somamos pi/2
    # Teremos valores negativos a partir das 9 horas. Para resolver somamos mais um circulo inteiro positivo de 2 pi
    # Por isso chegamos no 5pi/2 = 2.5 pi
    return (math.atan2(delta_vertical, delta_horizontal) + 5.0*math.pi/2.0)%(2*math.pi)

    

    
def minutos(angulo):
    """A partir do angulo encontra os minutos"""
    um_minuto = 2*math.pi/60.0
    return int(angulo/um_minuto)
    
    
def horas(angulo):
    """A partir do angulo encontra as horas
    """
    uma_hora = 2*math.pi/12.0
    return int(angulo/uma_hora)
    
def desenha_horario(bgr, horas, minutos):
    """ Recebe uma imagem BGR, horas e minutos e desenha o horario"""
    font = cv2.FONT_HERSHEY_SIMPLEX
    pos = (300,400)
    fontscale=2
    color=(0,255,255)
    thickness=3
    mensagem = "{:02d}:{:02d}".format(int(horas), int(minutos))
    cv2.putText(bgr, mensagem, pos, font, fontscale, color, thickness, cv2.LINE_AA) 
    
def desenha_angulo(bgr, ang_horas, ang_minutos):
    """ Recebe uma imagem BGR, horas e minutos e desenha os angulos"""
    horas = math.degrees(ang_horas)
    minutos = math.degrees(ang_minutos)
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    pos = (300,150)
    fontscale=2
    color=(255,255,255)
    thickness=3
    mensagem = "{:2d}:{:2d} graus".format(int(horas), int(minutos))
    cv2.putText(bgr, mensagem, pos, font, fontscale, color, thickness, cv2.LINE_AA) 
    
def text_cv(bgr, pos, text, fontscale=1, thickness=1):
    font = cv2.FONT_HERSHEY_SIMPLEX    
    color=(255,255,255)    
    mensagem = "{}".format(text)
    cv2.putText(bgr, mensagem, pos, font, fontscale, color, thickness, cv2.LINE_AA) 

c = (305,246)
# c = (246, 305)
centro = c
h = 0 # horizontal
v = 1 # vertical

def horario_from_bgr(bgr, centro):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    
    hours_purple = filter_purple(hsv)
    minutes_orange = filter_orange(hsv)
    
    list_hours = apply_hough(hours_purple, output_img=bgr)
    list_minutes = apply_hough(minutes_orange, output_img=bgr)
    ponteiro_minutes = media_crosshair(list_minutes, bgr, (255, 128,0))
    ponteiro_hours = media_crosshair(list_hours, bgr, (255, 0, 255))
    
    delta_min = delta(centro, ponteiro_minutes)
    delta_hr = delta(centro, ponteiro_hours)
    
    angulo_min = angulo(delta_min[v], delta_min[h])
    angulo_hr = angulo(delta_hr[v], delta_hr[h])
    
    # Função de debug, descomente para desenhar o angulo
    #desenha_angulo(bgr, angulo_hr, angulo_min)

    hr = horas(angulo_hr)
    minutes = minutos(angulo_min)
    
    desenha_horario(bgr, hr, minutes)
    
    crosshair(bgr, c, 4, (0,0,255))


### Fim do código vindo do notebook



if __name__ == "__main__":

    # Inicializa a aquisição da webcam
    cap = cv2.VideoCapture(video)
    cap.set(cv2.CAP_PROP_FPS, 3)


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

        # Vamos usar a função desenvolvida
        horario_from_bgr(frame, centro)

        # NOTE que em testes a OpenCV 4.0 requereu frames em BGR para o cv2.imshow
        cv2.imshow('Resultado', frame)

        if cv2.waitKey(50) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()


