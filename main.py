from direct.showbase.ShowBase import ShowBase
from panda3d.core import LVector3, LColor, PointLight, AmbientLight, DirectionalLight
from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectGui import DirectFrame, DirectButton
from direct.task import Task
import random

class PvZNurbek3D(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Kamera va Fon sozlamalari
        self.setBackgroundColor(0.01, 0.05, 0.01) # To'q yashil/qora fon
        self.disableMouse()
        self.camera.setPos(0, -45, 35)
        self.camera.setHpr(0, -40, 0)

        # O'yin o'zgaruvchilari
        self.sun = 500
        self.plants = []
        self.zombies = []
        self.mowers = []
        self.projectiles = []
        self.grid_rows = 5
        self.grid_cols = 9
        self.cell_size = 5

        # UI Elementlari (Neon dizayn)
        self.setup_ui()
        
        # Dunyoni qurish
        self.create_lawn()
        self.setup_lights()
        
        # Harakatlar/Tasklar
        self.taskMgr.add(self.update, "update")
        self.taskMgr.doMethodLater(5, self.spawn_zombie_task, "zombie_spawn")
        
    def setup_ui(self):
        """Neon uslubidagi interfeys"""
        self.sun_text = OnscreenText(text=f"SUN: {self.sun}", pos=(-1.1, 0.9), 
                                     scale=0.08, fg=(1, 1, 0, 1), shadow=(0, 0, 0, 1))
        
        # O'simliklar tanlash paneli (Pastda)
        self.menu = DirectFrame(frameColor=(0, 0.2, 0, 0.8),
                                frameSize=(-0.8, 0.8, -0.15, 0.15),
                                pos=(0, 0, -0.85))
        
        # Tugmalar (Oddiyroq qilib yaratilgan)
        self.btn_peashooter = DirectButton(text="PEA (100)", scale=0.05, pos=(-0.5, 0, 0),
                                           command=self.select_plant, extraArgs=["peashooter", 100])
        self.btn_sunflower = DirectButton(text="SUN (50)", scale=0.05, pos=(-0.2, 0, 0),
                                          command=self.select_plant, extraArgs=["sunflower", 50])
        
    def setup_lights(self):
        """Atmosferani yaratish uchun chiroqlar"""
        alight = AmbientLight('alight')
        alight.setColor((0.2, 0.4, 0.2, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)

        dlight = DirectionalLight('dlight')
        dlight.setColor((0.4, 1, 0.4, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(0, -60, 0)
        self.render.setLight(dlnp)

    def create_lawn(self):
        """5x9 Maydonni yaratish"""
        for r in range(self.grid_rows):
            for c in range(self.grid_cols):
                # Har bir katak uchun model (Box o'rnida oddiyroq model)
                tile = self.loader.loadModel("models/box")
                tile.reparentTo(self.render)
                tile.setScale(2.4, 2.4, 0.1)
                tile.setPos((c - 4) * self.cell_size, (r - 2) * self.cell_size, 0)
                
                # Ranglarni almashtirish (Shaxmat taxtasi kabi)
                if (r + c) % 2 == 0:
                    tile.setColor(0.1, 0.3, 0.1, 1)
                else:
                    tile.setColor(0.05, 0.2, 0.05, 1)
            
            self.create_mower(r)

    def create_mower(self, row):
        """O't o'radigan mashina (Lawnmower)"""
        mower = self.loader.loadModel("models/box")
        mower.reparentTo(self.render)
        mower.setScale(1, 1.5, 0.5)
        mower.setPos(-25, (row - 2) * self.cell_size, 0.5)
        mower.setColor(0.8, 0, 0, 1) # Qizil rang
        self.mowers.append({"model": mower, "row": row, "active": False})

    def spawn_zombie_task(self, task):
        row = random.randint(0, 4)
        zombie = self.loader.loadModel("models/box")
        zombie.reparentTo(self.render)
        zombie.setScale(0.8, 0.8, 2.5)
        zombie.setPos(25, (row - 2) * self.cell_size, 1.25)
        zombie.setColor(0.3, 0.2, 0.1, 1) # Zombi jigarrang tanasi
        
        self.zombies.append({"model": zombie, "row": row, "hp": 100, "speed": 0.05})
        return task.again

    def select_plant(self, type, cost):
        self.selected_type = type
        self.selected_cost = cost
        print(f"Selected: {type}")

    def update(self, task):
        dt = globalClock.getDt()

        # Zombilar harakati
        for z in self.zombies:
            z["model"].setX(z["model"].getX() - z["speed"])
            
            # Lawnmower bilan to'qnashuv
            for m in self.mowers:
                if m["row"] == z["row"] and not m["active"]:
                    if abs(z["model"].getX() - m["model"].getX()) < 2:
                        m["active"] = True

        # Lawnmower harakati
        for m in self.mowers:
            if m["active"]:
                m["model"].setX(m["model"].getX() + 0.5)
                # Yo'lidagi zombilarni o'ldirish
                for z in self.zombies:
                    if z["row"] == m["row"] and abs(z["model"].getX() - m["model"].getX()) < 3:
                        z["hp"] = 0
                        z["model"].hide()

        return Task.cont

app = PvZNurbek3D()
app.run()
