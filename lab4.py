import os
import random
from pygame import *

from PIL import Image
from OpenGL.GL import *
from OpenGL.GLU import *
import OpenGL.GL.shaders

import pygame
import numpy
import pyrr

vertex_shader = """
#version 430
in layout(location = 0) vec3 position;
in layout(location = 1) vec2 textureCoords;
uniform mat4 transform;
out vec3 newPosition;
out vec2 newTexture;
out vec3 fragNormal;
void main()
{   
    newPosition = position;
    fragNormal = vec4(position.x * 2, position.y * 2, position.z * 2, 0.0).xyz;
    gl_Position = transform * vec4(newPosition, 1.0f);
    newTexture = textureCoords;
}
"""

fragment_shader = """
#version 430
in vec3 newPosition;
in vec2 newTexture;
in vec3 fragNormal;

out vec4 outColor;
uniform sampler2D samplerTexture;
void main()
{
    vec4 texel = texture(samplerTexture, newTexture) ;
    
    float x = newPosition.x;
    float y = newPosition.y;
    
    bool inRad = pow(x,2) + pow(y,2) < 0.3;
    
    //Отверстие в торе
    if(inRad){
        discard;
    } else {
        outColor = texel;
    }
    
    vec3 ambientLightIntensity = vec3(0.3, 0.2, 0.4);
    vec3 sunLightIntensity = vec3(0.9, 0.9, 0.9);
    vec3 highLightDirection = normalize(vec3(-2.0, -2.0, 0.0));
    vec3 bottomLightDirection = normalize(vec3(2.0, 2.0, 0.0));
    
    vec3 lightIntensity = ambientLightIntensity + sunLightIntensity * max(dot(fragNormal, highLightDirection), 0.0) + sunLightIntensity * max(dot(fragNormal, bottomLightDirection), 0.0);
    
    outColor = vec4(outColor.rgb * lightIntensity, outColor.a);
}
"""

interval = 10

MAX_Z = -10
MIN_Z = -100

ANGLES_COUNT = int(os.environ.get('LAYERS_COUNT', 20))
LAYERS_COUNT = int(os.environ.get('ANGLES_COUNT', 20))


def get_random_color():
    return [round(random.random(), 2), round(random.random(), 2), round(random.random(), 2)]


def change_color(torus):
    len_torus = len(torus)
    last_color = torus[len(torus) - 3: len(torus) + 1].copy()

    colors = []

    for color_num in range(3, len_torus, 6):
        current_color = torus[color_num: color_num + 3].copy()
        torus[color_num: color_num + 3] = last_color
        last_color = current_color
        colors.append(last_color)

    return numpy.array(torus, dtype=numpy.float32)


def init_object(layers_count, angles_count):
    double_pi = 2 * numpy.pi
    torus = []
    indices = []
    last_index = 0

    num_vertices = (layers_count + 1) * (angles_count + 1)
    primitive_restart_index = num_vertices

    main_segment_angle_step = double_pi / float(layers_count)
    tube_segment_angle_step = double_pi / float(angles_count)

    main_segment_texture_step = 2 / float(layers_count)
    tube_segment_texture_step = 1 / float(angles_count)

    current_main_segment_angle = 0.0

    current_main_segment_texture_coord = 0.0

    for i in range(0, layers_count + 1):
        layer_color = get_random_color()

        sin_main_segment = numpy.sin(current_main_segment_angle)
        cos_main_segment = numpy.cos(current_main_segment_angle)
        current_tube_segment_angle = 0.0

        current_tube_segment_texture_coord = 0.0
        for j in range(0, angles_count + 1):
            sin_tube_segment = numpy.sin(current_tube_segment_angle)
            cos_tube_segment = numpy.cos(current_tube_segment_angle)

            x = float((0.5 + 0.3 * cos_tube_segment) * cos_main_segment)
            y = float((0.5 + 0.3 * cos_tube_segment) * sin_main_segment)
            z = float(0.3 * sin_tube_segment)

            vertex = [x, y, z]
            vertex.extend(layer_color)
            vertex.extend([current_tube_segment_texture_coord,
                          current_main_segment_texture_coord])
            torus.extend(vertex)

            current_tube_segment_texture_coord += tube_segment_texture_step
            current_tube_segment_angle += tube_segment_angle_step

        current_main_segment_angle += main_segment_angle_step
        current_main_segment_texture_coord += main_segment_texture_step

    current_vertex_offset = 0
    for i in range(0, layers_count + 1):
        for j in range(0, angles_count + 1):
            indices.append(current_vertex_offset)
            indices.append(current_vertex_offset + angles_count + 1)
            current_vertex_offset += 1
            # indices.append(current_vertex_offset - 1)

        if i != layers_count - 1:
            indices.append(primitive_restart_index)

    return torus, indices


def main():
    pygame.init()
    display = (1400, 900)
    pygame.display.set_mode(display, OPENGL | DOUBLEBUF)

    torus, indices = init_object(LAYERS_COUNT, ANGLES_COUNT)

    shader = OpenGL.GL.shaders.compileProgram(OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
                                              OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))

    torus = numpy.array(torus, dtype=numpy.float32)
    vertex_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)
    glBufferData(GL_ARRAY_BUFFER, len(torus) * torus.itemsize, torus, GL_STREAM_DRAW)

    indices = numpy.array(indices, dtype=numpy.uint32)
    indices_buffer = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, indices_buffer)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * indices.itemsize, indices, GL_STREAM_DRAW)

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, torus.itemsize * 8, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, torus.itemsize, ctypes.c_void_p(12))
    glEnableVertexAttribArray(1)


    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    #
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    image = Image.open("79027192-abstract-nature-marble-plastic-stony-mosaic-tiles-texture-background-with-green-grout-emerald-and-pu.jpg")
    img_data = numpy.array(list(image.getdata()), numpy.uint8)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    glEnable(GL_TEXTURE_2D)

    glUseProgram(shader)

    glEnable(GL_DEPTH_TEST)

    gluPerspective(45, (display[0] / display[1]), 1, 200)
    glTranslatef(0.0, 0.0, -5)

    value = 0
    stop_flag = False

    rand_result = random.randint(0, 1)
    change_color_interval = 0

    while True:
        # torus = change_color(torus)

        change_color_interval += 10
        value += 0.1
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if not stop_flag:
            affin = pyrr.Matrix44.from_x_rotation(-10 * numpy.pi / 180 * value)
            affin *= pyrr.Matrix44.from_y_rotation(-20 * numpy.pi / 180 * value)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == pygame.BUTTON_WHEELUP:
                    affin *= pyrr.Matrix44.from_scale([2, 2, 2])
                elif event.button == pygame.BUTTON_WHEELDOWN:
                    affin *= pyrr.Matrix44.from_scale([0.5, 0.5, 0.5])
                else:
                    stop_flag = not stop_flag
            if event.type == pygame.MOUSEMOTION and not stop_flag:
                x = event.rel[1]
                y = event.rel[0]
                affin *= pyrr.Matrix44.from_x_rotation(10 * numpy.sign(x))
                affin *= pyrr.Matrix44.from_y_rotation(10 * numpy.sign(y))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            affin *= pyrr.Matrix44.from_translation([-1, 0, 0])
        if keys[pygame.K_d]:
            affin *= pyrr.Matrix44.from_translation([1, 0, 0])
        if keys[pygame.K_w]:
            affin *= pyrr.Matrix44.from_translation([0, 0, 1])
        if keys[pygame.K_s]:
            affin *= pyrr.Matrix44.from_translation([0, 0, -1])
        if keys[pygame.K_LSHIFT]:
            affin *= pyrr.Matrix44.from_translation([0, 1, 0])
        if keys[pygame.K_LCTRL]:
            affin *= pyrr.Matrix44.from_translation([0, -1, 0])

        if change_color_interval == 400:
            change_color_interval = 0
            if rand_result == 1:
                rand_result = 0
            else:
                rand_result = 1

        transform_loc = glGetUniformLocation(shader, "transform")
        glUniformMatrix4fv(transform_loc, 1, GL_FALSE, affin)
        glDrawElements(GL_TRIANGLE_STRIP, len(indices), GL_UNSIGNED_INT, None)
        pygame.display.flip()
        pygame.time.wait(10)


if __name__ == '__main__':
    main()
