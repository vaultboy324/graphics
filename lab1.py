import os
import random
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders

import numpy

colors = [

]

COUNT_LAYERS = 5
COUNT_ANGLES = 100

time = 10

MAX_Z = -10
MIN_Z = -100

PERSPECTIVE = 0


def generate_colors(layers_count):
    for i in range(0, layers_count):
        colors.append([random.randint(0, 256), random.randint(0, 256), random.randint(0, 256)])


def create_object(layers_count, angles_count):
    double_pi = 2 * numpy.pi
    for i in range(0, layers_count):
        glBegin(GL_QUAD_STRIP)
        glColor3ubv(colors[i])
        for j in range(0, angles_count + 1):

            for k in range(2, 0, -1):
                s = (i + k) % layers_count + 0.5
                t = j % (angles_count + 1)

                theta = s * double_pi / layers_count
                rho = t * double_pi / angles_count

                x = float((1 + 0.2 * numpy.cos(theta)) * numpy.cos(rho))
                y = float((1 + 0.2 * numpy.cos(theta)) * numpy.sin(rho))
                z = 0.5 * float(numpy.sin(theta))
                glVertex3f(x, y, z)
        glEnd()

def redraw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    create_object(COUNT_LAYERS, COUNT_ANGLES)
    pygame.display.flip()
    pygame.time.wait(time)


def change_colors():
    new_last_color = colors[0]
    for index in range(1, len(colors)):
        colors[index - 1] = colors[index]

    colors[len(colors) - 1] = new_last_color


def resize(flag, z):
    if flag:
        z += 10
    else:
        z -= 10
    return z


def main():
    generate_colors(COUNT_LAYERS)

    pygame.init()
    display = (1400, 900)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)

    if PERSPECTIVE == 1:
        gluPerspective(45, (display[0]/display[1]), 1, 200)
        glTranslatef(0.0, 0.0, -5)
    else:
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-5, 5, -5, 5, -1.5, 0)

    change_color_timer = 0

    rescale_timer = 0
    current_z = MAX_Z
    rescale_flag = True

    stop_flag = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_WHEELUP:
                    glScalef(2, 2, 2)
                elif event.button == pygame.BUTTON_WHEELDOWN:
                    glScalef(0.5, 0.5, 0.5)
                else:
                    stop_flag = not stop_flag
            if event.type == pygame.MOUSEMOTION and not stop_flag:
                x = event.rel[1]
                y = event.rel[0]
                glRotate(10, numpy.sign(x), numpy.sign(y), 0)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            glTranslatef(-1, 0, 0)
        if keys[pygame.K_d]:
            glTranslatef(1, 0, 0)
        if keys[pygame.K_w]:
            glTranslatef(0, 0, 1)
        if keys[pygame.K_s]:
            glTranslate(0, 0, -1)
        if keys[pygame.K_LSHIFT]:
            glTranslate(0, 1, 0)
        if keys[pygame.K_LCTRL]:
            glTranslate(0, -1, 0)

        change_color_timer += time
        if change_color_timer > 100:
            change_colors()
            change_color_timer = 0

        rescale_timer += 10

        if rescale_timer == 100:
            if current_z == MAX_Z:
                rescale_flag = False
            elif current_z == MIN_Z:
                rescale_flag = True

            current_z = resize(rescale_flag, current_z)
            rescale_timer = 0

            if rescale_flag:
                glScalef(1.2, 1.2, 1.2)
            else:
                glScalef(0.8, 0.8, 0.8)

        redraw()

main()
