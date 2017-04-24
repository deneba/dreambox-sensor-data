##
## Sensor Data
## by Asif Rana, 20170413
## based on PermanentClock
##
from Components.ActionMap import ActionMap
from Components.config import config, ConfigInteger, ConfigSubsection, ConfigYesNo
from Components.Language import language
from Components.MenuList import MenuList
from Components.Label import Label
from enigma import ePoint, eTimer, getDesktop
from os import environ
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import gettext
import json,urllib
from enigma import eTimer
from Components.Element import Element

##############################################################################

config.plugins.SensorData = ConfigSubsection()
config.plugins.SensorData.enabled = ConfigYesNo(default=False)
config.plugins.SensorData.position_x = ConfigInteger(default=590)
config.plugins.SensorData.position_y = ConfigInteger(default=35)

##############################################################################

class Source(Element):
	def execBegin(self):
		pass
	
	def execEnd(self):
		pass
	
	def onShow(self):
		pass

	def onHide(self):
		pass
	
	def destroy(self):
		self.__dict__.clear()

class SensorDataSource(Source):
	def __init__(self, update_interval = 5000):
		self.update_interval = update_interval
		Source.__init__(self)

		self.update_timer = eTimer()
		self.update_timer.callback.append(self.updateValue)
		self.update_timer.start(self.update_interval)

	def getValue(self):
		return self.getSensorData()
	
	def getText(self):
		return self.getValue()

	def setText(self, text):
		self.__text = text

	def updateValue(self):
		self.changed((self.CHANGED_POLL,))

	def destroy(self):
		self.update_timer.callback.remove(self.updateValue)
	
	def getSensorData(self):
	   try:                                                                                     
        	jsonurl = urllib.urlopen("http://REST_SERVER:PORT/DATA_ENDPOINT")                               
        	textd = json.loads(jsonurl.read()) 
		return "T:" + '{:02d}'.format(int(textd[0]["last_Temperature"])) + ",H:" + '{:02d}'.format(int(textd[0]["last_Humidity"])) + ",C:" + '{:04d}'.format(int(textd[0]["last_CO2"]))
	   except:
		return "Sensor Error"         

	text = property(getText, setText)

##############################################################################

SKIN = """
	<screen position="0,0" size="400,50" zPosition="1" backgroundColor="#ff000000" title="%s" flags="wfNoBorder">
		<widget source="SensorDataTxt" render="Label" position="0,0" size="400,50" font="Regular;23" 
valign="center" halign="center" backgroundColor="#ff000000" transparent="1" zPosition="1" >
</widget>
	</screen>""" % "Sensor Data"

##############################################################################

class SensorDataScreen(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skin = SKIN
		self["SensorDataTxt"] = SensorDataSource(update_interval = 30000)
		self.onShow.append(self.movePosition)
	
	def movePosition(self):
		if self.instance:
			self.instance.move(ePoint(config.plugins.SensorData.position_x.value, config.plugins.SensorData.position_y.value))

##############################################################################

class SensorData():
	def __init__(self):
		self.dialog = None

	def gotSession(self, session):
		self.dialog = session.instantiateDialog(SensorDataScreen)
		self.showHide()

	def changeVisibility(self):
		if config.plugins.SensorData.enabled.value:
			config.plugins.SensorData.enabled.value = False
		else:
			config.plugins.SensorData.enabled.value = True
		config.plugins.SensorData.enabled.save()
		self.showHide()

	def showHide(self):
		if config.plugins.SensorData.enabled.value:
			self.dialog.show()
		else:
			self.dialog.hide()

pClock = SensorData()

##############################################################################

class SensorDataPositioner(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skin = SKIN
		self["SensorDataTxt"] = SensorDataSource(update_interval = 30000)

		self["actions"] = ActionMap(["WizardActions"],
		{
			"left": self.left,
			"up": self.up,
			"right": self.right,
			"down": self.down,
			"ok": self.ok,
			"back": self.exit
		}, -1)
		
		desktop = getDesktop(0)
		self.desktopWidth = desktop.size().width()
		self.desktopHeight = desktop.size().height()
		
		self.moveTimer = eTimer()
		self.moveTimer.callback.append(self.movePosition)
		self.moveTimer.start(50, 1)

	def movePosition(self):
		self.instance.move(ePoint(config.plugins.SensorData.position_x.value, config.plugins.SensorData.position_y.value))
		self.moveTimer.start(50, 1)

	def left(self):
		value = config.plugins.SensorData.position_x.value
		value -= 1
		if value < 0:
			value = 0
		config.plugins.SensorData.position_x.value = value

	def up(self):
		value = config.plugins.SensorData.position_y.value
		value -= 1
		if value < 0:
			value = 0
		config.plugins.SensorData.position_y.value = value

	def right(self):
		value = config.plugins.SensorData.position_x.value
		value += 1
		if value > self.desktopWidth:
			value = self.desktopWidth
		config.plugins.SensorData.position_x.value = value

	def down(self):
		value = config.plugins.SensorData.position_y.value
		value += 1
		if value > self.desktopHeight:
			value = self.desktopHeight
		config.plugins.SensorData.position_y.value = value

	def ok(self):
		config.plugins.SensorData.position_x.save()
		config.plugins.SensorData.position_y.save()
		self.close()

	def exit(self):
		config.plugins.SensorData.position_x.cancel()
		config.plugins.SensorData.position_y.cancel()
		self.close()

##############################################################################

class SensorDataMenu(Screen):
	skin = """
		<screen position="center,center" size="420,105" title="%s">
			<widget name="list" position="10,10" size="400,85" />
		</screen>""" % "Sensor Data"

	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self["list"] = MenuList([])
		self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.okClicked, "cancel": self.close}, -1)
		self.onLayoutFinish.append(self.showMenu)

	def showMenu(self):
		list = []
		if config.plugins.SensorData.enabled.value:
			list.append("Deactivate Sensor Data")
		else:
			list.append("Activate Sensor Data")
		list.append("Change Sensor Data")
		self["list"].setList(list)

	def okClicked(self):
		sel = self["list"].getCurrent()
		if pClock.dialog is None:
			pClock.gotSession(self.session)
		if sel == "Deactivate Sensor Data" or sel == "Activate Sensor Data":
			pClock.changeVisibility()
			self.showMenu()
		else:
			pClock.dialog.hide()
			self.session.openWithCallback(self.positionerCallback, SensorDataPositioner)

	def positionerCallback(self, callback=None):
		pClock.showHide()

##############################################################################

def sessionstart(reason, **kwargs):
	if reason == 0:
		pClock.gotSession(kwargs["session"])

def startConfig(session, **kwargs):
	session.open(SensorDataMenu)

def main(menuid):
	if menuid != "system": 
		return [ ]
	return [("Sensor Data", startConfig, "Sensor_data", None)]

##############################################################################

def Plugins(**kwargs):
	return [
		PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionstart),
		PluginDescriptor(name="Sensor Data", description="Shows sensor data permanent on the screen", 
where=PluginDescriptor.WHERE_MENU, fnc=main)]
