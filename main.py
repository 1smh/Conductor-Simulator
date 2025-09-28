from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader
from ursina.prefabs.ursfx import ursfx

from group import Group

import audioManager as am
app = Ursina()

random.seed(0)
Entity.default_shader = lit_with_shadows_shader

ground = Entity(model='concerthallv3', position=(-150.75,-5,-310.75), scale=15, texture='grass', texture_scale=(4,4), rotation=(0,0,180))
ground.collider = 'mesh'

editor_camera = EditorCamera(enabled=False, ignore_paused=True)
player = FirstPersonController(model='cube', position=(0,100,-10), color=color.orange, origin_y=-.5, speed=0)
print(player.position)
#player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))
# player.gravity = False

gun = Entity(model='cube', parent=camera, position=(.2,-.25,.25), scale=(.01,.01,1.5), rotation=(0,10,0), origin_z=-.5, color=color.black, on_cooldown=False)
gun.muzzle_flash = Entity(parent=gun, z=1, world_scale=.5, model='quad', color=color.yellow, enabled=False)
tempoMarker = Entity(model="sphere", parent=camera, position = (0,0,5), color=color.red, scale=(1,1,1), enabled=False)


health_bar = Entity(y=3, x=0, z=-20, model='cube', color=color.red, world_scale=(15,1,1))
health_bar.world_scale_x = 15
health_bar.alpha = 1

def spawn_conductor_platform():
    platform = Entity(model='cube', scale=(2,2,4), color=color.gray, position=(0,1,-6))
    platform_top = Entity(parent=platform, model='cube', scale=(1,0.2,1), color=color.light_gray, position=(0,.6,0), texture='white_cube', texture_scale=(4,4))
    podium = Entity(parent=platform, model='cube', scale=(0.5,0.5,0.25), color=color.brown, position=(0,0.9,0.3), texture='white_cube', texture_scale=(4,4), rotation=(0,0,0))
    
# spawn_conductor_platform()

def update():
    if held_keys['q']:
        shoot()

    # Configurable variables
    TEMPO_RATE = 1          # seconds between tempo windows
    TEMPO_WINDOW = 0.2      # seconds `window to react
    HEALTH_DECREASE = 1     # amount to decrease health

    if not hasattr(update, 'tempo_window_timer'):
        update.tempo_window_timer = 0
        update.tempo_window_allowed = False

    update.tempo_window_timer += time.dt

    if update.tempo_window_timer >= TEMPO_RATE:
        update.tempo_window_allowed = True
        update.tempo_window_timer = 0
        update.tempo_window_opened = time.time()

    if update.tempo_window_allowed:
        tempoMarker.enabled = True
        tempoMarker.color = color.red
        tempoMarker.scale = ((1 - (time.time() - update.tempo_window_opened) / TEMPO_WINDOW)/2,
                             (1 - (time.time() - update.tempo_window_opened) / TEMPO_WINDOW)/2,
                             (1 - (time.time() - update.tempo_window_opened) / TEMPO_WINDOW)/2)
        if time.time() - update.tempo_window_opened > TEMPO_WINDOW:
            health_bar.world_scale_x -= HEALTH_DECREASE
            if health_bar.world_scale_x <= 0:
                health_bar.world_scale_x = 0.1
            update.tempo_window_allowed = False
            tempoMarker.enabled = False
            camera.shake(duration=0.2, magnitude=0.6)
        elif held_keys['left mouse']:
            update.tempo_window_allowed = False
            tempoMarker.color = color.green
    
    # if not hasattr(update, 'note_timer'):
    #     update.note_timer = 0
    # update.note_timer += time.dt
    # if update.note_timer > random.uniform(0.5, 1):  # spawn every 1 second
    #     Note(x=random.uniform(-20,20), z=random.uniform(2,10), y=random.uniform(4,20))
    #     update.note_timer = 0
    offsets = []
    for group in orchestra:
        offsets.append(group.determineAudio(0.0)) #beat align is currently 0.0
    am.determineAudio(offsets) 


#repurpose for selecting musicians
def shoot():
    if not gun.on_cooldown:
        # print('shoot')
        gun.on_cooldown = True
        gun.muzzle_flash.enabled=True
        gun.rotation = (0,0,0)
        #ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)], volume=0.5, wave='noise', pitch=random.uniform(-13,-12), pitch_change=-12, speed=3.0)
        invoke(gun.muzzle_flash.disable, delay=0.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)
        invoke(setattr, gun, 'rotation', (0,10,0), delay=0.1)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.blink(color.red)
            mouse.hovered_entity.hp -= 1
        # health_bar.world_scale_x += 5



class Note(Entity):
    def __init__(self, **kwargs):
        model_choice = random.choice(['uploads_files_2463307_Note+Eight', 'uploads_files_2463288_Eighth+note'])
        super().__init__(parent=shootables_parent, model=model_choice, origin_y=-.5, color=color.cyan, collider='box', **kwargs)
        self.max_hp = 1
        self.hp = self.max_hp
        self.initial_scale = 0.5
        self.scale_y = self.initial_scale
        self.scale_x = self.initial_scale
        self.scale_z = self.initial_scale

    def update(self):
        """Main game update loop"""
        if not self.input_enabled:
            return



def pause_input(key):
    if key == 'tab':    # press tab to toggle edit/play mode
        editor_camera.enabled = not editor_camera.enabled

        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position

        application.paused = editor_camera.enabled

#chris
am.start()
orchestra = []
drum = Group(9, -6.5, 8, "drumA")
bass = Group(12, -6.5, 9, "bassC")
trumpet = Group(15, -6, 12, "trumpetB")
trumpet2 = Group(18, -6, 13, "trumpetD")
orchestra.append(drum)
orchestra.append(bass)
orchestra.append(trumpet)
orchestra.append(trumpet2)
        


"""
def spawn_musicians(radius, height, count, group):
    center = Vec3(0,height,-10)
    start_angle = math.radians(20)
    end_angle = math.radians(160)
    for i in range(count):
        angle = start_angle + (end_angle - start_angle) * i / (count - 1)
        x = center.x + radius * math.cos(angle)
        z = center.z + radius * math.sin(angle)
        group.append(Musician(player, x=x, z=z, y=center.y))
    return group


drum = []
bass = []
trumpet = []


# Spawn 5 enemies in a smaller semicircle and 10 in a larger semicircle

"""
pause_handler = Entity(ignore_paused=True, input=pause_input)


sun = DirectionalLight()
sun.look_at(Vec3(1,-1,-1))
Sky()

app.run()
