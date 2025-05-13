import matplotlib.pyplot as plt
import numpy as np
import random
import time
from buzzness import WorkerBee, QueenBee, DroneBee, Flower, Tree, Barrier

# -- Input with exponential backoff --
def prompt_int(msg, low, high):
    delay = 0.5
    while True:
        try:
            val = int(input(msg))
            if low <= val <= high:
                return val
            print(f"Value must be between {low} and {high}.")
        except ValueError:
            print("Please enter an integer.")
        time.sleep(delay)
        delay = min(delay * 2, 5)

# 1. Read user parameters
num_bees    = prompt_int("Enter number of worker bees (1–6): ", 1, 6)
num_flower  = prompt_int(f"Enter number of flowers (1–{num_bees}): ", 1, num_bees)
sim_length  = prompt_int("Enter simulation length (1–100): ", 1, 100)

# 2. Grids
hiveX, hiveY = 11, 10
hive = np.zeros((hiveX, hiveY), dtype=int)
hive[5, ::2] = np.random.randint(1, 6, size=5)
hive[0:5, :]   = 10
hive[6:11, :]  = 10

worldX, worldY = 50, 40
world = np.full((worldX, worldY), 5, dtype=int)

# 3. Positions & Entities
world_centre = (worldX // 2, worldY // 2)
hive_position = (worldX // 4, worldY // 4)  # where bees enter/exit hive in the world

workers = [WorkerBee(pos, world_centre)
           for pos in [(0,6),(0,4),(0,2),(10,6),(10,4),(10,2)][:num_bees]]
queen   = QueenBee()
drones  = [DroneBee(pos) for pos in [(3,7),(7,7),(3,3),(7,3)]]
flowers = [Flower(worldX, worldY) for _ in range(num_flower)]
trees   = [Tree(worldX, worldY) for _ in range(random.randint(1,10))]
barriers= [Barrier(worldX, worldY) for _ in range(random.randint(1,10))]

# 4. Compute SPEED to finish within sim_length
import math
dists = [abs(world_centre[0]-f.get_flowerpos()[0]) + abs(world_centre[1]-f.get_flowerpos()[1])
         for f in flowers]
maxd    = max(dists) if dists else 0
roundtrip = 2*maxd
SPEED     = max(1, math.ceil(roundtrip / sim_length))
print(f"[Info] Moving bees at {SPEED} steps per frame to finish within {sim_length} timesteps.")

# 5. Simulation
plt.ion()
fig, (ax_hive, ax_world) = plt.subplots(1,2, figsize=(14,6))

# initial one-to-one flower assignment
claimed = set()
for i,w in enumerate(workers):
    if i < len(flowers):
        f = flowers[i]
        w.targetflower = f.get_flowerpos()
        claimed.add(f)

hive_width = 3
hive_height = 3

for t in range(sim_length):
    ax_hive.clear(); ax_world.clear()

    # draw hive grid
    ax_hive.imshow(hive.T, cmap="YlOrBr", origin="lower", vmin=0, vmax=10)
    # move & target logic
    occupied = {queen.get_hivepos()} | {d.get_hivepos() for d in drones} | {b.get_pos() for b in barriers}
    for w in workers:
        w.update_age()
        # leave hive and choose comb
        if w.inhive and w.age>=2 and w.targetcomb is None:
            w.leavehive(hive_position)
            w.get_nearComb(hive)
        # choose flower if in world
        if not w.inhive and w.targetflower is None:
            unclaimed = [f for f in flowers if f not in claimed]
            if unclaimed:
                flower_obj = w.find_nearest_flower(unclaimed)
                if flower_obj: claimed.add(flower_obj)
        # step SPEED times
        for _ in range(SPEED):
            w.step_change(occupied, worldX, worldY)

    # nectar collection & set return target
    for w in workers:
        if not w.inhive and w.targetflower:
            for f in flowers[:]:
                if w.get_worldpos() == f.get_flowerpos():
                    f.collect_nectar()
                    if f.nectarValue()==0:
                        # clear stale targets
                        for o in workers:
                            if o.targetflower == (f.x, f.y): o.targetflower=None
                        flowers.remove(f)
                        claimed.discard(f)
                    w.touchflower()
                    w.set_target_world(hive_position)
                    w.targetcomb = hive_position
                    break

    # check for actual return into hive square
    for w in workers:
        if (not w.inhive) and w.has_nectar() and w.get_worldpos() == hive_position:
            w.inhive = True
            w.hivepos = hive_position

    # deposit nectar
    for w in workers:
        if w.inhive and w.has_nectar():
            w.deposit_nectar(hive)

    # plot hive occupants
    hx = [w.get_hivepos()[0] for w in workers]
    hy = [w.get_hivepos()[1] for w in workers]
    ax_hive.scatter(hx, hy, c='yellow', marker='o', label='Workers')
    qx,qy = queen.get_hivepos()
    ax_hive.scatter(qx,qy, c='cyan', marker='D', label='Queen')
    dx = [d.get_hivepos()[0] for d in drones]
    dy = [d.get_hivepos()[1] for d in drones]
    ax_hive.scatter(dx,dy, c='cyan', marker='^', label='Drones')
    ax_hive.set_title("Hive")
    ax_hive.legend(loc='upper left')

    # plot world
    ax_world.imshow(world.T, cmap="tab20", origin="lower", vmin=1, vmax=20)
    fx = [f.get_flowerpos()[0] for f in flowers]
    fy = [f.get_flowerpos()[1] for f in flowers]
    ax_world.scatter(fx,fy, c='yellow', marker='*', label='Flowers')
    tx = [t.get_treepos()[0] for t in trees]
    ty = [t.get_treepos()[1] for t in trees]
    ax_world.scatter(tx,ty, c='green', marker='+', label='Trees')
    bx = [b.get_pos()[0] for b in barriers]
    by = [b.get_pos()[1] for b in barriers]
    ax_world.scatter(bx,by, c='black', marker='X', label='Barriers')
    # hive square in world
    ax_world.add_patch(plt.Rectangle(hive_position, hive_width, hive_height,
                                     fill=True, color='lightgray', label='Hive'))
    wx = [w.get_worldpos()[0] for w in workers if not w.inhive]
    wy = [w.get_worldpos()[1] for w in workers if not w.inhive]
    ax_world.scatter(wx,wy, c='yellow', marker='o', label='Workers')
    ax_world.set_title("World")
    ax_world.legend(loc='upper left')

    fig.suptitle(f"Timestep {t+1}")
    plt.pause(0.5)

plt.ioff()
plt.show()
