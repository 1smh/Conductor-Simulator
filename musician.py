from ursina import *
from ursina.prefabs.health_bar import HealthBar
from ursina.prefabs.first_person_controller import FirstPersonController


shootables_parent = Entity()
mouse.traverse_target = shootables_parent

class Musician(Entity):
    
    def __init__(self,  **kwargs ):
        super().__init__(parent=shootables_parent, model='cube', scale_y=2, origin_y=-.5, color=color.light_gray, collider='box', **kwargs)
        self.health_bar = Entity(parent=self, y=1.2, model='cube', color=color.red, world_scale=(1.5,.1,.1))
        self.max_hp = 1
        self.hp = self.max_hp
        self.instrument = Entity(parent=self, model='violinprefab', position=(-0.4,0.8,1), scale=0.05, rotation=(-80,90,-60))
        #chris
         # Musician state
        self.bad_actor = False
        self.last_bad_actor_check = 0.0
        self.bad_actor_check_interval = 0.5  # seconds
        self.performance = 1.0  # 1.0 = perfect, 0.0 = terrible
        self.bad_actor_threshold = random.uniform(1.0, 5.0)

        self.active = True
        
        self.fumble = 0


    # def update(self):
    #     self.look_at_2d(player.position, 'y')

    def update(self):
        self.player = Entity( position=(0,100,-10), origin_y=-.5, speed=0)

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)
        self.look_at_2d(self.player.position, 'y')
        # hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 30, ignore=(self,))
        # print(hit_info.entity)

        if not self.active:
            return
            
        # Check for bad actor status every 5 seconds instead of every frame
        current_time = time.time()
        # print("Fumble:", self.fumble, "Bad Actor Threshold:", self.bad_actor_threshold)
        if current_time - self.last_bad_actor_check >= self.bad_actor_check_interval:
            # print("Fumble:", self.fumble, "Bad Actor Threshold:", self.bad_actor_threshold)
            if self.bad_actor_threshold <= self.fumble and not self.bad_actor:
                #print("bad")
                self.become_bad_actor()
            elif self.fumble < self.bad_actor_threshold and self.bad_actor:
                self.bad_actor = False  # Recover from bad actor status
                self.fumble = 0  # Reset fumble on recovery
            self.last_bad_actor_check = current_time
            
        # Visual feedback for bad actors
        if self.bad_actor:
            # Make bad actors more visually obvious
            self.color = color.red
        else :
            self.color = color.light_gray
        
    def become_bad_actor(self):
        self.performance = random.uniform(0.0, 0.5)
        self.bad_actor = True
        self.color=color.red

    def improve_performance(self, beatAlign):
        if(beatAlign > 0):
            if not self.bad_actor:
                self.performance = 1.0
            self.fumble -= beatAlign
        else:
            self.fumble += 0.5
        

        
    def get_audio_offset(self):
        """Calculate how much this musician's audio should be offset"""
        if not self.active:
            return 0.0
        return self.performance


    @property
    def hp(self):
        return self._hp

    #upon setting hp anytime it appears this would run
    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:

            self.active = False
            self.bad_actor = False
            self.color = color.black
            self.scale = (0.5, 0.5, 0.5)
            return

        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1
    