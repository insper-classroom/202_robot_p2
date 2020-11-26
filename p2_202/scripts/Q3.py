#! /usr/bin/env python
# -*- coding:utf-8 -*-

# Sugerimos rodar com:
# roslaunch turtlebot3_gazebo  turtlebot3_empty_world.launch 
# RESPOSTA DA QUESTAO 4 - POLIGONO REGULAR
#
# Can be seen runnning at https://youtu.be/Mpi8JuHOoLY
#

from __future__ import print_function, division
import rospy
import numpy as np
import cv2
from geometry_msgs.msg import Twist, Vector3
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist, Vector3
import math
import time
from tf import transformations


x = None
y = None
angle_z = None

contador = 0
pula = 50

velocidade_saida = None

def recebe_odometria(data):
    global x
    global y
    global contador
    global angle_z

    x = data.pose.pose.position.x
    y = data.pose.pose.position.y

    quat = data.pose.pose.orientation
    lista = [quat.x, quat.y, quat.z, quat.w]
    radianos = transformations.euler_from_quaternion(lista)
    angle_z = radianos[2]
    angulos = np.degrees(radianos)    

    if contador % pula == 0:
        print("Posicao (x,y)  ({:.2f} , {:.2f}) + angulo {:.2f}".format(x, y,angulos[2]))
    contador = contador + 1

def segmento(length, v):
    vel = Twist(Vector3(v,0,0), Vector3(0,0,0))
    delta_t = length/v
    velocidade_saida.publish(vel)
    rospy.sleep(delta_t)


def rotacao(angle_rad, w):
    global angle_z
    angle_0 = angle_z
    if angle_0 < 0.0:
        angle_0 = angle_0 + 2*math.pi        
    vel_ang = Twist(Vector3(0,0,0), Vector3(0,0,w))
    zero = Twist(Vector3(0,0,0), Vector3(0,0,0))        
    
    local_z = angle_z

    if local_z < 0: 
        local_z = local_z + 2*math.pi

    while(local_z < angle_0 + angle_rad):
        print('angle z atual : {} angle 0 inicial: {} target {}'.format(local_z, angle_0,angle_0 + angle_rad))     
        velocidade_saida.publish(vel_ang)
        rospy.sleep(0.01)

        local_z = angle_z
        if local_z < 0: 
            local_z = local_z + 2*math.pi        
    velocidade_saida.publish(zero)
    rospy.sleep(0.1)


def desenha_poligono(n):

    v = 0.25
    w = 0.15

    angle_deg = 360.0/n 
    angle_rad = math.radians(angle_deg)

    for i in range(n):
        segmento(1.2, v)
        rotacao(angle_rad, w)







if __name__=="__main__":

    rospy.init_node("q3")

    velocidade_saida = rospy.Publisher("/cmd_vel", Twist, queue_size = 3 )

    ref_odometria = rospy.Subscriber("/odom", Odometry, recebe_odometria)


    rospy.sleep(1.0) # contorna bugs de timing    

    while not rospy.is_shutdown():
        if angle_z is not None: 
            desenha_poligono(5)
        rospy.sleep(0.5)    
