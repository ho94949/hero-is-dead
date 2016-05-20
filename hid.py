# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import weakref

from pyglet.window import key
from pyglet.window import mouse
from pyglet import gl

import cocos
from cocos.director import director
import cocos.collision_model as cm
import cocos.euclid as eu

fe = 1.0e-4

consts = {
    "window": {
        "width": 640,
        "height": 480,
        "vsync": True,
        "resizable": True
    },
    "world": {
        "width": 1200,
        "height": 1000,
        "rPlayer": 8.0,
    },
    "edit": {
        "bindings": {
            key.LEFT: 'left',
            key.RIGHT: 'right',
            key.UP: 'up',
            key.DOWN: 'down',
            key.NUM_ADD: 'zoomin',
            key.NUM_SUBTRACT: 'zoomout'
        },
        "mod_modify_selection": key.MOD_SHIFT,
        "mod_restricted_mov": key.MOD_ACCEL,
        "fastness": 160.0,
        "autoscroll_border": 20.0,  # in pixels, float; None disables autoscroll
        "autoscroll_fastness": 320.0,
        "wheel_multiplier": 2.5,
        "zoom_min": 0.1,
        "zoom_max": 2.0,
        "zoom_fastness": 1.0
    },
    "view": {
        # size visible area, measured in world
        'width': 400,
        'height': 300,
        # as the font file is not provided it will decay to the default font;
        # the setting is retained anyway to not downgrade the code
        "font_name": 'Axaxax',
        "palette": {
            'bg': (0, 65, 133),
            'player': (237, 27, 36),
            'wall': (247, 148, 29),
            'gate': (140, 198, 62),
            'food': (140, 198, 62)
        }
    }
}

class Actor(cocos.sprite.Sprite):
    colors = [(255, 255, 255), (0, 80, 0)]

    def __init__(self):
        super(Actor, self).__init__('ball32.png')
        self._selected = True
        radius = self.image.width / 2.0
        assert abs(radius - 16.0) < fe
        self.cshape = cm.CircleShape(eu.Vector2(0.0, 0.0), radius)
#        self.cshape = cm.AARectShape(eu.Vector2(0.0, 0.0), radius, radius)

    def update_position(self, new_position):
        self.position = new_position
        self.cshape.center = new_position

    def set_selected(self, value):
        self._set_selected = value
        self.color = Actor.colors[1 if value else 0]

class EditLayer(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self, worldview,
                 bindings=None, fastness=None, autoscroll_border=10,
                 autoscroll_fastness=None, wheel_multiplier=None,
                 zoom_min=None, zoom_max=None, zoom_fastness=None,
                 mod_modify_selection=None, mod_restricted_mov=None):
        super(EditLayer, self).__init__()

        self.bindings = bindings
        buttons = {}
        modifiers = {}
        for k in bindings:
            buttons[bindings[k]] = 0
            modifiers[bindings[k]] = 0
        self.buttons = buttons
        self.modifiers = modifiers

        self.fastness = fastness
        self.autoscroll_border = autoscroll_border
        self.autoscroll_fastness = autoscroll_fastness
        self.wheel_multiplier = wheel_multiplier
        self.zoom_min = zoom_min
        self.zoom_max = zoom_max
        self.zoom_fastness = zoom_fastness
        self.mod_modify_selection = mod_modify_selection
        self.mod_restricted_mov = mod_restricted_mov

        self.weak_worldview = weakref.ref(worldview)
        self.wwidth = worldview.width
        self.wheight = worldview.height

        self.autoscrolling = False
        self.drag_selecting = False
        self.drag_moving = False
        self.restricted_mov = False
        self.wheel = 0
        self.dragging = False
        self.keyscrolling = False
        self.keyscrolling_descriptor = (0, 0)
        self.wdrag_start_point = (0, 0)
        self.elastic_box = None
        self.selection = {}

        # opers that change cshape must ensure it goes to False,
        # selection opers must ensure it goes to True
        self.selection_in_collman = True
        #? Hardcoded here, should be obtained from level properties or calc
        # from available actors or current actors in worldview
        gsize = 32 * 1.25
        self.collman = cm.CollisionManagerGrid(-gsize, self.wwidth + gsize,
                                               -gsize, self.wheight + gsize,
                                               gsize, gsize)
        for actor in worldview.actors:
            self.collman.add(actor)

        self.schedule(self.update)

    def on_enter(self):
        super(EditLayer, self).on_enter()
        scene = self.get_ancestor(cocos.scene.Scene)
        if self.elastic_box is None:
            self.elastic_box = MinMaxRect()
            scene.add(self.elastic_box, z=10)
            self.mouse_mark = ProbeQuad(4, (0, 0, 0, 255))
            scene.add(self.mouse_mark, z=11)

    def update(self, dt):
        pass

class ColorRect(cocos.cocosnode.CocosNode):

    def __init__(self, width, height, color4):
        super(ColorRect, self).__init__()
        self.color4 = color4
        w2 = int(width / 2)
        h2 = int(height / 2)
        self.vertexes = [(0, 0, 0), (0, height, 0), (width, height, 0), (width, 0, 0)]

    def draw(self):
        gl.glPushMatrix()
        self.transform()
        gl.glBegin(gl.GL_QUADS)
        gl.glColor4ub(*self.color4)
        for v in self.vertexes:
            gl.glVertex3i(*v)
        gl.glEnd()
        gl.glPopMatrix()


class ProbeQuad(cocos.cocosnode.CocosNode):

    def __init__(self, r, color4):
        super(ProbeQuad, self).__init__()
        self.color4 = color4
        self.vertexes = [(r, 0, 0), (0, r, 0), (-r, 0, 0), (0, -r, 0)]

    def draw(self):
        gl.glPushMatrix()
        self.transform()
        gl.glBegin(gl.GL_QUADS)
        gl.glColor4ub(*self.color4)
        for v in self.vertexes:
            gl.glVertex3i(*v)
        gl.glEnd()
        gl.glPopMatrix()


class MinMaxRect(cocos.cocosnode.CocosNode):

    """ WARN: it is not a real CocosNode, it pays no attention to position,
        rotation, etc. It only draws the quad depicted by the vertexes.
        In other worlds, a nasty hack that gets the work done and you
        should not take as example"""

    def __init__(self):
        super(MinMaxRect, self).__init__()
        self.color3 = (0, 0, 255)
        self.vertexes = [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0)]
        self.visible = False

    def adjust_from_w_minmax(self, wminx, wmaxx, wminy, wmaxy):
        # asumes world to screen preserves order
        sminx, sminy = world_to_screen(wminx, wminy)
        smaxx, smaxy = world_to_screen(wmaxx, wmaxy)
        self.vertexes = [(sminx, sminy), (sminx, smaxy), (smaxx, smaxy), (smaxx, sminy)]

    def draw(self):
        if not self.visible:
            return
        gl.glLineWidth(2)  # deprecated
        gl.glColor3ub(*self.color3)
        gl.glBegin(gl.GL_LINE_STRIP)
        for v in self.vertexes:
            gl.glVertex2f(*v)
        gl.glVertex2f(*self.vertexes[0])
        gl.glEnd()

    def set_vertexes_from_minmax(self, minx, maxx, miny, maxy):
        self.vertexes = [(minx, miny), (minx, maxy), (maxx, maxy), (maxx, miny)]


class Worldview(cocos.layer.ScrollableLayer):
    is_event_handler = True

    def __init__(self, width=None, height=None, rPlayer=None):
        super(Worldview, self).__init__()
        self.width = width
        self.height = height
        self.px_width = width
        self.px_height = height

        # background
        self.add(ColorRect(width, height, (0, 0, 255, 255)), z=-2)
        border_size = 10
        inner = ColorRect(width - 2 * border_size, height - 2 * border_size, (255, 0, 0, 255))
        inner.position = (border_size, border_size)
        self.add(inner, z=-1)

        # actors
        use_batch = True
        if use_batch:
            self.batch = cocos.batch.BatchNode()
            self.add(self.batch)
        self.actors = []
        m = height / width
        i = 0
        for x in range(0, int(width), int(4 * rPlayer)):
            y = m * x
            actor = Actor()
            actor.update_position(eu.Vector2(float(x), float(y)))
            if use_batch:
                self.batch.add(actor, z=i)
            else:
                self.add(actor, z=i)
            self.actors.append(actor)
            i += 1

    def on_enter(self):
        super(Worldview, self).on_enter()

director.init(**consts["window"])
scene = cocos.scene.Scene()
playview = Worldview(**consts['world'])
#editor = EditLayer(scrolling_manager, playview, **consts['edit'])
editor = EditLayer(playview, **consts['edit'])
scene.add(editor)
director.run(scene)
