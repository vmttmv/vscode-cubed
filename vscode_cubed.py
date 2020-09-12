import os
import sys
import time
import glfw
import numpy
import pyrr
import pyautogui
import Xlib.display

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from easyprocess import EasyProcess
from pyvirtualdisplay.smartdisplay import SmartDisplay

vertex_src = """
    #version 330 core
    layout(location = 0) in vec3 pos;
    layout(location = 1) in vec2 uv;
    out vec2 uv_out;
    uniform mat4 u_rot;
    uniform vec3 u_scale;
    void main() {
        uv_out = uv;
        gl_Position = u_rot * vec4(pos * u_scale, 1.0);
    }
"""

frag_src = """
    #version 330 core
    in vec2 uv_out;
    layout(location = 0) out vec4 frag_color;
    uniform sampler2D u_tex;
    void main() {
        frag_color = texture(u_tex, uv_out);
    }
"""

vertices = [-0.5, 0.5, -0.5, 0.0, 0.0,
            -0.5, -0.5, -0.5, 0.0, 1.0,
            0.5, -0.5, -0.5, 1.0, 1.0,
            0.5,  0.5, -0.5, 1.0, 0.0,

            -0.5, 0.5, 0.5, 0.0, 1.0,
            -0.5, -0.5, 0.5, 0.0, 0.0,
            0.5, -0.5, 0.5, 1.0, 0.0,
            0.5,  0.5, 0.5, 1.0, 1.0,

            0.5, 0.5, -0.5, 0.0, 0.0,
            0.5, -0.5, -0.5, 0.0, 1.0,
            0.5, -0.5, 0.5, 1.0, 1.0,
            0.5, 0.5, 0.5, 1.0, 0.0,

            -0.5, 0.5, -0.5, 0.0, 0.0,
            -0.5, -0.5, -0.5, 0.0, 1.0,
            -0.5, -0.5, 0.5, 1.0, 1.0,
            -0.5, 0.5, 0.5, 1.0, 0.0,

            -0.5, 0.5, 0.5, 0.0, 0.0,
            -0.5, 0.5, -0.5, 0.0, 1.0,
            0.5, 0.5, -0.5, 1.0, 1.0,
            0.5, 0.5, 0.5, 1.0, 0.0,

            -0.5, -0.5, 0.5, 0.0, 0.0,
            -0.5, -0.5, -0.5, 0.0, 1.0,
            0.5, -0.5, -0.5, 1.0, 1.0,
            0.5, -0.5, 0.5, 1.0, 0.0]

indices = [0,  1,  3,  3,  1,  2,
           4,  5,  7,  7,  5,  6,
           8,  9, 11, 11, 9,  10,
          12, 13, 15, 15, 13, 14,
          16, 17, 19, 19, 17, 18,
          20, 21, 23, 23, 21, 22]

def on_char(window, c):
    pyautogui.write(chr(c))

def on_key(window, key, scancode, action, mods):
    if action == glfw.PRESS:
        if key == glfw.KEY_BACKSPACE:
            pyautogui.keyDown('backspace')
        elif key == glfw.KEY_ENTER:
            pyautogui.keyDown('enter')
        elif key == glfw.KEY_LEFT_CONTROL or key == glfw.KEY_RIGHT_CONTROL:
            pyautogui.keyDown('ctrl')
        elif key == glfw.KEY_LEFT_SHIFT or key == glfw.KEY_RIGHT_SHIFT:
            pyautogui.keyDown('shift')
        elif key == glfw.KEY_LEFT_ALT or key == glfw.KEY_RIGHT_ALT:
            pyautogui.keyDown('alt')
        elif key == glfw.KEY_UP:
            pyautogui.keyDown('up')
        elif key == glfw.KEY_DOWN:
            pyautogui.keyDown('down')
        elif key == glfw.KEY_LEFT:
            pyautogui.keyDown('left')
        elif key == glfw.KEY_RIGHT:
            pyautogui.keyDown('right')
    elif action == glfw.RELEASE:
        if key == glfw.KEY_BACKSPACE:
            pyautogui.keyUp('backspace')
        elif key == glfw.KEY_ENTER:
            pyautogui.keyUp('enter')
        elif key == glfw.KEY_LEFT_CONTROL or key == glfw.KEY_RIGHT_CONTROL:
            pyautogui.keyUp('ctrl')
        elif key == glfw.KEY_LEFT_SHIFT or key == glfw.KEY_RIGHT_SHIFT:
            pyautogui.keyUp('shift')
        elif key == glfw.KEY_LEFT_ALT or key == glfw.KEY_RIGHT_ALT:
            pyautogui.keyUp('alt')
        elif key == glfw.KEY_UP:
            pyautogui.keyUp('up')
        elif key == glfw.KEY_DOWN:
            pyautogui.keyUp('down')
        elif key == glfw.KEY_LEFT:
            pyautogui.keyUp('left')
        elif key == glfw.KEY_RIGHT:
            pyautogui.keyUp('right')

if not glfw.init():
    raise Exception("glfw init failed")

glfw.window_hint(glfw.DEPTH_BITS, 24)
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

window = glfw.create_window(1600, 900, "vscode^3", None, None)
if not window:
    glfw.terminate()
    raise Exception("failed to create a window")

glfw.set_char_callback(window, on_char)
glfw.set_key_callback(window, on_key)

glfw.make_context_current(window)

vao = glGenVertexArrays(1)
glBindVertexArray(vao)

vertices = numpy.array(vertices, dtype=numpy.float32)
indices = numpy.array(indices, dtype=numpy.uint32)

vbo = glGenBuffers(1)
glBindBuffer(GL_ARRAY_BUFFER, vbo)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

ibo = glGenBuffers(1)
glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo)
glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

glEnableVertexAttribArray(0)
glEnableVertexAttribArray(1)
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, vertices.itemsize*5, ctypes.c_void_p(0))
glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, vertices.itemsize*5, ctypes.c_void_p(12))

program = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(frag_src, GL_FRAGMENT_SHADER))
glUseProgram(program); 
rot_loc = glGetUniformLocation(program, "u_rot")
scale_loc = glGetUniformLocation(program, "u_scale")

texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

glEnable(GL_DEPTH_TEST)

file = ""
if len(sys.argv) > 1:
    file = sys.argv[1]

with SmartDisplay(backend="xvfb", size=(1920, 1080)) as disp:
    pyautogui.FAILSAFE = False
    pyautogui._pyautogui_x11._display = Xlib.display.Display(os.environ['DISPLAY'])
    with EasyProcess(["code", "-r", file]):
        rot_x = 0
        rot_y = 0
        last_frame = glfw.get_time()
        while not glfw.window_should_close(window):
            now = glfw.get_time()
            dt = now - last_frame
            last_frame = now

            img = disp.waitgrab()
            img_data = img.tobytes()
            img.save("foo.png")
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

            glClearColor(0, 0, 0, 1)
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

            width, height = glfw.get_framebuffer_size(window);
            glViewport(0, 0, width, height)

            rot_x = rot_x + dt
            rot_y = rot_y + dt
            mx = pyrr.Matrix44.from_x_rotation(rot_x)
            my = pyrr.Matrix44.from_y_rotation(rot_y)
            glUniformMatrix4fv(rot_loc, 1, GL_FALSE, pyrr.matrix44.multiply(mx, my))
            glUniform3f(scale_loc, 1, 1, 1)

            glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, None)

            glfw.swap_buffers(window)
            glfw.poll_events()

glfw.terminate()
