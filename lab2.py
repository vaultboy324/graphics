import os
import random
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders

import numpy

interval = 10

MAX_Z = -10
MIN_Z = -100

LAYERS_COUNT = int(os.environ.get('LAYERS_COUNT', 5))
ANGLES_COUNT = int(os.environ.get('ANGLES_COUNT', 100))

PERSPECTIVE = int(os.environ.get('PERSPECTIVE', 1))

DIRECTED_FIRST = GL_LIGHT0
DIRECTED_SECOND = GL_LIGHT1

POINTED_FIRST = GL_LIGHT2
POINTED_SECOND = GL_LIGHT3

POINTED_FIRST_START_Y = -1.0
POINTED_SECOND_START_X = 1.0


def create_object(layers_count, angles_count):
    double_pi = 2 * numpy.pi
    for i in range(0, layers_count):
        glBegin(GL_QUAD_STRIP)
        for j in range(0, angles_count + 1):
            for k in range(2, 0, -1):
                s = (i + k) % layers_count + 0.5
                t = j % (angles_count + 1)

                theta = s * double_pi / layers_count
                rho = t * double_pi / angles_count

                x = float((1 + 0.2 * numpy.cos(theta)) * numpy.cos(rho))
                y = float((1 + 0.2 * numpy.cos(theta)) * numpy.sin(rho))
                z = 0.5 * float(numpy.sin(theta))

                glNormal3f(x, y, z)
                glVertex3f(x, y, z)
        glEnd()


def redraw():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    create_object(LAYERS_COUNT, ANGLES_COUNT)
    pygame.display.flip()
    pygame.time.wait(interval)


def resize(flag, z):
    if flag:
        z += 10
    else:
        z -= 10
    return z


def init_light():
    glEnable(GL_LIGHTING)
    glEnable(GL_AUTO_NORMAL)
    glEnable(GL_NORMALIZE)

    ambient_on()


def ambient_on():
    ambient_color = [0, 255, 255, 1]
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient_color)


def ambient_off():
    ambient_color = (0, 0, 0, 1)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, ambient_color)


def first_directed_on():
    directed_color = [255, 0, 0]
    direction = [1.0, 1.0, 0.0, 0.0]

    glEnable(DIRECTED_FIRST)
    glLightfv(DIRECTED_FIRST, GL_DIFFUSE, directed_color)
    glLightfv(DIRECTED_FIRST, GL_POSITION, direction)


def second_directed_on():
    directed_color = [0, 255, 0]
    direction = [0.0, 0.0, -1.0, 0.0]

    glEnable(DIRECTED_SECOND)
    glLightfv(DIRECTED_SECOND, GL_DIFFUSE, directed_color)
    glLightfv(DIRECTED_SECOND, GL_POSITION, direction)


def first_pointed_on(dy):
    glEnable(POINTED_FIRST)

    change_color_first(5)
    move_pointed_first(dy)


def second_pointed_on(dx):
    glEnable(POINTED_SECOND)
    change_color_second(4)
    move_pointed_second(dx)


def move_pointed_first(dy):
    position = [1.0, POINTED_FIRST_START_Y + dy, 1.0, 1.0]
    glLightfv(POINTED_FIRST, GL_POSITION, position)


def move_pointed_second(dx):
    position = [POINTED_SECOND_START_X + dx, 1.0, 1.0, 1.0]
    glLightfv(POINTED_SECOND, GL_POSITION, position)


def change_color_first(code):
    new_color = []
    if code == 1:
        new_color = [255, 0, 0]
    elif code == 2:
        new_color = [0, 255, 0]
    elif code == 3:
        new_color = [0, 0, 255]
    elif code == 4:
        new_color = [255, 0, 255]
    elif code == 5:
        new_color = [255, 255, 0]

    glLightfv(POINTED_FIRST, GL_DIFFUSE, new_color)


def change_color_second(code):
    new_color = []
    if code == 1:
        new_color = [255, 0, 0]
    elif code == 2:
        new_color = [0, 255, 0]
    elif code == 3:
        new_color = [0, 0, 255]
    elif code == 4:
        new_color = [255, 0, 255]
    elif code == 5:
        new_color = [255, 255, 0]

    glLightfv(POINTED_SECOND, GL_DIFFUSE, new_color)


def first_directed_off():
    glDisable(DIRECTED_FIRST)


def second_directed_off():
    glDisable(DIRECTED_SECOND)


def first_pointed_off():
    glDisable(POINTED_FIRST)


def second_pointed_off():
    glDisable(POINTED_SECOND)


def main():
    pygame.init()
    display = (1400, 900)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    glEnable(GL_DEPTH_TEST)

    init_light()

    gluPerspective(45, (display[0]/display[1]), 1, 200)
    glTranslatef(0.0, 0.0, -5)

    change_color_timer = 0

    rescale_timer = 0
    current_z = MAX_Z
    rescale_flag = True

    stop_flag = False

    ambient_is_on = True
    directed_first_is_on = False
    directed_second_is_on = False
    pointed_first_is_on = False
    pointed_second_is_on = False

    dy = 0
    dx = 0

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
        if keys[pygame.K_SPACE]:
            if ambient_is_on:
                ambient_off()
                ambient_is_on = False
            else:
                ambient_on()
                ambient_is_on = True
        if keys[pygame.K_LCTRL]:
            if directed_first_is_on:
                first_directed_off()
                directed_first_is_on = False
            else:
                first_directed_on()
                directed_first_is_on = True
        if keys[pygame.K_RCTRL]:
            if directed_second_is_on:
                second_directed_off()
                directed_second_is_on = False
            else:
                second_directed_on()
                directed_second_is_on = True
        if keys[pygame.K_LSHIFT]:
            if pointed_first_is_on:
                first_pointed_off()
                pointed_first_is_on = False
            else:
                first_pointed_on(dx)
                pointed_first_is_on = True
        if keys[pygame.K_RSHIFT]:
            if pointed_second_is_on:
                second_pointed_off()
                pointed_second_is_on = False
            else:
                second_pointed_on(dy)
                pointed_second_is_on = True
        if keys[pygame.K_w]:
            # glTranslate(0.0, 1.0, 0.0)
            dy += 1.0
            move_pointed_first(dy)
        if keys[pygame.K_s]:
            # glTranslate(0.0, -1.0, 0.0)
            dy += -1.0
            move_pointed_first(dy)
        if keys[pygame.K_LEFT]:
            # glTranslate(-1.0, 0.0, 0.0)
            dx += -10.0
            move_pointed_second(dx)
        if keys[pygame.K_RIGHT]:
            # glTranslate(1.0, 0.0, 0.0)
            dx += 10.0
            move_pointed_second(dx)
        if keys[pygame.K_1]:
            change_color_first(1)
        if keys[pygame.K_2]:
            change_color_first(2)
        if keys[pygame.K_3]:
            change_color_first(3)
        if keys[pygame.K_4]:
            change_color_first(4)
        if keys[pygame.K_5]:
            change_color_first(5)
        if keys[pygame.K_F1]:
            change_color_second(1)
        if keys[pygame.K_F2]:
            change_color_second(2)
        if keys[pygame.K_F3]:
            change_color_second(3)
        if keys[pygame.K_F4]:
            change_color_second(4)
        if keys[pygame.K_F5]:
            change_color_second(5)

        rescale_timer += 10

        if rescale_timer == 100:
            if current_z == MAX_Z:
                rescale_flag = False
            elif current_z == MIN_Z:
                rescale_flag = True

            current_z = resize(rescale_flag, current_z)
            rescale_timer = 0

        if not stop_flag:
            glRotate(10, 1, 1, 0)

        redraw()


main()
