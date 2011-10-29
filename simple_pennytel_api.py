#!/usr/bin/python

# my fork of version created by d1b
# using Python GUI Hello World tutorial 

# SETTINGS
PENNYTEL_ACCOUNT_NUMBER = ""
PENNYTEL_PASSWORD = "" 
PENNYTEL_API_URL = "https://www.pennytel.com/pennytelapi/services/PennyTelAPI" # use https://  

# THE MESSAGE 
TO = "" # phone number to send it to, include country code e.g. 61400000000
SMS_MESSAGE = "" # the sms message to be sent

# operational stuff
import lxml
import pycurl
import StringIO
from lxml import etree
from lxml.builder import ElementMaker
from lxml.builder import E

# gui stuff 
import pygtk
pygtk.require('2.0')
import gtk

class PennytelConException(Exception):
	def __init__(self, message, response=None):
		Exception.__init__(self, message)
		self.response = response

class PennytelCon:
	def __init__(self, username="_none_", password="_none_", post_url="_none_", connection=pycurl.Curl()):
		self._username = username
		self._password = password
		self._post_url = post_url
		self._connection = connection
		self._build_soap_base()

	def _post_using_over_https(self, post_data=None):
		string_s = StringIO.StringIO()
		if post_data is not None:
			self._connection.setopt(pycurl.POSTFIELDS, post_data)

		self._connection.setopt(pycurl.HTTPHEADER, ['SOAPAction:ebXML'])
		self._connection.setopt(pycurl.USERAGENT, "pennytel python bindings version 0.01")
		self._connection.setopt(pycurl.FOLLOWLOCATION, False) #Do not follow redirects.
		self._connection.setopt(pycurl.SSL_VERIFYPEER, 1)
		self._connection.setopt(pycurl.SSL_VERIFYHOST, 2)
		self._connection.setopt(pycurl.SSLVERSION, 3)
		self._connection.setopt(pycurl.WRITEFUNCTION, string_s.write)
		self._connection.setopt(pycurl.URL, self._post_url)
		self._connection.perform()
		the_page = string_s.getvalue()
		http_code = self._connection.getinfo(pycurl.HTTP_CODE)
		return http_code, the_page


	def _build_soap_base(self):
		self._base_xml = ElementMaker (
			namespace = 'http://schemas.xmlsoap.org/soap/envelope/',
			nsmap =
			{
				'xsd' : 'http://www.w3.org/2001/XMLSchema',
				'xsi' : 'http://www.w3.org/2001/XMLSchema-instance',
				'soap' : 'http://schemas.xmlsoap.org/soap/encoding/'
			}
		)

	def _send_soap_request(self):
		self._request_xml = self._base_xml.Envelope(self._base_xml.Body(self._action_specific_xml))
		post_data = etree.tostring(self._request_xml, xml_declaration=True, encoding='UTF-8', pretty_print=True)

		http_code, the_page =  self._post_using_over_https(post_data)

		if http_code != 200:
			message = "api failure, http code = " + str(http_code)
			raise PennytelConException(message, the_page)
		return the_page

	def send_sms(self, message, destination, date="2007-02-01T09:37:00"):
		self._action_specific_xml = (
			E.sendSMS (
				E.id(self._username), E.password(self._password),
				E.type('0'), E.to(destination),
				E.message(message),
				E.date(date)
			)
		)
		self._send_soap_request()
		return "SMS sent successfully!"

	def trigger_callback(self, leg1, leg2, date="2007-02-01T09:37:00"):
		self._action_specific_xml = (
			E.triggerCallback (
				E.id(self._username), E.password(self._password),
				E.leg1(leg1), E.leg2(leg2),
				E.date(date)
			)
		)
		return self._send_soap_request()

	def get_contacts(self, criteria="%"):
		self._action_specific_xml = (
			E.getAddressBookEntries (
				E.id(self._username), E.password(self._password),
				E.criteria(criteria)
			)
		)
		return self._send_soap_request()

	def get_account_info(self):
		self._action_specific_xml = (
			E.getAccount (
				E.id(self._username), E.password(self._password)
			)
		)
		return self._send_soap_request()

class SMSWindow:

    # This is a callback function. The data arguments are ignored
    # in this example. More on callbacks below.
    def send(self, widget, data=None):
        print penny.send_sms(SMS_MESSAGE, TO)

    def delete_event(self, widget, event, data=None):
        # If you return FALSE in the "delete_event" signal handler,
        # GTK will emit the "destroy" signal. Returning TRUE means
        # you don't want the window to be destroyed.
        # This is useful for popping up 'are you sure you want to quit?'
        # type dialogs.
        #print "delete event occurred"

        # Change FALSE to TRUE and the main window will not be destroyed
        # with a "delete_event".
        return False

    def destroy(self, widget, data=None):
        # print "destroy signal occurred"
        gtk.main_quit()

    def __init__(self):
        # create a new window
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    
        # When the window is given the "delete_event" signal (this is given
        # by the window manager, usually by the "close" option, or on the
        # titlebar), we ask it to call the delete_event () function
        # as defined above. The data passed to the callback
        # function is NULL and is ignored in the callback function.
        self.window.connect("delete_event", self.delete_event)
    
        # Here we connect the "destroy" event to a signal handler.  
        # This event occurs when we call gtk_widget_destroy() on the window,
        # or if we return FALSE in the "delete_event" callback.
        self.window.connect("destroy", self.destroy)
    
        # Sets the border width of the window.
        self.window.set_border_width(50)
    
        # Creates a new button with the label "Hello World".
        self.button = gtk.Button("Send SMS")
    
        # When the button receives the "clicked" signal, it will call the
        # function hello() passing it None as its argument.  The hello()
        # function is defined above.
        self.button.connect("clicked", self.send, None)
    
        # This will cause the window to be destroyed by calling
        # gtk_widget_destroy(window) when "clicked".  Again, the destroy
        # signal could come from here, or the window manager.
        self.button.connect_object("clicked", gtk.Widget.destroy, self.window)
    
        # This packs the button into the window (a GTK container).
        self.window.add(self.button)
    
        # The final step is to display this newly created widget.
        self.button.show()
    
        # and the window
        self.window.show()

    def main(self):
        # All PyGTK applications must have a gtk.main(). Control ends here
        # and waits for an event to occur (like a key press or mouse event).
        gtk.main()

# If the program is run directly or passed as an argument to the python
# interpreter then create a HelloWorld instance and show it
if __name__ == "__main__":
	penny = PennytelCon(PENNYTEL_ACCOUNT_NUMBER, PENNYTEL_PASSWORD, PENNYTEL_API_URL)
	send = SMSWindow()
	send.main()
    	
    	