from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

import cocos
from cocos.director import director

import pyglet

import time
import math
import random

class Idiot(cocos.layer.Layer):
    def __init__(self, x, y):
        super(Idiot, self).__init__()
        self.id = 0
        self.moveable = True
        self.posx = x
        self.posy = y
        self.distance = 0
        self.sprite = cocos.sprite.Sprite('ball32.png')
        self.sprite.position = x, y
        self.add(self.sprite, z = 1)

    def update_position(self, pos, x, y):
        self.posx, self.posy = pos
        self.sprite.position  = pos
        self.distance = math.sqrt(math.pow(self.posx - x, 2) + math.pow(self.posy - y, 2))


class Restaurance(cocos.layer.Layer):
    def __init__(self, x, y):
        super(Restaurance, self).__init__()
        self.id = 1
        self.moveable = True
        self.posx = x
        self.posy = y
        self.distance = 0
        self.sprite = cocos.sprite.Sprite('restaurance.png')
        self.sprite.position = x, y
        self.add(self.sprite, z = 1)

    def update_position(self, pos, x, y):
        self.posx, self.posy = pos
        self.sprite.position  = pos
        self.distance = math.sqrt(math.pow(self.posx - x, 2) + math.pow(self.posy - y, 2))

class MainFrame(cocos.layer.Layer):

    is_event_handler = True

    def __init__(self):
        super(MainFrame, self).__init__()
        self.hos = cocos.sprite.Sprite('hos.png')
        x, y = director.get_window_size()
        self.hos.position = x/2, y/2
        self.add(self.hos, z = 1)
        self.center_x, self.center_y = self.hos.position
        self.idiots = []
        self.restaurances = []
        self.people = []
        self.idiots_count = 0
        self.restaurances_count = 0
        self.people_count = 0
        self.initial_idiots = 10
        self.initial_restaurances = 10
        self.timer = time.time()
        self.is_select = False
        self.p_speed = 100 #suck speed
        self.h_speed = 1000 #rotate speed
        self.click_radius = 1000
        self.storm_radius = 100

        for i in range(self.initial_idiots):
            self.create_idiot()
        for i in range(self.initial_restaurances):
            self.create_restaurance()

        self.timeLabel = cocos.text.Label(str(time.time() - self.timer), font_size=18, x=800, y=700)
        self.add(self.timeLabel)

        #for debugging
        self.mouseLabel = cocos.text.Label('No mouse events yet', font_size=18, x=800, y=660)
        self.add(self.mouseLabel)

        self.idiotLabel = cocos.text.Label('idiots: ' + str(len(self.idiots)) + ', ' + str(self.idiots_count), font_size=18, x=800, y=620)
        self.add(self.idiotLabel)

        self.restLabel = cocos.text.Label('rests: ' + str(len(self.restaurances)) + ', ' + str(self.restaurances_count), font_size=18, x=800, y=580)
        self.add(self.restLabel)

        self.totalLabel = cocos.text.Label('total: ' + str(len(self.people)) + ', ' + str(self.people_count), font_size=18, x=800, y=540)
        self.add(self.totalLabel)
        #

        self.schedule(self.update)

    def update(self, dt):
        self.hos.rotation += 0.75
        self.timeLabel.element.text = 'Time: ' + '%.3f' %(time.time() - self.timer)
        self.idiotLabel.element.text = 'idiots: ' + str(len(self.idiots)) + ', ' + str(self.idiots_count)
        self.restLabel.element.text = 'rests: ' + str(len(self.restaurances)) + ', ' + str(self.restaurances_count)
        self.totalLabel.element.text = 'total: ' + str(len(self.people)) + ', ' + str(self.people_count)
        for person in self.people:
            if(person.moveable):
                theta = math.atan2(person.posy - self.center_y, person.posx - self.center_x)
                person.update_position((person.posx - (self.p_speed * math.cos(theta) - self.h_speed * math.sin(theta))/person.distance ,
                    person.posy - (self.p_speed * math.sin(theta) + self.h_speed * math.cos(theta))/person.distance), 
                    self.center_x, self.center_y)

                if(person.distance < self.storm_radius):
                    self.remove_person(person)

    def update_text(self, x, y):
        text = 'Mouse @ %d,%d' % (x, y)
        self.mouseLabel.element.text = text

    def on_mouse_motion(self, x, y, dx, dy):
        """Called when the mouse moves over the app window with no button pressed
        
        (x, y) are the physical coordinates of the mouse
        (dx, dy) is the distance vector covered by the mouse pointer since the
          last call.
        """
        self.update_text(x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Called when the mouse moves over the app window with some button(s) pressed
        
        (x, y) are the physical coordinates of the mouse
        (dx, dy) is the distance vector covered by the mouse pointer since the
          last call.
        'buttons' is a bitwise or of pyglet.window.mouse constants LEFT, MIDDLE, RIGHT
        'modifiers' is a bitwise or of pyglet.window.key modifier constants
           (values like 'SHIFT', 'OPTION', 'ALT')
        """
        if(self.is_select):
            self.picking_object.update_position(director.get_virtual_coordinates(x, y), self.center_x, self.center_y)

    def on_mouse_press(self, x, y, buttons, modifiers):
        """This function is called when any mouse button is pressed

        (x, y) are the physical coordinates of the mouse
        'buttons' is a bitwise or of pyglet.window.mouse constants LEFT, MIDDLE, RIGHT
        'modifiers' is a bitwise or of pyglet.window.key modifier constants
           (values like 'SHIFT', 'OPTION', 'ALT')
        """
        if(buttons == pyglet.window.mouse.LEFT):
            m = self.click_radius
            v_x, v_y = director.get_virtual_coordinates(x,y)
            for i in range(len(self.people)):
                s_x, s_y = self.people[i].sprite.position
                dx = v_x - s_x
                dy = v_y - s_y
                l = math.pow(dx, 2) + math.pow(dy, 2)
                if(l < self.click_radius):
                    self.is_select = True
                    if(m > l):
                        self.picking_object = self.people[i]
            if(self.is_select):
                self.picking_object.moveable = False
                self.picking_object.update_position((v_x, v_y), self.center_x, self.center_y)

        elif(buttons == pyglet.window.mouse.RIGHT):
            v_x, v_y = director.get_virtual_coordinates(x, y)
            idiot = Idiot(v_x, v_y)
            idiot.distance = math.sqrt(math.pow(idiot.posx - self.center_x, 2) + math.pow(idiot.posy - self.center_y, 2))
            self.add_person(idiot)

    def on_mouse_release(self, x, y, buttons, modifiers):
        self.is_select = False
        self.picking_object.moveable = True
        if(buttons == pyglet.window.mouse.LEFT):
            person = self.picking_object
            if(person.distance < self.storm_radius):
                self.remove_person(person)

    def create_idiot(self):
        rand = random.random() * 2 * math.pi
        idiot = Idiot((1 + math.cos(rand) * 0.9)*self.center_x, (1+math.sin(rand) * 0.9)*self.center_y)
        idiot.distance = math.sqrt(math.pow(idiot.posx - self.center_x, 2) + math.pow(idiot.posy - self.center_y, 2))
        self.add_person(idiot)

    def create_restaurance(self):
        rand = random.random() * 2 * math.pi
        restaurance = Restaurance((1 + math.cos(rand) * 0.9)*self.center_x, (1+math.sin(rand) * 0.9)*self.center_y)
        restaurance.distance = math.sqrt(math.pow(restaurance.posx - self.center_x, 2) + math.pow(restaurance.posy - self.center_y, 2))
        self.add_person(restaurance)

    def add_person(self, person):
        self.add(person)
        self.people.append(person)
        self.people_count+=1
        if(person.id == 0):
            self.idiots.append(person)
            self.idiots_count+=1
        else:
            self.restaurances.append(person)
            self.restaurances_count+=1

    def remove_person(self, person):
        self.remove(person)
        self.people.remove(person)
        self.people_count-=1
        if(person.id == 0):
            self.idiots.remove(person)
            self.idiots_count-=1
        else:
            self.restaurances.remove(person)
            self.restaurances_count-=1

if __name__ == "__main__":
    director.init(width=1024, height=768,resizable=False)
    scene = cocos.scene.Scene()
    mainFrame = MainFrame()
    scene.add(mainFrame)
    director.run(scene)