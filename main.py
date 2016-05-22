# -*- encoding: utf-8 -*-
#!/usr/bin/env python

from __future__ import division, print_function, unicode_literals

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#

import cocos
from cocos.actions import *
from cocos.director import director
from cocos import audio

import pyglet
try:
    import pyglet.media.avbin
    have_avbin = True
except:
    have_avbin = False

import time
import math
import random
import webbrowser

class ScoreManageFrame(cocos.layer.Layer):
    
    def getHallOfFame(self):
        return self.data
    
    def saveScore(self):
        f = file('score.db','w')
        for i in self.data:
            f.write(str(i[0])+" "+i[1]+"\n")
        f.close()
    
    def updateScore(self, score, NAME):
        self.data.append((score, NAME))
        self.data.sort()
        self.data.reverse()
        self.data = self.data [:17]
        self.saveScore()
        
    def __init__(self):
        if os.path.isfile('score.db'):
            f = file('score.db','r')
            self.data = map(lambda x: (int(x[0]), x[1]), map(lambda x: x.split(), f.readlines()))
            self.data.sort()
            self.data.reverse()
            f.close()
        else:
            self.data = [ (0,'NONAME') for i in range(17)]
            self.saveScore()
            
    

class GameOverFrame(cocos.layer.Layer):
    is_event_handler = True
    def __init__(self, score):
        super(GameOverFrame, self).__init__()
        self.hos = cocos.sprite.Sprite('hos.png')
        self.windowx, self.windowy = director.get_window_size()
        self.hos.position = self.windowx/2, self.windowy/2
        self.add(self.hos, z = 1)
        self.hos.do(ScaleTo(5, 3))
        self.hos.do(RotateBy(720, 3))
        self.timer = time.time()
        self.webOpen = False
        self.schedule(self.update)
        self.score = score
        
    def update(self, dt):
        currentTime = time.time() -  self.timer
        if currentTime >3 and not self.webOpen :
            self.webOpen = True
            webbrowser.open_new("http://kr.battle.net/heroes/ko/")
            self.remove(self.hos)
            self.infoLabel = cocos.text.Label('Type Your Name And Press Enter:', font_size = 18, x=512, y=450, anchor_x = "center")
            self.add(self.infoLabel)
            
            self.name = ""
            self.nameLabel = cocos.text.Label(self.name, font_size=36, x= 320, y =384, )
            self.add(self.nameLabel)
            
            self.scoreLabel = cocos.text.Label('Score: '+str(self.score),font_size=24, x=512, y=500, anchor_x = "center")
            self.add(self.scoreLabel)
            
        if self.webOpen:
            if int(currentTime*3)%2==0 :
                self.nameLabel.element.text = self.name + " "
            else:
                self.nameLabel.element.text = self.name + "|"
    def on_mouse_press(self, x, y, buttons, modifiers):
        pass
           
    
    def on_key_press(self, key, modifiers):
        print (key)
        print (pyglet.window.key.symbol_string(key))
        if self.webOpen:
            if ord('a')<= key <=ord('z'):
                if len(self.name) < 6:
                    self.name += pyglet.window.key.symbol_string(key)
                    #self.nameLabel.element.text = self.name
            if pyglet.window.key.symbol_string(key) == 'BACKSPACE':
                if len(self.name) != 0:
                    self.name = self.name [:-1]
                    #self.nameLabel.element.text = self.name
            if pyglet.window.key.symbol_string(key) == 'RETURN':
                if(self.name ==''): self.name = 'NONAME'
                scoreManageFrame.updateScore(self.score, self.name)
                del self
                scene = cocos.scene.Scene()
                titleFrame = TitleFrame()
                if(have_avbin):
                    music_player.queue(pyglet.resource.media('MainMenu.mp3', streaming=True))
                    music_player.queue(pyglet.resource.media('OST.mp3', streaming=True))
                    music_player.next()
                scene.add(titleFrame)
                director.replace(scene)             
        
    
class TitleFrame(cocos.layer.Layer):
    
    is_event_handler = True
    
    @classmethod
    def ordinalPostfix(cls,a):
        if a%100 == 11 or a%100 == 12 or a%100 == 13: return "th"
        if a%10 == 1: return "st"
        if a%10 == 2: return "nd"
        if a%10 == 3: return "rd"
        return "th"
    
    def __init__(self):
        super(TitleFrame, self).__init__()
        self.logo = cocos.sprite.Sprite('logo.png')
        self.logo.position = 512, 600
        self.add(self.logo)
        self.chosen = False
        
        self.start_button = cocos.sprite.Sprite('run.png')
        self.start_button.position = 512, 384
        self.add(self.start_button)
        self.run3_img_src = pyglet.image.load('run3.png')
        self.run2_img_src = pyglet.image.load('run2.png')
        self.run_img_src = pyglet.image.load('run.png')
        
        self.scoreLabel = []
        HighScoreData = scoreManageFrame.getHallOfFame()
        for i in range(17):
            self.scoreLabel.append(cocos.text.Label(('%2d%s: '%(i+1,TitleFrame.ordinalPostfix(i+1)) )+('%06d %s'%HighScoreData[i]),font_name='GulimChe',font_size=16, x=750, y=700-i*40))
            self.add(self.scoreLabel[i])    
            
    @classmethod
    def insideObj(cls, obj, x, y):
        return obj.x - obj.width/2 <= x <= obj.x + obj.width/2 and obj.y - obj.height/2 <= y <= obj.y + obj.height/2
        
    
    def on_mouse_motion(self, x, y, dx, dy):
        if TitleFrame.insideObj(self.start_button, x, y):
            self.start_button.image = self.run2_img_src
        else:
            self.start_button.image = self.run_img_src

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.chosen: return
        if TitleFrame.insideObj(self.start_button, x, y):
            self.start_button.image = self.run2_img_src
        else:
            self.start_button.image = self.run_img_src
   
    def on_mouse_press(self, x, y, buttons, modifiers):            
        
        if TitleFrame.insideObj(self.start_button, x, y):
            self.start_button.image = self.run3_img_src
            self.chosen = True
        else:
            self.chosen = False
    
    def on_mouse_release(self, x, y, buttons, modifiers):
        if self.chosen and TitleFrame.insideObj(self.start_button, x, y):
            if(have_avbin):
                music_player.next()
            scene = cocos.scene.Scene()
            mainFrame = MainFrame()
            scene.add(mainFrame)
            eventHandler = EventHandler(mainFrame)
            scene.add(eventHandler)
            mainFrame.eventHandler = eventHandler
            director.replace(scene)
        self.chosen = False
        
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
        self.standOn = False
        self.p_speed = 0
        self.h_speed = 0
        self.add(self.sprite, z = 1)

    def update_position(self, pos, x, y):
        self.posx, self.posy = pos
        self.sprite.position  = pos
        self.distance = math.sqrt(math.pow(self.posx - x, 2) + math.pow(self.posy - y, 2))

class Restaurance(cocos.layer.Layer):
    def __init__(self, x, y, spy_on):
        super(Restaurance, self).__init__()
        self.id = 1
        self.moveable = True
        self.posx = x
        self.posy = y
        self.distance = 0
        self.spy_on = spy_on
        if(spy_on):
            self.sprite = cocos.sprite.Sprite('spy.png')
        else:
            self.sprite = cocos.sprite.Sprite('restaurance.png')
        self.sprite.position = x, y
        self.standOn = False
        self.p_speed = 0
        self.h_speed = 0
        self.timer = 0
        self.portal_time = 5
        self.portal_distance = 250
        self.add(self.sprite, z = 1)

    def update_position(self, pos, x, y):
        self.posx, self.posy = pos
        self.sprite.position  = pos
        self.distance = math.sqrt(math.pow(self.posx - x, 2) + math.pow(self.posy - y, 2))

    def update_time(self, mainFrame, dt):
        self.timer += dt
        if(self.timer >= self.portal_time and self.distance > self.portal_distance):
            portal = Portal(mainFrame, self.posx, self.posy)
            mainFrame.add(portal, z = 1)
            self.timer -= self.portal_time

class Portal(cocos.layer.Layer):
    is_event_handler = True
    
    def __init__(self, mainFrame, x, y):
        super(Portal, self).__init__()
        self.id = 2
        self.mainFrame = mainFrame
        self.posx = x
        self.posy = y
        self.sprite = cocos.sprite.Sprite('portal.png')
        self.sprite.scale = 0.3
        self.sprite.position = x, y
        self.timer = 0
        self.gen_time = 6
        self.max_num = 2
        self.create_num = 0
        self.remove = False
        self.schedule(self.update)
        self.mainFrame.PortalList.append(self)
        self.add(self.sprite, z = 1)

    def update(self, dt):
        self.timer += dt
        if(self.remove):
            if(self.timer >= self.gen_time):
                self.mainFrame.remove(self)
                self.mainFrame.PortalList.remove(self)
                del self
                return

        if(self.timer >= self.gen_time):
            self.timer -= self.gen_time
            self.mainFrame.create_idiot_pos(self.posx, self.posy)
            self.create_num += 1
            if(self.create_num >= self.max_num):
                self.remove = True
                self.timer = 0
                self.sprite.do(ScaleTo(0.2, self.gen_time - 1))
        return

class OrangePortal(cocos.layer.Layer):
    is_event_handler = True
    
    def __init__(self, mainFrame, x, y):
        super(OrangePortal, self).__init__()
        self.id = 2
        self.mainFrame = mainFrame
        self.posx = x
        self.posy = y
        self.sprite = cocos.sprite.Sprite('portal2.png')
        self.sprite.scale = 0.3
        self.sprite.position = x, y
        self.timer = 0
        self.gen_time = 6
        self.max_num = 1
        self.create_num = 0
        self.remove = False
        self.schedule(self.update)
        self.mainFrame.PortalList.append(self)
        self.add(self.sprite, z = 1)

    def update(self, dt):
        self.timer += dt
        if(self.remove):
            if(self.timer >= self.gen_time):
                self.mainFrame.remove(self)
                self.mainFrame.PortalList.remove(self)
                del self
                return

        if(self.timer >= self.gen_time):
            self.timer -= self.gen_time
            self.mainFrame.create_restaurance_pos(self.posx, self.posy)
            self.create_num += 1
            if(self.create_num >= self.max_num):
                self.remove = True
                self.timer = 0
                self.sprite.do(ScaleTo(0.2, self.gen_time - 1))
        return        
        

class EventHandler(cocos.layer.Layer):
    is_event_handler = True
    def __init__(self, mainFrame):
        super(EventHandler, self).__init__()
        self.mainFrame = mainFrame
        self.mainFrame.eventHandler = self
        self.schedule(self.update)
        self.prevTime = 0
        self.sprites = []

    def update(self, dt):
        currentTime = time.time() - self.mainFrame.timer
        if(currentTime > 3):
            if(self.prevTime <= 3):
                self.start_adv()
                self.mainFrame.testLabel.element.text = "zzzzzzzzzzzzzz!"
                
        if(currentTime > 9):
            if(self.prevTime <= 9):
                self.start_spy()
                
        if(currentTime > 12):
            if(self.prevTime <= 12):
                self.start_sudden(6)
                
        if(currentTime > 15):
            if(self.prevTime <= 15):
                self.end_adv()
                
        if(currentTime > 18):
            if(self.prevTime <= 18):
                self.end_spy()
        
        if(currentTime > 20):
            if(self.prevTime <= 20):
                self.blackout()
        
        if(currentTime > 20.5):
            if(self.prevTime <= 20.5):
                self.removeblackout()

        if(currentTime > 21):
            if(self.prevTime <= 21):
                self.blackout()
        
        if(currentTime > 21.5):
            if(self.prevTime <= 21.5):
                self.removeblackout()
                
        if(currentTime > 22):
            if(self.prevTime <= 22):
                self.start_spy()
                self.blackout()
        
        if(currentTime > 23):
            if(self.prevTime <= 23):
                self.removeblackout()
                self.start_adv()
        
        if(currentTime > 27):
            if(self.prevTime <= 27):
                self.start_spy()
                self.start_sudden(6)
        
        if(currentTime > 32):
            if(self.prevTime <=32):
                self.open_restaurance_portal()
                self.end_spy()

        if(currentTime > 35):
            if(self.prevTime <= 35):
                self.end_adv()
        self.prevTime = time.time()-self.mainFrame.timer

    def start_adv(self):
        self.backScene = cocos.scene.Scene()
        self.backScene.transform_anchor = self.mainFrame.hos.position
        n = 3
        self.add(self.backScene)
        for i in range(n):
            sprite = cocos.sprite.Sprite('adv.png')
            sprite.scale = 0.001
            sprite.position = self.mainFrame.hos.position
            sprite.do(ScaleTo(1, 3))
            sprite.do(RotateBy(-720, 3) + Repeat(RotateBy(360, 3)))
            sprite.do(MoveTo((self.mainFrame.center_x * (1 + 0.5*math.cos(2*math.pi * i/n)), 
                self.mainFrame.center_y * (1 + 0.5*math.sin(2*math.pi * i/n))), 3))
            self.backScene.add(sprite)
        self.backScene.do(Delay(3) + Repeat(RotateBy(-360, 3)))
        self.backScene.do(Delay(3) + ScaleTo(1.25, 3) + ScaleTo(0, 6))

    def end_adv(self):
        self.mainFrame.testLabel.element.text = "Wow!"
        self.remove(self.backScene)
        del self.backScene

    def start_sudden(self, n):
        for i in range(n):
            if i%2==0:
                restaurance = self.mainFrame.create_restaurance_pos(self.mainFrame.center_x + math.cos(2*math.pi * i/n) * self.mainFrame.storm_radius,
                    self.mainFrame.center_y + math.sin(2*math.pi * i/n) * self.mainFrame.storm_radius)
                restaurance.standOn = True
                restaurance.p_speed = -300
                restaurance.h_speed = 1000
            else:
                doslam = self.mainFrame.create_idiot_pos(self.mainFrame.center_x + math.cos(2*math.pi * i/n) * self.mainFrame.storm_radius,
                    self.mainFrame.center_y + math.sin(2*math.pi * i/n) * self.mainFrame.storm_radius)
                doslam.standOn = True
                doslam.p_speed = -300
                doslam.h_speed = 1000

    def end_sudden(self):
        pass

    def start_spy(self):
        self.mainFrame.spy_on = True
        for restaurance in self.mainFrame.restaurances:
            restaurance.sprite.image = pyglet.image.load('spy.png')

    def end_spy(self):
        self.mainFrame.spy_on = False
        for restaurance in self.mainFrame.restaurances:
            restaurance.sprite.image = pyglet.image.load('restaurance.png')
        
    def blackout(self):
        self.service = cocos.sprite.Sprite('service.jpg')
        self.service.position = self.mainFrame.windowx/2, self.mainFrame.windowy/2
        self.add(self.service, z=1)
    
    def removeblackout(self):
        self.remove(self.service)
    
    def open_restaurance_portal(self):
        n = 6
        for i in range(n):
            if i%2==0:
                portal = OrangePortal(self.mainFrame, self.mainFrame.center_x + self.mainFrame.windowx * 0.4 * math.cos(2*math.pi * i/n),
                self.mainFrame.center_y + self.mainFrame.windowy * 0.4 * math.sin(2*math.pi * i/n) )
                self.mainFrame.add(portal, z=1)
            else:
                restaurance = self.mainFrame.create_restaurance_pos(self.mainFrame.center_x + math.cos(2*math.pi * i/n) * self.mainFrame.storm_radius,
                    self.mainFrame.center_y + math.sin(2*math.pi * i/n) * self.mainFrame.storm_radius)
                restaurance.standOn = True
                restaurance.p_speed = -300
                restaurance.h_speed = 1000               
                
class MainFrame(cocos.layer.Layer):

    is_event_handler = True

    def __init__(self):
        super(MainFrame, self).__init__()
        self.hos = cocos.sprite.Sprite('hos.png')
        self.windowx, self.windowy = director.get_window_size()
        self.hos.position = self.windowx/2, self.windowy/2
        self.add(self.hos, z = 2)
        self.center_x, self.center_y = self.hos.position
        self.idiots = []
        self.restaurances = []
        self.people = []
        self.PortalList = []
        self.idiots_count = 0
        self.restaurances_count = 0
        self.people_count = 0
        self.initial_idiots = 5
        self.initial_restaurances = 2
        self.timer = time.time()
        self.is_select = False
        self.p_speed = 100 #suck speed
        self.h_speed = 1000 #rotate speed
        self.click_radius = 1000
        self.storm_radius = 100
        self.fps = 0
        self.score = 0
        self.life = 5
        self.last_idiot_gen_time = 1
        self.last_restaurance_gen_time = 1
        self.spy_on = False;
        self.debug = False

        for i in range(self.initial_idiots):
            self.create_idiot()
        for i in range(self.initial_restaurances):
            self.create_restaurance()

        
        self.highScore = scoreManageFrame.getHallOfFame()[0][0]
        
        self.highScoreLabel = cocos.text.Label('HighScore: '+str(self.highScore),font_size=18, x=800, y=740)
        self.add(self.highScoreLabel)
        
        self.scoreLabel = cocos.text.Label('Score: '+str(self.score),font_size=18, x=800, y=700)
        self.add(self.scoreLabel)

        self.timeLabel = cocos.text.Label(str(time.time() - self.timer), font_size=18, x=800, y=660)
        self.add(self.timeLabel)

        self.idiotLabel = cocos.text.Label('idiots: ' + str(self.idiots_count), font_size=18, x=800, y=620)
        self.add(self.idiotLabel)

        self.restLabel = cocos.text.Label('rests: ' + str(self.restaurances_count), font_size=18, x=800, y=580)
        self.add(self.restLabel)

        self.totalLabel = cocos.text.Label('total: ' + str(self.people_count), font_size=18, x=800, y=540)
        self.add(self.totalLabel)
        
        self.lifeLabel = cocos.text.Label('Life: '+  "♥"*self.life,font_size=18, x=800, y=500)
        self.add(self.lifeLabel)

        #for debugging
        self.mouseLabel = cocos.text.Label('No mouse events yet', font_size=18, x=800, y=460)
        self.add(self.mouseLabel)
        
        self.fpsLabel = cocos.text.Label('FPS: ' + str(self.fps), font_size=18, x=800, y=420)
        self.add(self.fpsLabel)

        self.testLabel = cocos.text.Label('Test message', font_size=18, x=800, y=380)
        self.add(self.testLabel)

        self.genTimeLabel = cocos.text.Label('genTime: '+  "0",font_size=18, x=800, y=340)
        self.add(self.genTimeLabel)
        #
        if(~self.debug):
            self.mouseLabel.scale = 0
            self.fpsLabel.scale = 0
            self.testLabel.scale = 0
            self.genTimeLabel.scale = 0

        self.schedule(self.update)

    def getTime(self):
        return time.time()-self.timer

    def update(self, dt):
        self.hos.rotation += 0.75
        
        #self.fps = int(1 / (time.time()-self.prevtime))
        if dt<0.01: self.fps = "Over 100!!!!"
        else: self.fps = int(1/dt)
        self.timeLabel.element.text = 'Time: ' + '%.3f' %(self.getTime())
        self.idiotLabel.element.text = 'idiots: ' + str(self.idiots_count)
        self.restLabel.element.text = 'rests: ' + str(self.restaurances_count)
        self.totalLabel.element.text = 'total: ' + str(self.people_count)
        self.fpsLabel.element.text = 'FPS: ' + str(self.fps)
        self.scoreLabel.element.text = 'Score: ' + str(self.calcscore())
        self.lifeLabel.element.text = 'Life: '+ "♥"*self.life
        self.highScoreLabel.element.text = 'HighScore: ' + str(max(self.highScore,self.calcscore()))
        
        required_base_gen_time = 10-math.log10(self.getTime()+1 ) 

        self.genTimeLabel.element.text = 'genTime: '+str(required_base_gen_time)
       
        #required_idiot_gen_time = required_base_gen_time / (self.restaurances_count+1)**0.5 
        required_idiot_gen_time = required_base_gen_time

        required_restaurance_gen_time = required_base_gen_time / (1+math.log10(self.getTime()+1 ) )
        if self.getTime() > self.last_idiot_gen_time + required_idiot_gen_time :
            self.create_idiot()
            self.last_idiot_gen_time = self.getTime()

        if self.getTime() > self.last_restaurance_gen_time + required_restaurance_gen_time :
            self.create_restaurance()
            self.last_restaurance_gen_time = self.getTime()


        for person in self.people:
            if(person.moveable):
                theta = math.atan2(person.posy - self.center_y, person.posx - self.center_x)
                if(person.standOn):
                    person.update_position((person.posx - (person.p_speed * math.cos(theta) - person.h_speed * math.sin(theta))/person.distance ,
                        person.posy - (person.p_speed * math.sin(theta) + person.h_speed * math.cos(theta))/person.distance), 
                        self.center_x, self.center_y)
                    if(person.distance > 400):
                        person.standOn = False

                else:
                    person.update_position((person.posx - (self.p_speed * math.cos(theta) - self.h_speed * math.sin(theta))/person.distance ,
                        person.posy - (self.p_speed * math.sin(theta) + self.h_speed * math.cos(theta))/person.distance), 
                        self.center_x, self.center_y)

                if(person.distance < self.storm_radius):
                    self.remove_person(person)
            if(person.id == 1):
                person.update_time(self, dt)

        #for portal in self.portals:
        #    portal.update_time(self, dt)
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
        if x<10: x=10
        if y<10: y=10
        if x>self.windowx: x=self.windowx
        if y>self.windowy: y=self.windowy
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
            """
            v_x, v_y = director.get_virtual_coordinates(x, y)
            idiot = Idiot(v_x, v_y)
            idiot.distance = math.sqrt(math.pow(idiot.posx - self.center_x, 2) + math.pow(idiot.posy - self.center_y, 2))
            self.add_person(idiot)
            """

    def on_mouse_release(self, x, y, buttons, modifiers):
        if hasattr(self, 'picking_object') and self.picking_object is not None:
            self.is_select = False
            self.picking_object.moveable = True
            if(buttons == pyglet.window.mouse.LEFT):
                person = self.picking_object
                if(person.distance < self.storm_radius):
                    self.remove_person(person)
            self.picking_object = None

    def on_key_press(self, key, modifiers):
        """This function is called when a key is pressed.
        
        'key' is a constant indicating which key was pressed.
        'modifiers' is a bitwise or of several constants indicating which
           modifiers are active at the time of the press (ctrl, shift, capslock, etc.)

        See also on_key_release situations when a key press does not fire an
         'on_key_press' event.
        """
        if(pyglet.window.key.symbol_string(key) == 'D'):
            if(self.debug):
                self.mouseLabel.scale = 0
                self.fpsLabel.scale = 0
                self.testLabel.scale = 0
                self.genTimeLabel.scale = 0
            else:
                self.mouseLabel.scale = 1
                self.fpsLabel.scale = 1
                self.testLabel.scale = 1
                self.genTimeLabel.scale = 1
            self.debug = ~self.debug

    def create_idiot(self):
        rand = random.random() * 2 * math.pi
        return self.create_idiot_pos((1 + math.cos(rand) * 0.9)*self.center_x, (1+math.sin(rand) * 0.9)*self.center_y)

    def create_idiot_pos(self, x, y):
        idiot = Idiot(x, y)
        idiot.distance = math.sqrt(math.pow(idiot.posx - self.center_x, 2) + math.pow(idiot.posy - self.center_y, 2))
        self.add_person(idiot)
        return idiot

    def create_restaurance(self):
        rand = random.random() * 2 * math.pi
        return self.create_restaurance_pos((1 + math.cos(rand) * 0.9)*self.center_x, (1+math.sin(rand) * 0.9)*self.center_y)

    def create_restaurance_pos(self, x, y):
        restaurance = Restaurance(x, y, self.spy_on)
        restaurance.distance = math.sqrt(math.pow(restaurance.posx - self.center_x, 2) + math.pow(restaurance.posy - self.center_y, 2))
        self.add_person(restaurance)
        return restaurance

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
            self.life -= 1
            if self.life <=0: self.gameover()
        else:
            self.restaurances.remove(person)
            self.restaurances_count-=1
            self.score += 100
        del person


    def gameover(self):
        scene = cocos.scene.Scene()
        gameOverFrame = GameOverFrame(self.calcscore())
        scene.add(gameOverFrame)
        director.replace(scene)
        for elem in self.PortalList: del elem
        for elem in self.people: del elem
        del self.eventHandler
        del self
        return 

    def calcscore(self):
        return int(self.score+(time.time()-self.timer)*30)

        
if __name__ == "__main__":
    global scoreManageFrame
    scoreManageFrame = ScoreManageFrame() 
    director.init(width=1024, height=768,resizable=False, caption = "Hero is Dead!")
    scene = cocos.scene.Scene()
    titleFrame = TitleFrame()
    scene.add(titleFrame)
    if(have_avbin):
        global music_player
        music_player = pyglet.media.Player()
        music_player.eos_action = 'loop'
        music_player.queue(pyglet.resource.media('MainMenu.mp3', streaming=True))
        music_player.queue(pyglet.resource.media('OST.mp3', streaming=True))
        music_player.play()
    director.run(scene)