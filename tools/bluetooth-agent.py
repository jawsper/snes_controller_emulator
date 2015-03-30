#!/usr/bin/python2

# bluetooth agent for sixaxis auto connect

import dbus
import dbus.service

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

class SixAxisManager(dbus.service.Object):
	def __init__(self, object_path):
		dbus.service.Object.__init__(self, dbus.SystemBus(), object_path)
		self.object_path = object_path

		bus = dbus.SystemBus()
		self.agent_manager = dbus.Interface(bus.get_object('org.bluez', '/org/bluez'), dbus_interface='org.bluez.AgentManager1')
		self.agent_manager.RegisterAgent(object_path, "DisplayYesNo")
		self.agent_manager.RequestDefaultAgent(object_path)


		device_proxy = bus.get_object('org.bluez', '/org/bluez/hci0')
		self.device_properties = dbus.Interface(device_proxy, 'org.freedesktop.DBus.Properties')
		self.device_properties.Set('org.bluez.Adapter1', 'Powered', True)

	def disable(self):
		self.agent_manager.UnregisterAgent(self.object_path)
		self.device_properties.Set('org.bluez.Adapter1', 'Powered', False)


	@dbus.service.method(dbus_interface='org.bluez.Agent1', in_signature='', out_signature='')
	def Release(self):
		print("Release called")

	@dbus.service.method(dbus_interface='org.bluez.Agent1', in_signature='o', out_signature='')
	def RequestAuthorization(self, device):
		print('RequestAuthorization({})'.format(device))
	@dbus.service.method(dbus_interface='org.bluez.Agent1', in_signature='os', out_signature='')
	def AuthorizeService(self, device, uuid):
		print('AuthorizeService({}, {})'.format(device, uuid))
	@dbus.service.method(dbus_interface='org.bluez.Agent1', in_signature='', out_signature='')
	def Cancel(self):
		print('Cancel()')


sixaxis = SixAxisManager('/sixaxisauth')

import gobject

loop = gobject.MainLoop()
try:
	loop.run()
finally:
	sixaxis.disable()