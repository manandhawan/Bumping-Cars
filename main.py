from direct.gui.DirectGui import *
import direct.directbase.DirectStart
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import CollisionTraverser,CollisionNode,CollisionHandlerEvent
from panda3d.core import CollisionHandlerQueue,CollisionRay,CollisionSphere
from panda3d.core import Filename,AmbientLight,DirectionalLight
from panda3d.core import PandaNode,NodePath,Camera,TextNode
from panda3d.core import Vec3,Vec4,BitMask32
from panda3d.core import WindowProperties
from panda3d.ai import *
from direct.showbase.ShowBase import ShowBase
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
from direct.showbase.DirectObject import DirectObject
from pandac.PandaModules import TransparencyAttrib
from direct.interval.IntervalGlobal import Sequence
import random, sys, os, math


SPEED = 0.5
BAR_WIDTH = 0.6


numObjText = OnscreenText(text = "Health left: 100", style = 1, fg = (1, 1, 1, 1),
                            pos = (0.85, 0.75), scale = 0.05,
                            mayChange = 1)
numObjText1 = OnscreenText(text = "Points Scored: 0", style = 1, fg = (1, 1, 1, 1),
                            pos = (0.85, 0.65), scale = 0.05,
                            mayChange = 1)       

healthBar = OnscreenImage(image="models/healthBar.png",pos = (0.85,0,0.85), scale = (BAR_WIDTH,0.2,0.2))
healthBar.setTransparency(TransparencyAttrib.MAlpha)

# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1,1,1,1),
                        pos=(-1.3, pos), align=TextNode.ALeft, scale = .05)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1,1,1,1),
                        pos=(1.3,-0.95), align=TextNode.ARight, scale = .07)

#Print Num Objects
def printHealthObj(n):
	numObjText['text'] = "Health left: " + (str)(n)
	
def printPointObj(n):
	numObjText1['text'] = "Points Scored: " + (str)(n)
	
class World(DirectObject):

    def __init__(self):
        self.keyMap = {"left":0, "right":0, "forward":0, "back":0, "cam-left":0, "cam-right":0}
        self.flag1=0
        self.flag2=0
        self.flag3=0 
        self.flag4=0
        self.count=0
        self.health = 100
        self.points = -5
        self.flagd=1
        self.player_points = 0
        base.win.setClearColor(Vec4(0,0,0,1))
        
        self.mySound=base.loader.loadSfx("sounds/trial.mp3")
        self.mySound.play()
        
        self.title = addTitle("Bumping Cars")
       
		#Full Screen
        props = WindowProperties.getDefault()
        w=base.pipe.getDisplayWidth()
        h=base.pipe.getDisplayHeight()
        props.setSize(w,h)
        props.setFullscreen(True)
        props.setCursorHidden(True)
        base.win.requestProperties(props) 

		# Load World
        self.environ = loader.loadModel("models/world.egg")      
        self.environ.reparentTo(render)
        self.environ.setPos(0,0,0)
        
        #Load Sky
        self.sky = loader.loadModel("models/clouds.egg")
        self.sky.reparentTo(render)
        self.sky.setPos(60,0,-450)
        
        
        # Create Player Car
        carStartPos = self.environ.find("**/start_point").getPos()
        self.car = Actor("models/carnsx")
        self.car.reparentTo(render)
        self.car.setScale(0.25)
        #self.car.place()
        self.car.setPos(carStartPos)
        
        # Create Enemy Car 1
        enemyCarStartPos1 = (-108,-1,-.5)
        self.car1 = Actor("models/enemy_cars/monstercar/carmonster")
        self.car1.reparentTo(render)
        self.car1.setScale(0.25)
        #self.car1.place()
        self.car1.setPos(enemyCarStartPos1)
        
        # Create Enemy Car 2
        enemyCarStartPos2 = (-104,-26,-.02)
        self.car2 = Actor("models/enemy_cars/yugo/yugo")
        self.car2.reparentTo(render)
        self.car2.setScale(0.15)
        #self.car2.place()
        self.car2.setPos(enemyCarStartPos2)
        
        # Create Enemy Car 3
        enemyCarStartPos3 = (-111,-26,0)
        self.car3 = Actor("models/enemy_cars/truck/cartruck")
        self.car3.reparentTo(render)
        self.car3.setScale(0.25)
        #self.car3.place()
        self.car3.setPos(enemyCarStartPos3)
        
        # Create Enemy Car 4
        enemyCarStartPos4 = (-111,-2,-.5)
        self.car4 = Actor("models/enemy_cars/truck/cartruck-purple")
        self.car4.reparentTo(render)
        self.car4.setScale(0.25)
        #self.car4.place()
        self.car4.setPos(enemyCarStartPos4)
        

        # Create a floater object.  We use the "floater" as a temporary
        # variable in a variety of calculations.
        
        self.floater = NodePath(PandaNode("floater"))
        self.floater.reparentTo(render)

        # Accept the control keys for movement and rotation

        self.accept("escape", sys.exit)
        self.accept("a", self.setKey, ["cam-left",1])
        self.accept("s", self.setKey, ["cam-right",1])
        self.accept("arrow_up",self.setKey, ["forward",1])
        self.accept("arrow_left",self.setKey, ["left",1])
        self.accept("arrow_down",self.setKey, ["back",1])
        self.accept("arrow_right",self.setKey, ["right",1])
        self.accept("a-up", self.setKey, ["cam-left",0])
        self.accept("s-up", self.setKey, ["cam-right",0])
        self.accept("arrow_up-up",self.setKey, ["forward",0])
        self.accept("arrow_left-up",self.setKey, ["left",0])
        self.accept("arrow_right-up",self.setKey, ["right",0])
        self.accept("arrow_down-up",self.setKey, ["back",0])

        taskMgr.add(self.move,"moveTask")

        # Game state variables
        self.isMoving = False

        # Set up the camera
        
        base.disableMouse()
        base.camera.setPos(self.car.getX(),self.car.getY()+10,2)
        
        # Create some lighting
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor(Vec4(.3, .3, .3, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(Vec3(-5, -5, -5))
        directionalLight.setColor(Vec4(1, 1, 1, 1))
        directionalLight.setSpecularColor(Vec4(1, 1, 1, 1))
        render.setLight(render.attachNewNode(ambientLight))
        render.setLight(render.attachNewNode(directionalLight))
        
        # AI
        self.AIworld = AIWorld(render)
 
        # AI Car 1
        self.AIchar1 = AICharacter("car1",self.car1, 70, 0.1, 3)
        self.AIworld.addAiChar(self.AIchar1)
        self.AIbehaviors1 = self.AIchar1.getAiBehaviors()
        self.AIbehaviors1.pursue(self.car)
        
        # AI Car 2
        self.AIchar2 = AICharacter("car2",self.car2, 180, 0.1, 1)
        self.AIworld.addAiChar(self.AIchar2)
        self.AIbehaviors2 = self.AIchar2.getAiBehaviors()
        self.AIbehaviors2.pursue(self.car4)
        
        # AI Car 3
        self.AIchar3 = AICharacter("car3",self.car3, 70, 0.1, 3)
        self.AIworld.addAiChar(self.AIchar3)
        self.AIbehaviors3 = self.AIchar3.getAiBehaviors()
        self.AIbehaviors3.pursue(self.car)
        
        # AI Car 4
        self.AIchar4 = AICharacter("car4",self.car4, 200, 0.5, 2)
        self.AIworld.addAiChar(self.AIchar4)
        self.AIbehaviors4 = self.AIchar4.getAiBehaviors()
        self.AIbehaviors4.pursue(self.car3)
        
        # Obstacle avoidance
        self.AIbehaviors1.obstacleAvoidance(1.0)
        self.AIworld.addObstacle(self.car2)
        self.AIworld.addObstacle(self.car3)
        self.AIworld.addObstacle(self.car4)
        
        self.AIbehaviors2.obstacleAvoidance(1.0)
        self.AIbehaviors3.obstacleAvoidance(1.0)
        self.AIbehaviors4.obstacleAvoidance(1.0)
          
        #AI World update        
        taskMgr.add(self.AIUpdate,"AIUpdate")
        
    
        self.cTrav = CollisionTraverser()
        #self.cTrav.showCollisions(render)
       
        self.ralphGroundRay = CollisionRay()
        self.ralphGroundRay.setOrigin(0,0,1000)
        self.ralphGroundRay.setDirection(0,0,-1)
        self.ralphGroundCol = CollisionNode('ralphRay')
        self.ralphGroundCol.addSolid(self.ralphGroundRay)
        self.ralphGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.ralphGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.carGroundColNp = self.car.attachNewNode(self.ralphGroundCol)
        self.ralphGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.carGroundColNp, self.ralphGroundHandler)
        
        #car1
        self.car1Ray = CollisionSphere(0,0,0,4)
        self.car1GroundCol = CollisionNode('car1Ray')
        self.car1GroundCol.addSolid(self.car1Ray)
        self.car1GroundCol.setFromCollideMask(BitMask32.bit(0))
        self.car1GroundCol.setIntoCollideMask(BitMask32.allOff())
        self.car1GroundColNp = self.car.attachNewNode(self.car1GroundCol)
        self.car1GroundHandler = CollisionHandlerQueue()
        #self.car1GroundColNp.show()
        self.cTrav.addCollider(self.car1GroundColNp, self.car1GroundHandler)
        cnodePath = self.car1.attachNewNode(CollisionNode('cnode1'))
        cnodePath.node().addSolid(self.car1Ray)
        #cnodePath.show()
        
        #car2
        self.car2Ray = CollisionSphere(0,0,0,4)
        self.car2GroundCol = CollisionNode('car2Ray')
        self.car2GroundCol.addSolid(self.car2Ray)
        self.car2GroundCol.setFromCollideMask(BitMask32.bit(0))
        self.car2GroundCol.setIntoCollideMask(BitMask32.allOff())
        self.car2GroundColNp = self.car.attachNewNode(self.car2GroundCol)
        self.car2GroundHandler = CollisionHandlerQueue()
        #self.car2GroundColNp.show()
        self.cTrav.addCollider(self.car2GroundColNp, self.car2GroundHandler)
        cnodePath = self.car2.attachNewNode(CollisionNode('cnode2'))
        cnodePath.node().addSolid(self.car2Ray)
        #cnodePath.show()
           
        #car3
        self.car3Ray = CollisionSphere(0,0,0,4)
        self.car3GroundCol = CollisionNode('car3Ray')
        self.car3GroundCol.addSolid(self.car3Ray)
        self.car3GroundCol.setFromCollideMask(BitMask32.bit(0))
        self.car3GroundCol.setIntoCollideMask(BitMask32.allOff())
        self.car3GroundColNp = self.car.attachNewNode(self.car3GroundCol)
        self.car3GroundHandler = CollisionHandlerQueue()
        #self.car3GroundColNp.show()
        self.cTrav.addCollider(self.car3GroundColNp, self.car3GroundHandler)
        cnodePath = self.car3.attachNewNode(CollisionNode('cnode3'))
        cnodePath.node().addSolid(self.car3Ray)
        #cnodePath.show()
         
        #car4
        self.car4Ray = CollisionSphere(0,0,0,4)
        self.car4GroundCol = CollisionNode('car4Ray')
        self.car4GroundCol.addSolid(self.car4Ray)
        self.car4GroundCol.setFromCollideMask(BitMask32.bit(0))
        self.car4GroundCol.setIntoCollideMask(BitMask32.allOff())
        self.car4GroundColNp = self.car.attachNewNode(self.car4GroundCol)
        self.car4GroundHandler = CollisionHandlerQueue()
        #self.car4GroundColNp.show()
        self.cTrav.addCollider(self.car4GroundColNp, self.car4GroundHandler)
        cnodePath = self.car4.attachNewNode(CollisionNode('cnode4'))
        cnodePath.node().addSolid(self.car4Ray)
        #cnodePath.show()
       
        
        #camera
        self.camGroundRay = CollisionRay()
        self.camGroundRay.setOrigin(0,0,1000)
        self.camGroundRay.setDirection(0,0,-1)
        self.camGroundCol = CollisionNode('camRay')
        self.camGroundCol.addSolid(self.camGroundRay)
        self.camGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.camGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.camGroundColNp = base.camera.attachNewNode(self.camGroundCol)
        self.camGroundHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)
               
		
    def onCollision(self, entry):
		print("123")
		    
    def displayHealth(self):
		healthBar['scale'] = (self.health*0.01*BAR_WIDTH,0.2,0.2)
		
    #Records the state of the arrow keys
    def setKey(self, key, value):
        self.keyMap[key] = value
    

    def makezero4(self,task):
		self.flag4=0
		
    def makezero3(self,task):
		self.flag3=0
		
    #to update the AIWorld
    def AIUpdate(self,task):
        self.AIworld.update()            
        return task.cont
        
    def makezero1(self,task):
		self.flag1=0
		
    def makezero2(self,task):
		self.flag2=0
	
    def move(self, task):
        if (self.flagd==1):
            self.points = self.points + globalClock.getDt()
        self.player_points = int(self.points)
        printPointObj(self.player_points)
        #print int(self.points)

        base.camera.lookAt(self.car)
        if (self.keyMap["cam-left"]!=0):
            base.camera.setX(base.camera, -20 * globalClock.getDt())
        if (self.keyMap["cam-right"]!=0):
            base.camera.setX(base.camera, +20 * globalClock.getDt())

        # save car's initial position so that we can restore it,
        # in case he falls off the map or runs into something.

        startposcar = self.car.getPos()

        # If a move-key is pressed, move the car in the specified direction.

        if (self.keyMap["left"]!=0):
            self.car.setH(self.car.getH() + 100 * globalClock.getDt())
        if (self.keyMap["right"]!=0):
            self.car.setH(self.car.getH() - 100 * globalClock.getDt())
        if (self.keyMap["forward"]!=0):
            self.car.setY(self.car, -40 * globalClock.getDt())
        if (self.keyMap["back"]!=0):
            self.car.setY(self.car, 40 * globalClock.getDt())
            

        if (self.keyMap["forward"]!=0) or (self.keyMap["left"]!=0) or (self.keyMap["right"]!=0) or (self.keyMap["back"]!=0):
            if self.isMoving is False:
                self.isMoving = True
        else:
            if self.isMoving:
                self.car.stop()
                self.isMoving = False

        # If the camera is too far from the car, move it closer.
        # If the camera is too close to the car, move it farther.

        camvec = self.car.getPos() - base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if (camdist > 10.0):
            base.camera.setPos(base.camera.getPos() + camvec*(camdist-10))
            camdist = 10.0
        if (camdist < 5.0):
            base.camera.setPos(base.camera.getPos() - camvec*(5-camdist))
            camdist = 5.0

        # Now check for collisions.

        self.cTrav.traverse(render)

        entries = []
        for i in range(self.ralphGroundHandler.getNumEntries()):
            entry = self.ralphGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            self.car.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            self.car.setPos(startposcar)

        entries=[] 
        for i in range(self.car1GroundHandler.getNumEntries()):
            entry = self.car1GroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))    
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "cnode1") and (self.flag1==0):
			#print "car1"
			self.flag1=1
			self.health=self.health - 10
			printHealthObj(self.health)
			print "car1"
			taskMgr.doMethodLater(5,self.makezero1,"flag1")
			
        entries=[]
        for i in range(self.car2GroundHandler.getNumEntries()):
            entry = self.car2GroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))    
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "cnode2") and (self.flag2==0):
			#print "car2"
			self.flag2=1
			self.health=self.health - 10
			printHealthObj(self.health)
			print "car2"
			taskMgr.doMethodLater(5,self.makezero2,"flag2")
			
        
        entries=[]
        for i in range(self.car3GroundHandler.getNumEntries()):
            entry = self.car3GroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))    
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "cnode3") and (self.flag3==0):
			#print "car3"
			self.flag3=1
			self.health=self.health - 10
			printHealthObj(self.health)
			print "car3"
			taskMgr.doMethodLater(5,self.makezero3,"flag3")
			
			
        entries=[]
        for i in range(self.car4GroundHandler.getNumEntries()):
            entry = self.car4GroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))    
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "cnode4") and (self.flag4==0):
			#print "car4"
			self.flag4=1
			self.health=self.health - 10
			printHealthObj(self.health)
			print "car4"
			taskMgr.doMethodLater(5,self.makezero4,"flag4")
			
        entries = []
        for i in range(self.camGroundHandler.getNumEntries()):
            entry = self.camGroundHandler.getEntry(i)
            entries.append(entry)
        entries.sort(lambda x,y: cmp(y.getSurfacePoint(render).getZ(),
                                     x.getSurfacePoint(render).getZ()))
        if (len(entries)>0) and (entries[0].getIntoNode().getName() == "terrain"):
            base.camera.setZ(entries[0].getSurfacePoint(render).getZ()+1.0)
        if (base.camera.getZ() < self.car.getZ() + 2.0):
            base.camera.setZ(self.car.getZ() + 2.0)
            
            
        if self.health <= 0:
			self.flagd=0
			frame=DirectFrame(image=r"end.jpg",frameSize=(-3, 3, -3, 3))
			textObject1 = OnscreenText(text = 'You Died!', pos = (0, 0.7), scale = 0.22)
			textObject2 = OnscreenText(text = 'Press ESC to Exit', pos = (0,0.9), scale=0.1)
			b = DirectButton(text="Exit Game",scale=0.1,command = sys.exit)
			textObject3 = OnscreenText(text = 'Your Score: ' + str(self.player_points), pos = (-0.2, -0.9), scale = 0.22)
			
        
        self.floater.setPos(self.car.getPos())
        self.floater.setZ(self.car.getZ() + 2.0)
        base.camera.lookAt(self.floater)
        self.displayHealth()

        return task.cont
        
        
def Help():
	inst1 = addInstructions(0.95, "[ESC]: Quit")
	inst2 = addInstructions(0.90, "[Left Arrow]: Turn Car Left")
	inst3 = addInstructions(0.85, "[Right Arrow]: Turn Car Right")
	inst4 = addInstructions(0.80, "[Up Arrow]: Drive Forward")
	inst8 = addInstructions(0.75, "[Down Arrow]: Reverse Car")
	inst6 = addInstructions(0.70, "[A]: Rotate Camera Left")
	inst7 = addInstructions(0.65, "[S]: Rotate Camera Right")
    
def selfDestroy():
	w = World()
	b1.destroy()
	b2.destroy()
	b3.destroy()
	textObject1.destroy()
	myFrame.destroy()
		     
myFrame = DirectFrame(image=r"menu.jpg",frameSize=(-3, 3, -3, 3),image_scale=(1.5,1.5,1.5))
textObject1 = OnscreenText(text = 'Bumping Cars', pos = (0, 0.55), scale = 0.2)
b1 = DirectButton(text="Start Game",scale=0.1,command=selfDestroy)
b1.setPos(-0.3,0.9,0)
b2 = DirectButton(text="Instructions",scale=0.1,command=Help)
b2.setPos(0.3,-0.9,0)
b3 = DirectButton(text="Exit Game",scale=0.1,command=sys.exit)
b3.setPos(0.9,-2.7,0)

run()

