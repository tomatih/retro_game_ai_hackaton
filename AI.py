# -*- coding: utf-8 -*-
"""
Created on Wed Oct 28 14:39:46 2020

@author: khale
"""
import numpy as np


def detect_threat(x, y, dx, dy, endx, endy):
    temp_x = x;
    temp_y = y;
    count = 0
    
    while (True):
        if temp_x <= endx:
            break
        if temp_y == endy or temp_y == (-1 * endy):
            break
        temp_x += dx
        temp_y += dy
        count += 1
    return [temp_x, temp_y, count]
        

class Kalman:
    def __init__(self, danger_distance):     
        self.enemy_positions = []
        self.bullets = []
        self.PLAYER_POSITION =[]
        self.danger_distance = danger_distance
        self.win_height = 0
        
        self.on = False
        
        self.up = False
        self.down = False
        self.shoot = False
        
        self.enemies_in_range = 0
    

    def check_diagnoal(self, bullet):
        if self.on:
            for i in self.enemy_positions:
                if i[2] == 50 and (i[0] == bullet.x and i[1] == bullet.y + i[3]):
                    return True
            return False
        else:
            return False
        
    def take_action(self):
        if self.on:
            danger = False
            net_force = 0
            for i in self.bullets:
                temp = np.sqrt(np.power(i[0]-self.PLAYER_POSITION[0], 2)+np.power(i[1]-self.PLAYER_POSITION[1], 2))
                if temp <= self.danger_distance:
                    danger = True
                    break
                
            if danger:
                for i in self.bullets:
                    threat = detect_threat(i[0], i[1], -2, 2*i[2]*0.5, self.PLAYER_POSITION[0], self.win_height)
                    if threat[0] <= self.PLAYER_POSITION[0] or i[0] <= self.PLAYER_POSITION[0] + (self.danger_distance/2):
                        temp = np.sqrt(np.power(i[0]-self.PLAYER_POSITION[0], 2)+np.power(i[1]-self.PLAYER_POSITION[1], 2))
                        if temp <= self.danger_distance * 2 / 3:
                            if i[1] > self.PLAYER_POSITION[1]:
                                net_force += np.sqrt(np.power(i[0]-self.PLAYER_POSITION[0], 2)+np.power(i[1]-self.PLAYER_POSITION[1], 2))/np.exp(threat[2])
                            elif i[1] < self.PLAYER_POSITION[1]:
                                net_force -= np.sqrt(np.power(i[0]-self.PLAYER_POSITION[0], 2)+np.power(i[1]-self.PLAYER_POSITION[1], 2))/np.exp(threat[2])
                if net_force > 0:
                    self.up = True
                elif net_force < 0:
                    self.down = True
                else:
                    self.shoot = True
            else:
                if self.enemies_in_range != 0:
                    self.shoot = True
                    self.enemies_in_range -= 1
                    wanted_index = 0
                    closestx = 1000000
                    for i in range(len(self.enemy_positions)):
                        if self.enemy_positions[i][1] - 2 <= self.PLAYER_POSITION[1] <=  self.enemy_positions[i][1] + 2 and abs(self.enemy_positions[i][0] -  self.PLAYER_POSITION[0]) < closestx:
                            wanted_index = i
                            closestx = self.enemy_positions[i][0]
                    self.enemy_positions[wanted_index][4] = 1
                else:
                    for i in self.enemy_positions:
                        if i[4] != 1:
                            if  i[1] - 2 <= self.PLAYER_POSITION[1] <=  i[1] + 2:
                                self.enemies_in_range += 1
                            elif i[1] > self.PLAYER_POSITION[1]:
                                net_force -= i[2]
                            else:
                                net_force += i[2]
                            if i[1] > self.PLAYER_POSITION[1]:
                                net_force += 1/(self.PLAYER_POSITION[1] - i[1] ) 
                            elif i[1] < self.PLAYER_POSITION[1]:
                                net_force += 1/(i[1] - self.PLAYER_POSITION[1])
                            
                            
                        
                    if self.enemies_in_range != 0:
                        self.shoot = True
                        self.enemies_in_range -= 1
                        wanted_index = 0
                        closestx = 1000000
                        for i in range(len(self.enemy_positions)):
                            if self.enemy_positions[i][1] - 2 <= self.PLAYER_POSITION[1] <=  self.enemy_positions[i][1] + 2 and abs(self.enemy_positions[i][0] -  self.PLAYER_POSITION[0]) < closestx:
                                wanted_index = i
                                closestx = self.enemy_positions[i][0]
                        self.enemy_positions[wanted_index][4] = 1
                    else:
                        if net_force > 0:
                            self.up = True
                        elif net_force < 0:
                            self.down = True
                        
        
        
                