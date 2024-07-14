import points as pt
import collections
from graph import moveWithoutBreakingWalls
import random
import math

barbarians = []
dragons = []
balloons = []
archers = []
stealthArcher=[]
healers=[]

troops_spawned = {
    'barbarian': 0,
    'archer': 0,
    'dragon': 0,
    'balloon': 0,
    'stealtharcher':0,
    'healer':0
}


def clearTroops():
    barbarians.clear()
    dragons.clear()
    balloons.clear()
    archers.clear()
    healers.clear()
    troops_spawned['barbarian'] = 0
    troops_spawned['dragon'] = 0
    troops_spawned['balloon'] = 0
    troops_spawned['archer'] = 0
    troops_spawned['SteathArcher']=0
    troops_spawned['healer']=0



class Barbarian:
    def __init__(self, position):
        self.speed = 1
        self.health = 100
        self.max_health = 100
        self.attack = 1
        self.position = position
        self.alive = True
        self.target = None

    def move(self, pos, V, type):
        if(self.alive == False):
            return
        vmap = V.map
        r = abs(pos[0] - self.position[0])
        c = abs(pos[1] - self.position[1])
        if(r + c == 1):
            info = vmap[pos[0]][pos[1]]
            if(info == pt.TOWNHALL):
                self.break_building(pos[0], pos[1], V)
                return
            x = int(info.split(':')[1])
            y = int(info.split(':')[2])
            self.break_building(x, y, V)
            return
        elif type == 1:
            flag = 0
            for i in range(self.speed):
                coords = findPathWithoutWall(V.map, self.position, pos)
                if(coords == None):
                    flag = 1
                    break
                info = vmap[pos[0]][pos[1]]
                x = 0
                y = 0
                if(info != pt.TOWNHALL):
                    x = int(info.split(':')[1])
                    y = int(info.split(':')[2])
                else:
                    x = pos[0]
                    y = pos[1]
                if(x == coords[0] and y == coords[1]):
                    flag = 1
                    break
                self.position = coords
            if(flag == 0):
                return
        if(r == 0):
            if(pos[1] > self.position[1]):
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] + 1
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[1] += 1
                    if(abs(pos[1] - self.position[1]) == 1):
                        break
            else:
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] - 1
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[1] -= 1
                    if(abs(pos[1] - self.position[1]) == 1):
                        break
        elif(r > 1):
            if(pos[0] > self.position[0]):
                for i in range(self.speed):
                    r = self.position[0] + 1
                    c = self.position[1]
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[0] += 1
                    if(self.position[0] == pos[0]):
                        return
            else:
                for i in range(self.speed):
                    r = self.position[0] - 1
                    c = self.position[1]
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[0] -= 1
                    if(self.position[0] == pos[0]):
                        return
        elif(c > 1):
            if(pos[1] > self.position[1]):
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] + 1
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[1] += 1
                    if(self.position[1] == pos[1]):
                        return
            else:
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] - 1
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[1] -= 1
                    if(self.position[1] == pos[1]):
                        return
        elif(r+c == 2):
            if(pos[0] > self.position[0]):
                for i in range(self.speed):
                    r = self.position[0] + 1
                    c = self.position[1]
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[0] += 1
            else:
                for i in range(self.speed):
                    r = self.position[0] - 1
                    c = self.position[1]
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[0] -= 1

    def check_for_walls(self, x, y, vmap):
        if(vmap[x][y] == pt.WALL):
            return True
        return False

    def break_wall(self, x, y, V):
        target = V.wall_objs[(x, y)]
        self.attack_target(target)

    def break_building(self, x, y, V):
        target = None
        if(V.map[x][y] == pt.TOWNHALL):
            target = V.town_hall_obj
        else:
            all_buildings = collections.ChainMap(
                V.hut_objs, V.cannon_objs, V.wizard_tower_objs)
            target = all_buildings[(x, y)]
        self.attack_target(target)

    def attack_target(self, target):
        if(self.alive == False):
            return
        target.health -= self.attack
        if target.health <= 0:
            target.health = 0
            target.destroy()

    def kill(self):
        self.alive = False
        barbarians.remove(self)

    def deal_damage(self, hit,current_time):
        if(self.alive == False):
            return
        self.health -= hit
        if self.health <= 0:
            self.health = 0
            self.kill()

    def rage_effect(self):
        self.speed = self.speed*2
        self.attack = self.attack*2

    def heal_effect(self):
        self.health = self.health*1.5
        if self.health > self.max_health:
            self.health = self.max_health


class Archer:
    def __init__(self, position):
        self.speed = 1
        self.health = 100
        self.max_health = 100
        self.attack = 1
        self.attack_radius= random.randint(2,5)
        self.position = position
        self.alive = True
        self.target = None

    def isInAttackradius(self,pos):
        r = abs(pos[0] - self.position[0])
        c = abs(pos[1] - self.position[1])
        if(r**2 + c**2 <= self.attack_radius**2):
            return True
        return False

    def move(self, pos, V, type):
        if(self.alive == False):
            return
        vmap = V.map
        r = abs(pos[0] - self.position[0])
        c = abs(pos[1] - self.position[1])
        if(self.isInAttackradius(pos)):
            info = vmap[pos[0]][pos[1]]
            if(info == pt.TOWNHALL):
                self.break_building(pos[0], pos[1], V)
                return
            x = int(info.split(':')[1])
            y = int(info.split(':')[2])
            self.break_building(x, y, V)
            return
        elif type == 1:
            flag = 0
            for i in range(self.speed):
                coords = findPathWithoutWall(V.map, self.position, pos)
                if(coords == None):
                    flag = 1
                    break
                self.position = coords
            if(flag == 0):
                return
        if(r == 0):
            if(pos[1] > self.position[1]):
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] + 1
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[1] += 1
                    if(self.isInAttackradius(pos)):
                        break
            else:
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] - 1
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[1] -= 1
                    if(self.isInAttackradius(pos)):
                        break
        elif(r > 1):
            if(pos[0] > self.position[0]):
                for i in range(self.speed):
                    r = self.position[0] + 1
                    c = self.position[1]
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[0] += 1
                    if(self.position[0] == pos[0] or self.isInAttackradius(pos)):
                        return
            else:
                for i in range(self.speed):
                    r = self.position[0] - 1
                    c = self.position[1]
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[0] -= 1
                    if(self.position[0] == pos[0] or self.isInAttackradius(pos)):
                        return
        elif(c > 1):
            if(pos[1] > self.position[1]):
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] + 1
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[1] += 1
                    if(self.position[1] == pos[1] or self.isInAttackradius(pos)):
                        return
            else:
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] - 1
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[1] -= 1
                    if(self.position[1] == pos[1] or self.isInAttackradius(pos)):
                        return
        elif(r+c == 2):
            if(pos[0] > self.position[0]):
                for i in range(self.speed):
                    r = self.position[0] + 1
                    c = self.position[1]
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[0] += 1
                    if(self.isInAttackradius(pos)):
                        break
            else:
                for i in range(self.speed):
                    r = self.position[0] - 1
                    c = self.position[1]
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[0] -= 1
                    if(self.isInAttackradius(pos)):
                        break

    def check_for_walls(self, x, y, vmap):
        if(vmap[x][y] == pt.WALL):
            return True
        return False

    def break_wall(self, x, y, V):
        target = V.wall_objs[(x, y)]
        self.attack_target(target)

    def break_building(self, x, y, V):
        target = None
        if(V.map[x][y] == pt.TOWNHALL):
            target = V.town_hall_obj
        else:
            all_buildings = collections.ChainMap(
                V.hut_objs, V.cannon_objs, V.wizard_tower_objs)
            target = all_buildings[(x, y)]
        self.attack_target(target)

    def attack_target(self, target):
        if(self.alive == False):
            return
        target.health -= self.attack
        if target.health <= 0:
            target.health = 0
            target.destroy()

    def kill(self):
        self.alive = False
        archers.remove(self)

    def deal_damage(self, hit,current_time):
        if(self.alive == False):
            return
        self.health -= hit
        if self.health <= 0:
            self.health = 0
            self.kill()

    def rage_effect(self):
        self.speed = self.speed*2
        self.attack = self.attack*2

    def heal_effect(self):
        self.health = self.health*1.5
        if self.health > self.max_health:
            self.health = self.max_health


class Dragon:
    def __init__(self, position):
        self.speed = 1
        self.health = 100
        self.max_health = 100
        self.attack = 5
        self.position = position
        self.alive = True
        

    def move(self, pos, V):
        if(self.alive == False):
            return
        vmap = V.map
        r = abs(pos[0] - self.position[0])
        c = abs(pos[1] - self.position[1])
        if(r + c == 1):
            info = vmap[pos[0]][pos[1]]
            if(info == pt.TOWNHALL):
                self.break_building(pos[0], pos[1], V)
                return
            x = int(info.split(':')[1])
            y = int(info.split(':')[2])
            self.break_building(x, y, V)
            return
        elif(r == 0):
            if(pos[1] > self.position[1]):
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] + 1
                    self.position[1] += 1
                    if(abs(pos[1] - self.position[1]) == 1):
                        break
            else:
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] - 1
                    self.position[1] -= 1
                    if(abs(pos[1] - self.position[1]) == 1):
                        break
        elif(r > 1):
            if(pos[0] > self.position[0]):
                for i in range(self.speed):
                    r = self.position[0] + 1
                    c = self.position[1]
                    self.position[0] += 1
                    if(self.position[0] == pos[0]):
                        return
            else:
                for i in range(self.speed):
                    r = self.position[0] - 1
                    c = self.position[1]
                    self.position[0] -= 1
                    if(self.position[0] == pos[0]):
                        return
        elif(c > 1):
            if(pos[1] > self.position[1]):
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] + 1
                    self.position[1] += 1
                    if(self.position[1] == pos[1]):
                        return
            else:
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] - 1
                    self.position[1] -= 1
                    if(self.position[1] == pos[1]):
                        return
        elif(r+c == 2):
            if(pos[0] > self.position[0]):
                for i in range(self.speed):
                    r = self.position[0] + 1
                    c = self.position[1]
                    self.position[0] += 1
            else:
                for i in range(self.speed):
                    r = self.position[0] - 1
                    c = self.position[1]
                    self.position[0] -= 1

    def break_building(self, x, y, V):
        target = None
        if(V.map[x][y] == pt.TOWNHALL):
            target = V.town_hall_obj
        else:
            all_buildings = collections.ChainMap(
                V.hut_objs, V.cannon_objs, V.wizard_tower_objs)
            target = all_buildings[(x, y)]
        self.attack_target(target)

    def attack_target(self, target):
        if(self.alive == False):
            return
        target.health -= self.attack
        if target.health <= 0:
            target.health = 0
            target.destroy()

    def kill(self):
        self.alive = False
        dragons.remove(self)

    def deal_damage(self, hit,current_time):
        if(self.alive == False):
            return
        self.health -= hit
        if self.health <= 0:
            self.health = 0
            self.kill()

    def rage_effect(self):
        self.speed = self.speed*2
        self.attack = self.attack*2

    def heal_effect(self):
        self.health = self.health*1.5
        if self.health > self.max_health:
            self.health = self.max_health


class Balloon:
    def __init__(self, position):
        self.speed = 2
        self.health = 100
        self.max_health = 100
        self.attack = 2
        self.position = position
        self.alive = True
        

    def move(self, pos, V):
        if(self.alive == False):
            return
        vmap = V.map
        r = abs(pos[0] - self.position[0])
        c = abs(pos[1] - self.position[1])
        if(r + c == 1):
            info = vmap[pos[0]][pos[1]]
            if(info == pt.TOWNHALL):
                self.break_building(pos[0], pos[1], V)
                return
            x = int(info.split(':')[1])
            y = int(info.split(':')[2])
            self.break_building(x, y, V)
            return
        elif(r == 0):
            if(pos[1] > self.position[1]):
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] + 1
                    self.position[1] += 1
                    if(abs(pos[1] - self.position[1]) == 1):
                        break
            else:
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] - 1
                    self.position[1] -= 1
                    if(abs(pos[1] - self.position[1]) == 1):
                        break
        elif(r > 1):
            if(pos[0] > self.position[0]):
                for i in range(self.speed):
                    r = self.position[0] + 1
                    c = self.position[1]
                    self.position[0] += 1
                    if(self.position[0] == pos[0]):
                        return
            else:
                for i in range(self.speed):
                    r = self.position[0] - 1
                    c = self.position[1]
                    self.position[0] -= 1
                    if(self.position[0] == pos[0]):
                        return
        elif(c > 1):
            if(pos[1] > self.position[1]):
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] + 1
                    self.position[1] += 1
                    if(self.position[1] == pos[1]):
                        return
            else:
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] - 1
                    self.position[1] -= 1
                    if(self.position[1] == pos[1]):
                        return
        elif(r+c == 2):
            if(pos[0] > self.position[0]):
                    self.position[0] += 1
            else:
                    self.position[0] -= 1

    def break_building(self, x, y, V):
        target = None
        if(V.map[x][y] == pt.TOWNHALL):
            target = V.town_hall_obj
        else:
            all_buildings = collections.ChainMap(
                V.hut_objs, V.cannon_objs, V.wizard_tower_objs)
            target = all_buildings[(x, y)]
        self.attack_target(target)

    def attack_target(self, target):
        if(self.alive == False):
            return
        target.health -= self.attack
        if target.health <= 0:
            target.health = 0
            target.destroy()

    def kill(self):
        self.alive = False
        balloons.remove(self)

    def deal_damage(self, hit,current_time):
        if(self.alive == False):
            return
        self.health -= hit
        if self.health <= 0:
            self.health = 0
            self.kill()

    def rage_effect(self):
        self.speed = self.speed*2
        self.attack = self.attack*2

    def heal_effect(self):
        self.health = self.health*1.5
        if self.health > self.max_health:
            self.health = self.max_health


def spawnBarbarian(pos):
    if(pt.troop_limit['barbarian'] <= troops_spawned['barbarian']):
        return

    # convert tuple to list
    pos = list(pos)
    barb = Barbarian(pos)
    troops_spawned['barbarian'] += 1
    barbarians.append(barb)

def spawnArcher(pos):
    if(pt.troop_limit['archer'] <= troops_spawned['archer']):
        return

    # convert tuple to list
    pos = list(pos)
    archer = Archer(pos)
    troops_spawned['archer'] += 1
    archers.append(archer)

def spawnDragon(pos):
    if(pt.troop_limit['dragon'] <= troops_spawned['dragon']):
        return

    # convert tuple to list
    pos = list(pos)
    dr = Dragon(pos)
    troops_spawned['dragon'] += 1
    dragons.append(dr)

def spawnBalloon(pos):
    if(pt.troop_limit['balloon'] <= troops_spawned['balloon']):
        return

    # convert tuple to list
    pos = list(pos)
    bal = Balloon(pos)
    troops_spawned['balloon'] += 1
    balloons.append(bal)

def move_barbarians(V,type):
    if(type == 1):
        for barb in barbarians:
            if(barb.alive == False):
                continue
            if barb.target != None:    
                if(V.map[barb.target[0]][barb.target[1]] == pt.BLANK):
                    barb.target = None

            if(barb.target == None):
                barb.target = search_for_closest_building(barb.position, V.map, 0)
            if(barb.target == None):
                continue
            barb.move(barb.target, V, type)
    elif(type == 2):
        for barb in barbarians:
            if(barb.alive == False):
                continue
            closest_building = search_for_closest_building(barb.position, V.map, 0)
            if(closest_building == None):
                continue
            barb.move(closest_building, V, type)

def move_archers(V,type):
    if(type == 1):
        for archer in archers:
            if(archer.alive == False):
                continue
            if archer.target != None:
                if(V.map[archer.target[0]][archer.target[1]] == pt.BLANK):
                    archer.target = None
            if(archer.target == None):
                archer.target = search_for_closest_building(archer.position, V.map, 0)
            if(archer.target == None):
                continue
            archer.move(archer.target, V,type)
    elif(type == 2):
        for archer in archers:
            if(archer.alive == False):
                continue
            closest_building = search_for_closest_building(archer.position, V.map, 0)
            if(closest_building == None):
                continue
            archer.move(closest_building, V, type)

def move_dragons(V):
    for dr in dragons:
        if(dr.alive == False):
            continue
        closest_building = search_for_closest_building(dr.position, V.map, 0)
        if(closest_building == None):
            continue
        dr.move(closest_building, V)

def move_balloons(V):
    for bal in balloons:
        if(bal.alive == False):
            continue
        closest_building = search_for_closest_building(bal.position, V.map, 1)
        if(closest_building == None):
            continue
        bal.move(closest_building, V)


# def search_for_closest_troop_excluding_self():
#     pass

def search_for_closest_building(pos, vmap, prioritized):
    closest_building = None
    closest_dist = 10000
    flag = 0
    for i in range(len(vmap)):
        for j in range(len(vmap[i])):
            item = vmap[i][j].split(':')[0]
            if(prioritized == 0):
                if (item == pt.HUT or item == pt.CANNON or item == pt.TOWNHALL or item == pt.WIZARD_TOWER):
                    dist = abs(i - pos[0]) + abs(j - pos[1])
                    if(dist < closest_dist):
                        flag = 1
                        closest_dist = dist
                        closest_building = (i, j)
            else:
                if (item == pt.CANNON or item == pt.WIZARD_TOWER):
                    dist = abs(i - pos[0]) + abs(j - pos[1])
                    if(dist < closest_dist):
                        flag = 1
                        closest_dist = dist
                        closest_building = (i, j)
    if(flag == 0 and prioritized == 0):
        return None
    elif(flag == 0 and prioritized == 1):
        return search_for_closest_building(pos, vmap, 0)
    else:
        return closest_building

def findPathWithoutWall(grid,start,end):
    graph = []
    for row in grid:
        row2 = []
        for col in row:
            if(col == pt.BLANK):
                row2.append(0) # 0 means walkable
            else:
                row2.append(1) # 1 means not walkable
        graph.append(row2)
    graph[start[0]] [start[1]] = 2 # mark start as 2
    graph[end[0]] [end[1]] = 3 # mark end as 3

    coords = moveWithoutBreakingWalls(graph,start)
    if coords == None:
        return None
    else:
        return list(coords)
    
class StealthArcher:
    def __init__(self, position,spawn_time):
        self.speed = 1
        self.health = 100
        self.max_health = 100
        self.attack = 1
        self.attack_radius = random.randint(2,5)
        self.position = position
        self.alive = True
        self.target = None
        self.spawn_time=spawn_time
        self.invisible_until = spawn_time + 10


    def is_visible(self, current_time):
        return current_time >= self.invisible_until

    
    

    def isInAttackradius(self,pos):
        r = abs(pos[0] - self.position[0])
        c = abs(pos[1] - self.position[1])
        if(r**2 + c**2 <= self.attack_radius**2):
            return True
        return False

    def move(self, pos, V, type):
        if(self.alive == False):
            return
        vmap = V.map
        r = abs(pos[0] - self.position[0])
        c = abs(pos[1] - self.position[1])
        if(self.isInAttackradius(pos)):
            info = vmap[pos[0]][pos[1]]
            if(info == pt.TOWNHALL):
                self.break_building(pos[0], pos[1], V)
                return
            x = int(info.split(':')[1])
            y = int(info.split(':')[2])
            self.break_building(x, y, V)
            return
        elif type == 1:
            flag = 0
            for i in range(self.speed):
                coords = findPathWithoutWall(V.map, self.position, pos)
                if(coords == None):
                    flag = 1
                    break
                self.position = coords
            if(flag == 0):
                return
        if(r == 0):
            if(pos[1] > self.position[1]):
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] + 1
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[1] += 1
                    if(self.isInAttackradius(pos)):
                        break
            else:
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] - 1
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[1] -= 1
                    if(self.isInAttackradius(pos)):
                        break
        elif(r > 1):
            if(pos[0] > self.position[0]):
                for i in range(self.speed):
                    r = self.position[0] + 1
                    c = self.position[1]
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[0] += 1
                    if(self.position[0] == pos[0] or self.isInAttackradius(pos)):
                        return
            else:
                for i in range(self.speed):
                    r = self.position[0] - 1
                    c = self.position[1]
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[0] -= 1
                    if(self.position[0] == pos[0] or self.isInAttackradius(pos)):
                        return
        elif(c > 1):
            if(pos[1] > self.position[1]):
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] + 1
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[1] += 1
                    if(self.position[1] == pos[1] or self.isInAttackradius(pos)):
                        return
            else:
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] - 1
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[1] -= 1
                    if(self.position[1] == pos[1] or self.isInAttackradius(pos)):
                        return
        elif(r+c == 2):
            if(pos[0] > self.position[0]):
                for i in range(self.speed):
                    r = self.position[0] + 1
                    c = self.position[1]
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[0] += 1
                    if(self.isInAttackradius(pos)):
                        break
            else:
                for i in range(self.speed):
                    r = self.position[0] - 1
                    c = self.position[1]
                    if(self.check_for_walls(r, c, vmap)):
                        self.break_wall(r, c, V)
                        return
                    self.position[0] -= 1
                    if(self.isInAttackradius(pos)):
                        break

    def check_for_walls(self, x, y, vmap):
        if(vmap[x][y] == pt.WALL):
            return True
        return False

    def break_wall(self, x, y, V):
        target = V.wall_objs[(x, y)]
        self.attack_target(target)

    def break_building(self, x, y, V):
        target = None
        if(V.map[x][y] == pt.TOWNHALL):
            target = V.town_hall_obj
        else:
            all_buildings = collections.ChainMap(
                V.hut_objs, V.cannon_objs, V.wizard_tower_objs)
            target = all_buildings[(x, y)]
        self.attack_target(target)

    def attack_target(self, target):
        if(self.alive == False):
            return
        target.health -= self.attack
        if target.health <= 0:
            target.health = 0
            target.destroy()

    def kill(self):
        self.alive = False
        stealthArcher.remove(self)

    def deal_damage(self, hit,current_time):
        if(self.alive == False):
            return
        if self.is_visible(current_time):
            self.health -= hit
            if self.health <= 0:
                self.health = 0
                self.kill()

    def rage_effect(self):
        self.speed = self.speed*2
        self.attack = self.attack*2

    def heal_effect(self):
        self.health = self.health*1.5
        if self.health > self.max_health:
            self.health = self.max_health

def move_stealthArcher(V,type):
    if(type == 1):
        for i in stealthArcher:
            if(i.alive == False):
                continue
            if i.target != None:
                if(V.map[i.target[0]][i.target[1]] == pt.BLANK):
                    i.target = None
            if(i.target == None):
                i.target = search_for_closest_building(i.position, V.map, 0)
            if(i.target == None):
                continue
            i.move(i.target, V,type)
    elif(type == 2):
        for i in stealthArcher:
            if(i.alive == False):
                continue
            closest_building = search_for_closest_building(i.position, V.map, 0)
            if(closest_building == None):
                continue
            i.move(closest_building, V, type)

def spawnStealthArcher( pos,cnt):    #Current gae time has been received from the game loop which was defined as cnt 
    print("A stealth archer spawns!")
    spawn_time = cnt

        
    if(pt.troop_limit['stealtharcher'] <= troops_spawned['stealtharcher']):
        return

    # convert tuple to list
    pos = list(pos)
    stealtharcher = StealthArcher(pos,spawn_time)
    troops_spawned['stealtharcher'] += 1
    stealthArcher.append(stealtharcher)

def update(self, time_delta):
        if self.spawn_time is not None:
            self.spawn_time += time_delta
            if self.spawn_time >= 10:
                print("The stealth archer is now visible and can be targeted by buildings!")
    

class Healer:
    def __init__(self, position):
        self.speed = 1
        self.health = 250
        self.max_health = 250
        self.attack = -20 #Heal strength
        self.attack_radius= 7
        self.position = position
        self.alive = True
       
        

    # def move(self, pos, V):
    #     if(self.alive == False):
    #         return
    #     vmap = V.map
    #     r = abs(pos[0] - self.position[0])
    #     c = abs(pos[1] - self.position[1])
    #     if(r + c == 1):
    #         info = vmap[pos[0]][pos[1]]
    #         if(info == pt.TOWNHALL):
    #             self.break_building(pos[0], pos[1], V)
    #             return
    #         x = int(info.split(':')[1])
    #         y = int(info.split(':')[2])
    #         self.break_building(x, y, V)
    #         return
    #     elif(r == 0):
    #         if(pos[1] > self.position[1]):
    #             for i in range(self.speed):
    #                 r = self.position[0]
    #                 c = self.position[1] + 1
    #                 self.position[1] += 1
    #                 if(abs(pos[1] - self.position[1]) == 1):
    #                     break
    #         else:
    #             for i in range(self.speed):
    #                 r = self.position[0]
    #                 c = self.position[1] - 1
    #                 self.position[1] -= 1
    #                 if(abs(pos[1] - self.position[1]) == 1):
    #                     break
    #     elif(r > 1):
    #         if(pos[0] > self.position[0]):
    #             for i in range(self.speed):
    #                 r = self.position[0] + 1
    #                 c = self.position[1]
    #                 self.position[0] += 1
    #                 if(self.position[0] == pos[0]):
    #                     return
    #         else:
    #             for i in range(self.speed):
    #                 r = self.position[0] - 1
    #                 c = self.position[1]
    #                 self.position[0] -= 1
    #                 if(self.position[0] == pos[0]):
    #                     return
    #     elif(c > 1):
    #         if(pos[1] > self.position[1]):
    #             for i in range(self.speed):
    #                 r = self.position[0]
    #                 c = self.position[1] + 1
    #                 self.position[1] += 1
    #                 if(self.position[1] == pos[1]):
    #                     return
    #         else:
    #             for i in range(self.speed):
    #                 r = self.position[0]
    #                 c = self.position[1] - 1
    #                 self.position[1] -= 1
    #                 if(self.position[1] == pos[1]):
    #                     return
    #     elif(r+c == 2):
    #         if(pos[0] > self.position[0]):
    #             for i in range(self.speed):
    #                 r = self.position[0] + 1
    #                 c = self.position[1]
    #                 self.position[0] += 1
    #         else:
    #             for i in range(self.speed):
    #                 r = self.position[0] - 1
    #                 c = self.position[1]
    #                 self.position[0] -= 1

    # def move(self,pos, V):
    #     if self.alive == False:
    #         return
        
    #     vmap = V.map
    #     r = abs(pos[0] - self.position[0])
    #     c = abs(pos[1] - self.position[1])
        
    #     # Check if the healer is adjacent to a troop or a building
    #     if r + c == 1 or (r == 1 and c == 1):
    #         info = vmap[pos[0]][pos[1]]
    #         # # If it's a building, break it
    #         # if info == pt.TOWNHALL:
    #         #     self.break_building(pos[0], pos[1], V)
    #         #     return
    #         # else:
    #         x = int(info.split(':')[1])
    #         y = int(info.split(':')[2])
    #         target = V.get_unit_at(x, y)
    #             # If it's a troop and its health is less than max health, heal it
    #         if isinstance(target, troop) and target.health < target.max_health:
    #             self.attack_target(self, target, isKing,current_time) 
    #             return
    #     else:
    #         # Create a list of all troops that have less than max health
    #         wounded_troops = []
    #         for troop in V.get_all_units():
    #             if isinstance(troop, troop) and troop.health < troop.max_health:
    #                 wounded_troops.append(troop)
            
    #         # Sort the list of wounded troops based on their health
    #         sorted_wounded_troops = sorted(wounded_troops, key=lambda t: t.health)
            
    #         # Move towards the nearest wounded troop that's not adjacent to a building
    #         for troop in sorted_wounded_troops:
    #             r = abs(troop.position[0] - self.position[0])
    #             c = abs(troop.position[1] - self.position[1])
    #             # if r + c == 1:
    #             #     continue
    #             if r <= self.speed and c <= self.speed:
    #                 self.position = troop.position
    #                 return
    #             else:
    #                 if r > c:
    #                     if troop.position[0] > self.position[0]:
    #                         self.position[0] += self.speed
    #                     else:
    #                         self.position[0] -= self.speed
    #                 else:
    #                     if troop.position[1] > self.position[1]:
    #                         self.position[1] += self.speed
    #                     else:
    #                         self.position[1] -= self.speed
    #                 return

    # def break_building(self, x, y, V):
    #     target = None
    #     if(V.map[x][y] == pt.TOWNHALL):
    #         target = V.town_hall_obj
    #     else:
    #         all_buildings = collections.ChainMap(
    #             V.hut_objs, V.cannon_objs, V.wizard_tower_objs)
    #         target = all_buildings[(x, y)]
    #     self.attack_target(target)

    def attack_target(self, target, isKing,current_time):
        # if(self.destroyed == True):
        #     return

        if isKing == 1:
            target.deal_damage(self.attack,current_time)
        i = target.position[0] - 1
        j = target.position[1] - 1
        troops = barbarians+ archers + dragons + balloons +stealthArcher
        for row in range(i, i+3):
            for col in range(j, j+3):
                if(row < 0 or col < 0):
                    continue
                for troop in troops:
                    if(troop.position[0] == row and troop.position[1] == col):
                        troop.deal_damage(self.attack,current_time)


    def move(self, move_to_troops_pos, v):
        if not self.alive:
            return
        
        troops= barbarians+ archers + dragons + balloons +stealthArcher

        pos = move_to_troops_pos

        r = abs(move_to_troops_pos[0] - self.position[0])
        c = abs(move_to_troops_pos[1] - self.position[1])

        if(r == 0):
            if(pos[1] > self.position[1]):
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] + 1
                    self.position[1] += 1
                    if(abs(pos[1] - self.position[1]) == 1):
                        break
            else:
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] - 1
                    self.position[1] -= 1
                    if(abs(pos[1] - self.position[1]) == 1):
                        break
        elif(r > 1):
            if(pos[0] > self.position[0]):
                for i in range(self.speed):
                    r = self.position[0] + 1
                    c = self.position[1]
                    self.position[0] += 1
                    if(self.position[0] == pos[0]):
                        return
            else:
                for i in range(self.speed):
                    r = self.position[0] - 1
                    c = self.position[1]
                    self.position[0] -= 1
                    if(self.position[0] == pos[0]):
                        return
        elif(c > 1):
            if(pos[1] > self.position[1]):
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] + 1
                    self.position[1] += 1
                    if(self.position[1] == pos[1]):
                        return
            else:
                for i in range(self.speed):
                    r = self.position[0]
                    c = self.position[1] - 1
                    self.position[1] -= 1
                    if(self.position[1] == pos[1]):
                        return
        elif(r+c == 2):
            if(pos[0] > self.position[0]):
                    self.position[0] += 1
            else:
                    self.position[0] -= 1

        # Find the nearest friendly troop within the healing radius
        nearest_troop = None
        min_distance = math.inf
        for troop in troops:
            distance = math.sqrt((troop.position[0] - self.position[0]) ** 2 + (troop.position[1] - self.position[1]) ** 2)
            if distance <= self.attack_radius and distance < min_distance:
                nearest_troop = troop
                min_distance = distance
        
        if nearest_troop:
            # Move towards the nearest friendly troop
            dx = nearest_troop.position[0] - self.position[0]
            dy = nearest_troop.position[1] - self.position[1]
            distance = math.sqrt(dx ** 2 + dy ** 2)
            if distance <= self.speed:
                # Healer is close enough to heal the nearest troop
                self.attack_target(nearest_troop,False,current_time=10)
                # attack_target(self,nearest_troop,isKing,current_time)
            else:
                # Healer moves closer to the nearest troop
                self.position[0] += self.speed * dx / distance
                self.position[1] += self.speed * dy / distance

    def kill(self):
        self.alive = False

    def deal_damage(self, hit,current_time):
        if self.alive == False:
            return
        self.health -= hit
        if self.health <= 0:
            self.health = 0
            self.kill()

    # def heal(self, amount):
    #     if self.alive == False:
    #         return
    #     self.health += amount
    #     if self.health > self.max_health:
    #         self.health = self.max_health

    
    def kill(self):
        self.alive = False
        healers.remove(self)

    def deal_damage(self, hit,current_time):
        if(self.alive == False):
            return
        self.health -= hit
        if self.health <= 0:
            self.health = 0
            self.kill()

    def rage_effect(self):
        self.speed = self.speed*2
        self.attack = self.attack*2

    def heal_effect(self):
        self.health = self.health*1.5
        if self.health > self.max_health:
            self.health = self.max_health

def spawnHealer(pos):
    if(pt.troop_limit['healer'] <= troops_spawned['healer']):
        return

    # convert tuple to list
    pos = list(pos)
    heal = Healer(pos)
    troops_spawned['healer'] += 1
    healers.append(heal)

# def search_for_closest_troop(pos, vmap, prioritized):
#     closest_troop = None
#     closest_dist = 10000
#     flag = 0
#     for i in range(len(vmap)):
#         for j in range(len(vmap[i])):
#             item = vmap[i][j].split(':')[0]
#             if(prioritized == 0):
#                 if (item in pt.barbarians or item in pt.archers or item in pt.dragons or item in pt.balloons):
#                     dist = abs(i - pos[0]) + abs(j - pos[1])
#                     if(dist < closest_dist):
#                         flag = 1
#                         closest_dist = dist
#                         closest_troop = (i, j)
#             # else:
#             #     if (item == pt.CANNON or item == pt.WIZARD_TOWER):
#             #         dist = abs(i - pos[0]) + abs(j - pos[1])
#             #         if(dist < closest_dist):
#             #             flag = 1
#             #             closest_dist = dist
#             #             closest_building = (i, j)
#     if(flag == 0 and prioritized == 0):
#         return None
#     elif(flag == 0 and prioritized == 1):
#         return search_for_closest_troop(pos, vmap, 0)
#     else:
#         return closest_troop

# def move_healers( pos,V):
#     for hr in healers:
#         if(hr.alive == False):
#             continue
#         # closest_troop = search_for_closest_troop(hr.position, V.map, 0)
#         else:
#             hr.move(sorted_wounded_troops, V)

# def move_healers(pos, troops):
#     for healer in healers:
#         if not healer.alive:
#             continue

#         # Find the nearest friendly troop within the healing radius
#         nearest_troop = None
#         min_distance = math.inf
#         for troop in troops:
#             distance = math.sqrt((troop.position[0] - healer.position[0]) ** 2 + (troop.position[1] - healer.position[1]) ** 2)
#             if distance <= healer.attack_target and distance < min_distance:
#                 nearest_troop = troop
#                 min_distance = distance
        
#         if nearest_troop:
#             # Move towards the nearest friendly troop
#             dx = nearfest_troop.position[0] - healer.position[0]
#             dy = nearest_troop.position[1] - healer.position[1]
#             distance = math.sqrt(dx ** 2 + dy ** 2)
#             if distance <= healer.speed:
#                 # Healer is close enough to heal the nearest troop
#                 nearest_troop.heal(healer.attack)
#             else:
#                 # Healer moves closer to the nearest troop
#                 healer.position[0] += healer.speed * dx / distance
#                 healer.position[1] += healer.speed * dy / distance

def move_healers(V):
    for hr in healers:
        if(hr.alive == False):
            continue
        closest_troop = search_for_closest_ftroop(hr.position, V,hr)
        if(closest_troop == None):
            continue
        hr.move(closest_troop.position,V)

def search_for_closest_ftroop(pos, vmap, troopObject):
    closest_troop = None
    closest_dist = 10000000

    troops = barbarians+ archers + dragons + balloons +stealthArcher

    for troop in troops:
        if isinstance(troop, Healer):
            continue
        distance = math.sqrt((troop.position[0] - pos[0]) ** 2 + (troop.position[1] - pos[1]) ** 2)
        if distance < closest_dist:
            closest_troop = troop
            closest_dist = distance
        
    return closest_troop

# def move_healers(V):
#     for hr in healers:
#         if(hr.alive == False):
#             continue
#         closest_troop = search_for_closest_troop(hr.position, V.map, 0)
#         if(closest_troop == None):
#             continue
#         hr.move(closest_troop, V)


# def search_for_closest_troop(pos, vmap, prioritized):
#     closest_troop = None
#     closest_dist = 10000
#     flag = 0
#     for i in range(len(vmap)):
#         for j in range(len(vmap[i])):
#             item = vmap[i][j].split(':')[0]
#             if(prioritized == 0):
#                 if (item == pt.HUT or item == pt.CANNON or item == pt.TOWNHALL or item == pt.WIZARD_TOWER):
#                     dist = abs(i - pos[0]) + abs(j - pos[1])
#                     if(dist < closest_dist):
#                         flag = 1
#                         closest_dist = dist
#                         closest_troop = (i, j)
#             else:
#                 if (item == pt.CANNON or item == pt.WIZARD_TOWER):
#                     dist = abs(i - pos[0]) + abs(j - pos[1])
#                     if(dist < closest_dist):
#                         flag = 1
#                         closest_dist = dist
#                         closest_troop= (i, j)
#     if(flag == 0 and prioritized == 0):
#         return None
#     elif(flag == 0 and prioritized == 1):
#         return search_for_closest_troop(pos, vmap, 0)
#     else:
#         return closest_troop