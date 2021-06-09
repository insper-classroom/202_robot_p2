#! /usr/bin/env python3
# -*- coding:utf-8 -*-

from __future__ import print_function, division


# Para rodar, recomendamos que faça:
# 
#    roslaunch my_simulation pista_u.launch
#
# Depois o controlador do braço:
#
#    roslaunch mybot_description mybot_control2.launch 	

# This code can be seen running at https://youtu.be/pVpvHJr6G-I

import rospy 

import numpy as np

import cv2
import cv2.aruco as aruco

from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import Image, CompressedImage
from cv_bridge import CvBridge, CvBridgeError
from std_msgs.msg import Float64

import math


ranges = None
minv = 0
maxv = 10

bridge = CvBridge()

### REsposta feita na revisao em 08/6/21


def processa_amarelo(bgr): 
    """ recebe uma imagem bgr e devolve o centro de massa do maior contorno amarelo"""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    low = np.array([ 20, 50,50],dtype=np.uint8 )
    high = np.array([ 38, 255,255],dtype=np.uint8 )
    mask_yellow = cv2.inRange(hsv, low, high)

    return mask_yellow

## Codigo vindo da aula 03 

def center_of_mass(mask):
    """ Retorna uma tupla (cx, cy) que desenha o centro do contorno"""
    M = cv2.moments(mask)
    # Usando a expressão do centróide definida em: https://en.wikipedia.org/wiki/Image_moment
    m00 = max(1, M["m00"])
    cX = int(M["m10"] / m00) # para nao dar divisao por zero quando o contorno tem só 1 px
    cY = int(M["m01"] / m00)
    return [int(cX), int(cY)]

def crosshair(img, point, size, color):
    """ Desenha um crosshair centrado no point.
        point deve ser uma tupla (x,y)
        color é uma tupla R,G,B uint8
    """
    x,y = point
    cv2.line(img,(x - size,y),(x + size,y),color,5)
    cv2.line(img,(x,y - size),(x, y + size),color,5)

def center_of_mass_region(mask, x1, y1, x2, y2):
    # Para fins de desenho
    mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    clipped = mask[y1:y2, x1:x2]
    c = center_of_mass(clipped)
    c[0]+=x1
    c[1]+=y1
    crosshair(mask_bgr, c, 10, (0,0,255))
    cv2.rectangle(mask_bgr, (x1, y1), (x2, y2), (255,0,0),2,cv2.LINE_AA)
    return mask_bgr, c

aruco_dict  = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)

def detecta_aruco(bgr, dict_aruco):

    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    #--- Define the aruco dictionary
    # parameters  = aruco.DetectorParameters_create()
    # parameters.minDistanceToBorder = 0
    # parameters.adaptiveThreshWinSizeMax = 1000

    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict) #, parameters=parameters)


    aruco.drawDetectedMarkers(bgr, corners, ids)

    return corners, ids 


centro_imagem = [320, 240]
centro_massa_amarelo = [320,240]

ids_vistos = []

###



def scaneou(dado):
    global ranges
    global minv
    global maxv
    print("Faixa valida: ", dado.range_min , " - ", dado.range_max )
    print("Leituras:")
    ranges = np.array(dado.ranges).round(decimals=2)
    minv = dado.range_min 
    maxv = dado.range_max
 
# A função a seguir é chamada sempre que chega um novo frame
def roda_todo_frame(imagem):
    global centro_massa_amarelo
    global centro_imagem

    print("frame")
    try:
        cv_image = bridge.compressed_imgmsg_to_cv2(imagem, "bgr8")
        #cv2.imshow("Camera", cv_image)

        mask_amarela = processa_amarelo(cv_image)


        larg = mask_amarela.shape[1]
        alt  = mask_amarela.shape[0]
        inicio_y = int(alt/2)
        fim_y = int((3/4)*alt)

        centro_imagem = [int(larg/2), int(alt/2)]

        mask_bgr, cm = center_of_mass_region(mask_amarela, 0, inicio_y, larg, fim_y)
        
        centro_massa_amarelo = cm

        cv2.imshow("Centro de massa", mask_bgr)

        
        #cv2.imshow("Amarelo", mask_amarela)


        corners, ids = detecta_aruco(cv_image, aruco_dict)

        cv2.imshow("Filtro", cv_image)

        ids_vistos.clear()

        tamanho_min = 50

        if ids is not None and len(ids) > 0: 

            for i in range(len(ids)):
                print('ID: {}'.format(ids[i][0]))


                # Vejam este notebook para entender os índices abaixo: 
                # https://github.com/Insper/robot21.1/blob/main/projeto/aruco/aruco.ipynb
                if ids[i][0] == 20: 

                    tamanho = corners[i][0][1][0] - corners[i][0][0][0]
                    print("Tamanho: {}".format(tamanho))
                    if tamanho > tamanho_min:
                        ids_vistos.append(ids[i])

                    
        cv2.waitKey(1)
    except CvBridgeError as e:
        print('ex', e)

if __name__=="__main__":

    rospy.init_node("q3")

    topico_imagem = "/camera/image/compressed"
    velocidade_saida = rospy.Publisher("/cmd_vel", Twist, queue_size = 3 )
    recebe_scan = rospy.Subscriber("/scan", LaserScan, scaneou)
    recebedor = rospy.Subscriber(topico_imagem, CompressedImage, roda_todo_frame, queue_size=4, buff_size = 2**24)

    ombro = rospy.Publisher("/joint1_position_controller/command", Float64, queue_size=1)

    max_w = 1.4 # rad 
    v_frente = 0.4 
    max_delta = 640/2

    zero = Twist(Vector3(0,0,0), Vector3(0,0,0))
    giro = Twist(Vector3(0,0,0), Vector3(0,0,0.7))


    nao_terminou = True 


    estado = "INICIAL"


    while not rospy.is_shutdown():
        ## centro_massa_amarelo 
        ## centro_imagem


    # (20 not in ids_vistos) and nao_terminou

        if estado == "SEGUINDO": 
            delta_x = centro_massa_amarelo[0] - centro_imagem[0]

            rot = -(delta_x * max_w)/max_delta

            vel = Twist(Vector3(v_frente,0,0), Vector3(0,0,rot))

            velocidade_saida.publish(vel)

            if 20 in ids_vistos:
                estado = "VIU"

        if estado == "INICIAL":
            velocidade_saida.publish(zero)
            velocidade_saida.publish(zero)
            rospy.sleep(1)
            estado = "SEGUINDO"

        if estado == "VIU": 
            velocidade_saida.publish(zero)
            ombro.publish(1.5)
            rospy.sleep(1)
            velocidade_saida.publish(giro)
            estado = "FINAL"


        if estado == "FINAL":
            velocidade_saida.publish(giro)

        rospy.sleep(0.05)
