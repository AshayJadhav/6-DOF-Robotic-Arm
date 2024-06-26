

#from sympy import symbols, cos, sin, pi, simplify, pprint, tan, expand_trig, sqrt, trigsimp, atan2, asin, acos
#from sympy.matrices import Matrix
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import time
from numpy import arctan2, arcsin, sqrt, arccos
import numpy as np

a1 = 10
a2 = 9.0    #a3
a3 = 6
a4 = 7   # unka a4= hamara a3 + a4
a5 = 6
a6 = 6   # unka a6= hamara a6 + a5


# position of end effector
px, py, pz = 13, 9, 9
# value of orientation of the end effector
roll, pitch, yaw = 1, 1, 0



def get_cosine_law_angle(a, b, c):
    # given all sides of a triangle a, b, c
    # calculate angle gamma between sides a and b using cosine law
  
    gamma = np.arccos((a*a + b*b - c*c)/(2*a*b))
    return gamma

def griperCenter(px, py, pz, R06):
    # calculating griper center, see in arm diagram for detail
    Xc = px - (a5+a6)*R06[0,2]
    Yc = py - (a5+a6)*R06[1,2]
    Zc = pz - (a5+a6)*R06[2,2]
    return Xc, Yc, Zc
    
def calcFirst3Angles(Xc, Yc, Zc):
    # doing inverse kinematics on first 3 dof the reach the center of griper
    # see the calculation page of inverse kinematics for more details
    
    q1 = np.arctan2(Yc,Xc)
    '''  r1 = np.sqrt(Xc**2 + Yc**2)
    r2 = np.sqrt((r1-a2)**2 + (Zc-a1)**2)
    phi1 = np.arctan((Zc-a1)/(r1-a2))
    phi2 = get_cosine_law_angle(a3, r2, a4)
    q2 = phi1 + phi2

    phi3 = get_cosine_law_angle(a3, a4, r2)
    q3 = phi3 - np.pi '''

    r=np.sqrt((Zc-a1)*(Zc-a1) + (Xc/(np.cos(q1)))*(Xc/(np.cos(q1))))
    phi1=np.arccos((r*r + (a2)*a2 - (a3 + a4)*(a3 + a4))/(2*r*a2))
    phi2=np.arctan(((Zc-a1)/(np.sqrt(Xc*Xc + Yc*Yc))))
    q2=phi2+phi1                                                            # reason not known
    q3=np.pi-np.arccos((a2*a2 + (a3 + a4)*(a3 + a4)- r*r)/(2*a2*(a3+a4)))   #jugaad
    q3=-q3

    return q1, q2, q3

def calcLast3Angles(R36):
    # evaluating last 3 angles by comparing the matrices
    # R36 = Matrix([[-sin(q4)*sin(q6) + cos(q4)*cos(q5)*cos(q6), -sin(q4)*cos(q6) - sin(q6)*cos(q4)*cos(q5), sin(q5)*cos(q4)],
    #               [sin(q4)*cos(q5)*cos(q6) + sin(q6)*cos(q4), -sin(q4)*sin(q6)*cos(q5) + cos(q4)*cos(q6), sin(q4)*sin(q5)],
    #               [-sin(q5)*cos(q6)                         , sin(q5)*sin(q6)                           , cos(q5)]])

    q4 = np.arctan2(R36[1,2],R36[0, 2])

    q5 = np.arccos(R36[2,2])

    #q6 = np.arcsin(R36[2,1]/np.sin(q5))
    q6 = np.arctan2(R36[2,1],-R36[2,0])
    return q4, q5, q6

def get_angles(px, py, pz, b, a, c):

    # the frame of griper is pre-rotated from bellow rotation matrix
    R6a = np.array([[0, 0, 1.0], [0, -1.0, 0], [1.0, 0, 0]])
    
    # rotation matrix after rotating around y-axis (pitch)
    A = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])

    # rotation matrix after rotating around z-axis (roll)
    B = np.array([[np.cos(b), -np.sin(b), 0], [np.sin(b), np.cos(b), 0], [0, 0, 1]])

    # rotation matrix after rotating around x-axis (yaw)
    C = np.array([[1, 0, 0], [0, np.cos(c), -np.sin(c)], [0, np.sin(c), np.cos(c)]])

    # after total rotation of pitch, roll and yaw
    R6b = np.dot(np.dot(A,B),C)
    R06 = np.dot(R6a,R6b)
    # print(np.matrix(R06))

    # calculating center of griper
    Xc, Yc, Zc = griperCenter(px, py, pz, R06)

    # calculating first 3 angles
    q1, q2, q3 = calcFirst3Angles(Xc, Yc, Zc)

    # rotation matrix of 3 wrt 0 frame  see the calculation sheet for more understanding
    # homogeneous matrices
    H0_1 = np.array([[np.cos(q1),0,np.sin(q1)],
                  [np.sin(q1),0,-np.cos(q1)],
                  [0,1,0]])
    H1_2 = np.array([[np.cos(q2),-np.sin(q2),0],
                  [np.sin(q2),np.cos(q2),0],
                  [0,0,1]])
    H2_3 = np.array([[-np.sin(q3),0,np.cos(q3)],
                  [np.cos(q3),0,np.sin(q3)],
                  [0,1,0]])
    ''' H3_4 = Matrix([[cos(q4),0,-sin(q4),0],
                  [sin(q4),0,cos(q4),0],
                  [0,-1,0,a3+a4],
                  [0,0,0,1]])
    H4_5 = Matrix([[cos(q5),0,sin(q5),0],
                  [sin(q5),0,-cos(q5),0],
                  [0,1,0,0],
                  [0,0,0,1]])
    H5_6 = Matrix([[cos(q6),-sin(q6),0,0],
                  [sin(q6),cos(q6),0,0],
                  [0,0,1,(a5+a6)],
                  [0,0,0,1]])
    
    H0_6 = H0_1*H1_2*H2_3*H3_4*H4_5*H5_6  '''
    
    # rotation matrices
    '''  R0_1 = H0_1[:3][:3]
    R0_2 = R0_1*H1_2[:3][ :3]
    R0_3 = R0_2*H2_3[:3][ :3]'''

    R0_1 = H0_1
    R0_2 = np.dot(H0_1,H1_2)
    R0_3 = np.dot(R0_2,H2_3)   

    ''' R0_4 = R0_3*H3_4[:3, :3]
    R0_5 = R0_4*H4_5[:3, :3]
    R0_6 = R0_5*H5_6[:3, :3]  '''

    IR03=np.linalg.inv(R0_3) 
    # IR03 = np.transpose(R0_3)
    R36 = np.dot(IR03, R06)

    q4, q5, q6 = calcLast3Angles(R36)
    return q1, q2, q3, q4, q5, q6

q1, q2, q3, q4, q5, q6 = get_angles(px, py, pz, roll, pitch, yaw)

print("q1 : ", q1)
print("q2 : ", q2)
print("q3 : ", q3)
print("q4 : ", q4)
print("q5 : ", q5)
print("q6 : ", q6)


 # homogeneous matrices

def homogenousmatrices(q1, q2, q3, q4, q5, q6):
  h0_1 = np.array([[np.cos(q1),0,np.sin(q1),0],
                  [np.sin(q1),0,-np.cos(q1),0],
                  [0,1,0,a1],
                  [0,0,0,1]])
 
  h1_2 = np.array([[np.cos(q2),-np.sin(q2),0,a2*np.cos(q2)],
                  [np.sin(q2),np.cos(q2),0,a2*np.sin(q2)],
                  [0,0,1,0],
                  [0,0,0,1]])
 
  h0_2 = np.dot(np.array(h0_1), np.array(h1_2))
 
  h2_3 = np.array([[-np.sin(q3),0,np.cos(q3),0],
               [np.cos(q3),0,np.sin(q3),0],
               [0,1,0,0],
               [0,0,0,1]])
 
  h0_3 = np.dot(np.array(h0_2), np.array(h2_3))
 
  h3_4 = np.array([[np.cos(q4),0,-np.sin(q4),0],
               [np.sin(q4),0,np.cos(q4),0],
               [0,-1,0,a3+a4],
               [0,0,0,1]])
  h0_4 = np.dot(np.array(h0_3), np.array(h3_4))
 
  h4_5 = np.array([[np.cos(q5),0,np.sin(q5),0],
               [np.sin(q5),0,-np.cos(q5),0],
               [0,1,0,0],
               [0,0,0,1]])
  h0_5 = np.dot(np.array(h0_4), np.array(h4_5))
 
  h5_6 = np.array([[np.cos(q6),-np.sin(q6),0,0],
               [np.sin(q6),np.cos(q6),0,0],
               [0,0,1,(a5+a6)],
               [0,0,0,1]])
  h0_6 = np.dot(np.array(h0_5), np.array(h5_6))
  X=[]
  Y=[]
  Z=[]
  X.append(0)
  X.append(0)
  X.append(h0_1[0, 3])
  X.append(h0_2[0, 3])
  X.append(h0_3[0, 3])
  X.append(h0_4[0, 3])
  X.append(h0_5[0, 3])
  X.append(h0_6[0, 3])



  Y.append(0)
  Y.append(0)
  Y.append(h0_1[1, 3])
  Y.append(h0_2[1, 3])
  Y.append(h0_3[1, 3])
  Y.append(h0_4[1, 3])
  Y.append(h0_5[1, 3])
  Y.append(h0_6[1, 3])

  Z.append(0)
  Z.append(a1)
  Z.append(h0_1[2, 3])
  Z.append(h0_2[2, 3])
  Z.append(h0_3[2, 3])
  Z.append(h0_4[2, 3])
  Z.append(h0_5[2, 3])
  Z.append(h0_6[2, 3])
  return h0_6[0,3],h0_6[1,3],h0_6[2,3],X,Y,Z


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_xlabel('x axis')
ax.set_ylabel('y axis')
ax.set_zlabel('z axis')

Xx=[]
Yy=[]
Zz=[]
i=9
for i in range (9,17,1):
  px, py, pz= 7, 9, i
  q1, q2, q3, q4, q5, q6 = get_angles(px, py, pz, roll, pitch, yaw)
  x1, y1, z1, X, Y, Z=homogenousmatrices(q1, q2, q3, q4, q5, q6)
  Xx.append([x1])
  Yy.append([y1])
  Zz.append([z1])
  X = np.reshape(X, (1, 8))
  Y = np.reshape(Y, (1, 8))
  Z = np.reshape(Z, (1, 8)) 
  #ax.plot_wireframe(X, Y, Z) 
  fig.canvas.draw_idle()
  fig.canvas.flush_events()
  time.sleep(0.01)

for i in range (7,14,1):
  px, py, pz= i, 9, 16
  q1, q2, q3, q4, q5, q6 = get_angles(px, py, pz, roll, pitch, yaw)
  x1, y1, z1, X, Y, Z=homogenousmatrices(q1, q2, q3, q4, q5, q6)
  Xx.append([x1])
  Yy.append([y1])
  Zz.append([z1])
  X = np.reshape(X, (1, 8))
  Y = np.reshape(Y, (1, 8))
  Z = np.reshape(Z, (1, 8)) 
  #ax.plot_wireframe(X, Y, Z) 
  fig.canvas.draw_idle()
  fig.canvas.flush_events()
  time.sleep(.010)

for i in range (16,12,-1):
  px, py, pz= 13, 9, i
  q1, q2, q3, q4, q5, q6 = get_angles(px, py, pz, roll, pitch, yaw)
  x1, y1, z1, X, Y, Z=homogenousmatrices(q1, q2, q3, q4, q5, q6)
  Xx.append([x1])
  Yy.append([y1])
  Zz.append([z1])
  X = np.reshape(X, (1, 8))
  Y = np.reshape(Y, (1, 8))
  Z = np.reshape(Z, (1, 8)) 
  #ax.plot_wireframe(X, Y, Z) 
  fig.canvas.draw_idle()
  fig.canvas.flush_events()
  time.sleep(.10) 
  

for i in range (13,6,-1):
  px, py, pz= i, 9, 13
  q1, q2, q3, q4, q5, q6 = get_angles(px, py, pz, roll, pitch, yaw)
  x1, y1, z1, X, Y, Z=homogenousmatrices(q1, q2, q3, q4, q5, q6)
  Xx.append([x1])
  Yy.append([y1])
  Zz.append([z1])
  X = np.reshape(X, (1, 8))
  Y = np.reshape(Y, (1, 8))
  Z = np.reshape(Z, (1, 8)) 
  #ax.plot_wireframe(X, Y, Z) 
  fig.canvas.draw_idle()
  fig.canvas.flush_events()
  time.sleep(.10)

j=13+4/6
for i in range (7,14,1):
  j=j-4/5
  px, py, pz= i, 9, j
  q1, q2, q3, q4, q5, q6 = get_angles(px, py, pz, roll, pitch, yaw)
  x1, y1, z1, X, Y, Z=homogenousmatrices(q1, q2, q3, q4, q5, q6)
  Xx.append([x1])
  Yy.append([y1])
  Zz.append([z1])
  X = np.reshape(X, (1, 8))
  Y = np.reshape(Y, (1, 8))
  Z = np.reshape(Z, (1, 8)) 
  #ax.plot_wireframe(X, Y, Z) 
  fig.canvas.draw_idle()
  fig.canvas.flush_events()
  time.sleep(.010)

Xx = np.reshape(Xx, (1,33))
Yy= np.reshape(Yy, (1,33))
Zz= np.reshape(Zz, (1,33))

ax.plot_wireframe(Xx, Yy, Zz,color='r')

px=px-1
x1, y1, z1, X, Y, Z=homogenousmatrices(q1, q2, q3, q4, q5, q6)
 
X = np.reshape(X, (1, 8))
Y = np.reshape(Y, (1, 8))
Z = np.reshape(Z, (1, 8)) 
ax.plot_wireframe(X, Y, Z)
print("X=",X[0,-1]," Y=",Y[0,-1]," Z=",Z[0,-1])
 

plt.show()
