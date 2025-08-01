from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import time
import random

app = Ursina()

# === 地板 ===
class Ground(Entity):
    def __init__(self):
        super().__init__(
            model='plane',
            texture='white_cube',
            texture_scale=(50, 50),
            scale=50,
            collider='box',
            color=color.gray
        )

# === 玩家 ===
class MyPlayer(FirstPersonController):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hp = 100
        self.base_speed = 5
        self.run_speed = 10
        self.cursor.visible = False
        self.coyote_timer = 0
        self._was_pressing_space = False

    def update(self):
        super().update()
        self.speed = self.run_speed if held_keys['shift'] else self.base_speed

        # --- coyote time: 落地一瞬間容許跳躍
        if self.grounded:
            self.coyote_timer = 0.12
        else:
            self.coyote_timer -= time.dt

        if held_keys['space'] and not self._was_pressing_space and self.coyote_timer > 0:
            self.jump()
            self.coyote_timer = 0

        self._was_pressing_space = held_keys['space']

# === 敵人 ===
class Enemy(Entity):
    def __init__(self, player):
        pos = Vec3(random.uniform(-20, 20), 1, random.uniform(-20, 20))
        super().__init__(
            model='cube',
            color=color.red,
            position=pos,
            scale=2,
            collider='box'
        )
        self.player = player
        self.hp = 3
        self.hp_text = Text(
            text=str(self.hp),
            scale=1.5,
            world_parent=self,
            position=(0, self.scale_y + 0.5, 0),
            billboard=True,
            color=color.white,
            origin=(0, 0)
        )

    def update(self):
        self.look_at(self.player)
        if distance(self.position, self.player.position) > 1.5:
            direction = (self.player.position - self.position).normalized()
            self.position += direction * time.dt * 2
        # 地板防掉落
        ground_hit = raycast(self.world_position + Vec3(0, 0.5, 0), Vec3(0, -1, 0), distance=1.5, ignore=[self])
        if ground_hit.hit:
            self.y = max(self.y, ground_hit.world_point.y + self.scale_y / 2)

    def take_damage(self, amount):
        self.hp -= amount
        self.hp_text.text = str(self.hp)
        if self.hp <= 0:
            destroy(self.hp_text)
            destroy(self)
            return True
        return False

# 場景初始化
ground = Ground()
player = MyPlayer()

window.fps_counter.enabled = True
Entity(model='quad', parent=camera.ui, color=color.black, scale=0.01)
player_hp_text = Text(
    text=f'HP: {player.hp}',
    parent=camera.ui,
    position=(-0.75, -0.45),
    origin=(0, 0),
    scale=1.5,
    color=color.lime
)

enemies = [Enemy(player) for _ in range(10)]
bullets = []
shoot_cooldown = 0.2
last_shot_time = 0

def shoot():
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
    global last_shot_time

    player_hp_text.text = f'HP: {player.hp}'

    for enemy in enemies[:]:
        enemy.update()

    if held_keys['left mouse'] and time.time() - last_shot_time > shoot_cooldown:
        shoot()
        last_shot_time = time.time()

    for bullet in bullets[:]:
        bullet.position += bullet.direction * bullet.speed * time.dt
        hit_info = bullet.intersects()
        if hit_info.hit and isinstance(hit_info.entity, Enemy):
            killed = hit_info.entity.take_damage(1)
            if killed:
                enemies.remove(hit_info.entity)
            destroy(bullet)
            bullets.remove(bullet)

app.run()
