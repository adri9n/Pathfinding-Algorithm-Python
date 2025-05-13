import random

class WorkerBee:
    def __init__(self, hivepos, worldpos):
        self.hivepos = hivepos
        self.worldpos = worldpos
        self.age = 0
        self.inhive = True
        self.targetcomb = None
        self.targetflower = None
        self.nectar = 0

    def set_target_world(self, pos):
        self.targetflower = pos
    def has_nectar(self):
        return self.nectar > 0

    def get_hivepos(self):
        return self.hivepos

    def get_worldpos(self):
        return self.worldpos

    def get_pos(self):
        return self.hivepos if self.inhive else self.worldpos

    def update_age(self):
        self.age += 1

    def leavehive(self, hive_world_pos):
        # Bee leaves the hive into the world when old enough
        if self.age >= 2 and self.inhive:
            self.inhive = False
            self.worldpos = hive_world_pos

    def touchflower(self):
        # Called when bee collects nectar at a flower cell
        self.nectar = 1
        self.targetflower = None

    def get_nearComb(self, hive):
        # Find closest comb cell in hive with space
        comb_cells = [(8,5),(6,5),(4,5),(2,5),(0,5)]
        x, y = self.get_pos()
        best, min_d = None, float('inf')
        for cx, cy in comb_cells:
            if hive[cx, cy] < 5:
                d = abs(cx - x) + abs(cy - y)
                if d < min_d:
                    best, min_d = (cx, cy), d
        self.targetcomb = best
        return best

    def find_nearest_flower(self, flowers):
        # Pick the closest non-empty flower
        x, y = self.get_worldpos()
        best_flower, min_d = None, float('inf')
        for f in flowers:
            if f.nectarValue() > 0:
                fx, fy = f.get_flowerpos()
                d = abs(fx - x) + abs(fy - y)
                if d < min_d:
                    best_flower, min_d = f, d
        if best_flower:
            self.targetflower = best_flower.get_flowerpos()
        return best_flower

    def step_change(self, occupied_positions, worldX, worldY):
        # If carrying nectar and just stepped onto the comb cell, re-enter hive
        if not self.inhive and self.nectar > 0 and self.worldpos == self.targetcomb:
            self.inhive = True
            self.hivepos = self.worldpos
            return

        # Otherwise only move after age>=2
        if self.age < 2:
            return

        # Decide which target to move toward
        target = self.targetcomb if self.inhive else self.targetflower
        if not target:
            return

        x, y = self.get_pos()
        tx, ty = target
        dx = (1 if tx > x else -1 if tx < x else 0)
        dy = (1 if ty > y else -1 if ty < y else 0)

        # Try the primary step, then fallback directions
        moves = [
            (x+dx, y+dy),
            (x+1, y), (x-1, y),
            (x, y+1), (x, y-1)
        ]
        for nx, ny in moves:
            if 0 <= nx < worldX and 0 <= ny < worldY and (nx, ny) not in occupied_positions:
                if self.inhive:
                    self.hivepos = (nx, ny)
                else:
                    self.worldpos = (nx, ny)
                break

    def deposit_nectar(self, hive):
        # Deposit carried nectar into comb
        if self.targetcomb and self.nectar > 0:
            cx, cy = self.targetcomb
            if hive[cx, cy] < 5:
                hive[cx, cy] += 1
                self.nectar = 0
                self.targetcomb = None


class QueenBee:
    def __init__(self):
        self.hivepos = (5,5)
        self.inhive = True

    def get_hivepos(self):
        return self.hivepos

    def step_change(self, *args):
        pass  # queen doesn't move


class DroneBee:
    def __init__(self, hivepos):
        self.hivepos = hivepos
        self.inhive = True

    def get_hivepos(self):
        return self.hivepos

    def step_change(self, *args):
        pass  # drones don't move


class Flower:
    def __init__(self, worldX, worldY):
        self.x = random.randint(1, worldX-1)
        self.y = random.randint(1, worldY-1)
        self.nectar = random.randint(1,5)

    def get_flowerpos(self):
        return (self.x, self.y)

    def nectarValue(self):
        return self.nectar

    def collect_nectar(self):
        if self.nectar > 0:
            self.nectar -= 1


class Tree:
    def __init__(self, worldX, worldY):
        self.x = random.randint(1, worldX-1)
        self.y = random.randint(1, worldY-1)

    def get_treepos(self):
        return (self.x, self.y)


class Barrier:
    def __init__(self, worldX, worldY):
        self.x = random.randint(0, worldX-1)
        self.y = random.randint(0, worldY-1)

    def get_pos(self):
        return (self.x, self.y)