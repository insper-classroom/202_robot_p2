#! /usr/bin/env python
# -*- coding:utf-8 -*-
# Sugerimos rodar com:
#     roslaunch my_simulation novas_formas.launch
#
# Este código pode ser visto em: https://youtu.be/1Jf4EyDMw2Q
#
# RESPOSTA DA QUESTAO 3 - DETECTAR A FORMA, CENTRALIZAR E SE APROXIMAR PARANDO VIA LASER A UMA DISTANCIA ESPECIFICA


from __future__ import print_function, division
import rospy

import numpy as np

import cv2

from geometry_msgs.msg import Twist, Vector3
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import Image, CompressedImage
from cv_bridge import CvBridge, CvBridgeError

import math


ranges = [10]
minv = 0
maxv = 10

bridge = CvBridge()

# Evitando um problema de condicao inicial
c_img = [320, 240]
c_objeto = [640, 240]


### Coisas copiadas dos exemplos para projeto

def center_of_mass(mask):
    """ Retorna uma tupla (cx, cy) que desenha o centro do contorno"""
    M = cv2.moments(mask)
    # Usando a expressão do centróide definida em: https://en.wikipedia.org/wiki/Image_moment
    if M["m00"] == 0:
        M["m00"] = 1
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    return [int(cX), int(cY)]

def crosshair(img, point, size, color):
    """ Desenha um crosshair centrado no point.
        point deve ser uma tupla (x,y)
        color é uma tupla R,G,B uint8
    """
    x,y = point
    cv2.line(img,(x - size,y),(x + size,y),color,5)
    cv2.line(img,(x,y - size),(x, y + size),color,5)

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
    global c_img
    global c_objeto

    print("frame")
    try:
        cv_image = bridge.compressed_imgmsg_to_cv2(imagem, "bgr8")
        #cv2.imshow("Camera", cv_image)

        bgr = cv_image.copy()

        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

        mini = np.array([142, 50,50])#, dtype=np.uint8)
        maxi = np.array([170, 255,255])#, dtype=np.uint8)

        mask = cv2.inRange(hsv, mini , maxi)

        mask_bgr = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        cm = center_of_mass(mask)


        crosshair(mask_bgr, cm, 15, color=(0,0,255))


        ## Centro da imagem
        cimg = (int(cv_image.shape[1]/2), int(cv_image.shape[0]/2))

        crosshair(mask_bgr, cimg, 25, color=(0,255,0))

        cv2.imshow('Mascara', mask_bgr)


        c_img = cimg
        c_objeto = cm

        cv2.waitKey(1)
    except CvBridgeError as e:
        print('ex', e)

if __name__=="__main__":

    rospy.init_node("q4")

    topico_imagem = "/camera/rgb/image_raw/compressed"
    velocidade_saida = rospy.Publisher("/cmd_vel", Twist, queue_size = 3 )
    recebe_scan = rospy.Subscriber("/scan", LaserScan, scaneou)
    recebedor = rospy.Subscriber(topico_imagem, CompressedImage, roda_todo_frame, queue_size=4, buff_size = 2**24)

    pub = rospy.Publisher("cmd_vel", Twist, queue_size=3)
    
    w = 0.25
    v = 0.25

    zero = Twist(Vector3(0,0,0), Vector3(0,0,0))
    dire = Twist(Vector3(0,0,0), Vector3(0,0,-w))
    esq = Twist(Vector3(0,0,0), Vector3(0,0,w))
    frente = Twist(Vector3(v,0,0), Vector3(0,0,0))



    while not rospy.is_shutdown():
        x = 0
        y = 1
        margem = int(0.15*c_img[0])
        # Checar se objeto esta a esq
        if c_objeto[x] < c_img[x] - margem:
            pub.publish(esq)
        # Checar se objeto esta a dir
        elif c_objeto[x] > c_img[x] + margem:
            pub.publish(dire)
        else: 
        # Se centralizado, seguir em frente
            pub.publish(frente)

            if ranges[0] <=1.5:
                pub.publish(zero)

        rospy.sleep(0.01)



