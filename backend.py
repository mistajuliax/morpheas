from bgl import *
from .PIL import Image
from .. import pylivecoding
import numpy,pdb

class MOpenGLCanvas(pylivecoding.LiveObject):
    instances = []
    def __init__(self,world):
        super().__init__()
        self.world = world
        self.openGLversion = 3.3
        self.vertices_list = []
        self.needs_to_update_vertices_list = False
        self.initialised_OpenGL_context = False
        self.success_pointer = None
        self.void_pointer = None
        self.VAO_pointer = None
        self.VBO_pointer = None
        self.vertex_shader = None
        self.vertex_shader_source = None
        self.fragment_shader = None
        self.fragment_shader_source = None
        self.vertices = []
        self.shader_program = None




    def draw(self):
        #print("ok maybe it does not")
        if self.needs_to_update_vertices_list:
            self.vertices_list = []
            self.generate_vertices_list()
        if not self.initialised_OpenGL_context:
            self.initialise_OpenGL_context()

        glUseProgram(self.shader_program)
        glBindVertexArray(self.VAO_pointer.to_list()[0])
        glClearColor(0.0, 0.0, 0.4, 0.0)
        glDrawArrays(GL_TRIANGLES, 0, 3)
        # if self.openGLversion < 1.9:
        #     if not texture['is_gl_initialised']:
        #         self.initialise_texture(texture)
        #     else:
        #         glBindTexture(bgl.GL_TEXTURE_2D, texture['texture_id'].to_list()[0])


            #self.clean_up()
    def initialise_OpenGL_context(self):
        print("initialising OpenGL context")
        self.vertices = [-0.5,-0.5,0.0,
                    0.5,-0.5,0.0,
                    0.0,0.5,0.0]
        vertices_pointer = Buffer(GL_FLOAT,[len(self.vertices)],self.vertices)

        #initialise VAO
        self.VAO_pointer = Buffer(GL_INT, [1])
        glGenVertexArrays(1, self.VAO_pointer)
        glBindVertexArray(self.VAO_pointer.to_list()[0])

        #initialise VBO
        self.VBO_pointer = Buffer(GL_INT,[1])
        glGenBuffers(1,self.VBO_pointer)
        glBindBuffer(GL_ARRAY_BUFFER,self.VBO_pointer.to_list()[0])
        glBufferData(GL_ARRAY_BUFFER,len(self.vertices),vertices_pointer, GL_STATIC_DRAW)
        self.void_pointer = Buffer(GL_INT,[1])
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, self.void_pointer)
        glEnableVertexAttribArray(0)
        print("initialising vertext shader")
        #vertex shader
        self.vertex_shader_source= " # version 330 core \nlayout(location=0) in vec3 aPos; \nvoid main()\n{\n" \
                              "gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);\n}"
        print("vertex shader source : ",self.vertex_shader_source)
        self.vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(self.vertex_shader,self.vertex_shader_source)
        glCompileShader(self.vertex_shader)
        self.success_pointer = Buffer(GL_INT,[1])
        infolog=[]
        glGetShaderiv(self.vertex_shader,GL_COMPILE_STATUS, self.success_pointer)
        if not self.success_pointer.to_list()[0]:
            glGetShaderInfoLog(self.vertex_shader, 512, 0, infolog)
            print("vertex shader error log:",infolog)


        #fragment shadert
        print("intialising fragment shader")
        self.fragment_shader_source = "#version 330 core\n out vec4 FragColor; \n void main()\n{\n FragColor = vec4(" \
                                   "1.0f, " \
                                 "0.0f, 0.0f, 0.2f);\n }\n "
        print("fragment shader source : ",self.fragment_shader_source )
        self.fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(self.fragment_shader,self.fragment_shader_source)
        glCompileShader(self.fragment_shader)
        glGetShaderiv(self.fragment_shader, GL_COMPILE_STATUS, self.success_pointer)
        if not self.success_pointer.to_list()[0]:
            glGetShaderInfoLog(self.fragment_shader, 512, 0, infolog)
            #print("fragment shader error log:", infolog)

        #shader program
        print("initialsing shader program")
        self.shader_program = glCreateProgram()
        glAttachShader(self.shader_program, self.vertex_shader)
        glAttachShader(self.shader_program, self.fragment_shader)
        glLinkProgram(self.shader_program)
        glGetProgramiv(self.shader_program,GL_LINK_STATUS,self.success_pointer)
        if not self.success_pointer.to_list()[0]:
            glGetProgramInfoLog(self.shader_program, 512, 0, infolog)
            print("fragment shader error log:", infolog)

        err = 1
        while err is not GL_NO_ERROR :
            print("new OpenGL error : ",err)
            err = glGetError()
        self.initialised_OpenGL_context = True

        return
    def generate_vertices_list(self, morph_target= None):

        if morph_target is None or morph_target is self.world:
            # world bounds in screen coordinates
            morph_target=self.world
            px1 = self.world.draw_area_position[0]
            py1 = self.world.draw_area_position[1]
            px2 = self.world.draw_area_position[0]+self.world.width
            py2 = self.world.draw_area_position[1]+self.world.height
        else:
            # parent bounds in screen coordinates
            px1 = morph_target.parent.absolute_position[0]
            py1 = morph_target.parent.absolute_position[1]
            px2 = morph_target.parent.absolute_position[0] + morph_target.parent.width
            py2 = morph_target.parent.absolute_position[1] + morph_target.parent.height


        # morph bounds in screen coordinates (bottom left and top right corners)
        mx1 = morph_target.absolute_position[0]
        mx2 = morph_target.absolute_position[0] + morph_target.width
        my1 = morph_target.absolute_position[1]
        my2 = morph_target.absolute_position[0] + morph_target.height

        # morph bounds in OpenGL coordinates for vertices and textures
        # bottom left vertice
        mxv1 = self.convert_pixels_to_world_coordinates(mx1,px1,px2)
        myv1 = self.convert_pixels_to_world_coordinates(my1, py1, py2)
        mxt1= self.calculate_texture_clipping(mx1,morph_target.width,px1,px2)
        myt1= self.calculate_texture_clipping(my1,morph_target.height,py1,py2)

        # bottom right vertice
        mxv2 =  self.convert_pixels_to_world_coordinates(mx2,px1,px2)
        myv2 = myv1
        mxt2 = self.calculate_texture_clipping(mx2,morph_target.width,px1,px2)
        myt2 = myt1

        # top right vertice
        mxv3 = mxv2
        myv3 = self.convert_pixels_to_world_coordinates(my2,py1,py2)
        mxt3 = mxt2
        myt3 = self.calculate_texture_clipping(my2,morph_target.height,px1,px2)

        # top left vertice
        mxv4 = mxv1
        myv4 = myv3
        mxt4 = mxt1
        myt4 = myt2

        #colors
        r = morph_target.color[0]
        g = morph_target.color[1]
        b = morph_target.color[2]
        alpha = morph_target.color[3]

        # append them to the vertices_list
        vl = [ mxv1, myv1, 0.0, r,g,b, mxt1,myt1,
               mxv2, myv2, 0.0, r, g, b, mxt2, myt2,
               mxv3, myv3, 0.0, r, g, b, mxt3, myt3,
               mxv4, myv4, 0.0, r, g, b, mxt4, myt4]
        indices = [0,1,2, #first triamgle and then second
                   0,2,3]

        for morph in morph_target:
            if morph.can_draw:
                self.generate_vertices_list(morph)

    # texture of a morph will be clipped by the boundaries of the world or its parent morph
    def calculate_texture_clipping(self,value, value_width, min_value,max_value):
        # limit value to its range (min_value <--> max_value)
        lv = float(max(min(value, max_value), min_value))
        if value < min_value:
            return (lv-value)/value_width
        if value > max_value:
            return 1-((value - lv)/value_width)




    def convert_pixels_to_world_coordinates(self,value,min_value,max_value):

        center_value = ((max_value - min_value)/2)+min_value

        # limit value to its range (min_value <--> max_value)
        lv = float(max(min(value, max_value), min_value))

        half_width = center_value - min_value
        return float((lv - half_width)/half_width)

    def draw_quad_face(self,x,y,color):

        glColor4f(*color)

        # draw a simple rectangle with the dimensions, position and scale of the Morph
        # use the active texture as texture of the rectangle
        glEnable(GL_BLEND)
        glEnable(GL_TEXTURE_2D)
        glBegin(bgl.GL_QUADS)
        glTexCoord2f(0, 1)
        glVertex2f(x, y)
        glTexCoord2f(1, 1)
        glVertex2f((x + width), ys)
        glTexCoord2f(1, 0)
        glVertex2f((x + width), (y + height))
        glTexCoord2f(0, 0)
        glVertex2f(x, (y + height))

    def clean_up(self):
        if self.openGLversion <1.9:
            # restore OpenGL context to avoide any conflicts
            glEnd()
            glDisable(bgl.GL_TEXTURE_2D)
            glDisable(bgl.GL_BLEND)

    def initialise_texture(self,texture):
        texture.texture_id = Buffer(bgl.GL_INT, [1])
        glGenTextures(1, texture.texture_id)
        glBindTexture(GL_TEXTURE_2D, texture.texture_id.to_list()[0])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, texture.width, texture.height, 0,
                         GL_RGBA, GL_FLOAT, texture.data)
        bgl.glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        bgl.glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        texture.is_gl_initialised = True
        return texture 

    class MOpenGLTexture:
        textures_list = []
        search_path = ""

        def __init__(self):
            self.data = []
            self.name = []
            self.is_gl_initialized = []
            self.height = 100
            self.width = 100
            self.gl_coordinates = [0.0,0.0,0.0,0.0]
            self.gl_texture_id
            self.path = ""
            self.scale = 1
            self.id = 0

        def load_texture(self, name, scale=1):
            # detect the current location of the addon using Morpheas
            current_path = __file__[0:-11]
            bpy.path.basename(current_path)

            # create the full path of the texture to be loaded and load it
            full_path = current_path + __class__.search_path + name + '.png'
            im = Image.open(full_path)
            data = numpy.array(im)
            data = data.astype(float)
            data = numpy.divide(data, 255.0)
            content = numpy.array(data).reshape(im.size[1], im.size[0] * 4)
            buf = bgl.Buffer(bgl.GL_FLOAT, [len(content), len(content[0])], content)

            # a Morph can have multiple textures if it is needed, the information
            # about those textures are fetched directly from the PNG file
            self.texture.name = name
            self.width=im.size[0]
            self.height=im.size[1]
            self.path=full_path
            self.data= buf
            self.is_gl_initialised= False
            self.scale =scale
            self.id= 0

            return self
        