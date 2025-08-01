from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# 地板
ground = Entity(model='plane', texture='white_cube', texture_scale=(50,50),
                collider='box', scale=50, color=color.gray)

# 敵人
targets = []
for i in range(10):
    target = Entity(model='cube', color=color.red,
                    position=(random.uniform(-20,20),1,random.uniform(-20,20)),
                    scale=2, collider='box')
    targets.append(target)

# 玩家
player = FirstPersonController()
player.gravity = 0.5
player.cursor.visible = False
player.speed = 5  # 初始走路速度

# 顯示 FPS 和準心
window.fps_counter.enabled = True
Entity(model='quad', parent=camera.ui, color=color.black, scale=0.01)

# 子彈列表
bullets = []

def shoot():
    # 創建子彈：位置為鏡頭，方向為 forward
    bullet = Entity(
        model='sphere',
        color=color.yellow,
        scale=0.2,
        position=camera.world_position + camera.forward * 1,
        collider='sphere',
        direction=camera.forward,
        speed=25
    )
    bullets.append(bullet)

def update():
    # Shift 奔跑功能
    if held_keys['shift']:
        player.speed = 10  # 奔跑速度
    else:
        player.speed = 5   # 正常速度

    # 開槍
    if held_keys['left mouse']:
        shoot()

    # 子彈移動與碰撞偵測
    for bullet in bullets[:]:  # 複製一份避免刪除時報錯
        bullet.position += bullet.direction * bullet.speed * time.dt

        hit_info = bullet.intersects()
        if hit_info.hit:
            if hit_info.entity in targets:
                destroy(hit_info.entity)
                targets.remove(hit_info.entity)
            destroy(bullet)
            bullets.remove(bullet)

app.run()
