"""
Ilari Shafer
4/30/07
Interface to Outlook libraries
"""
import win32com.client

#convert a comma-separated list to a list with elements of type typ
def csv2lst(str, typ):
	return [typ(item) for item in str.split(",")]

#convert a list to a csv string
def lst2csv(lst):
	str = ""
	for dex in range(len(lst) - 1):
		str += lst[dex] + ","
	if len(lst) >= 1:
		str += lst[-1]
	return str

#defines publicly accessible methods for Outlook
class OutlookInterface:
	def __init__(self):
		self.out = Outlook()

	#Get the root list of names
	def GetNames(self):
		return lst2csv(self.out.root.childNames())

	#Get the list of folder names on the selected message path
	def GetNamesOnPath(self,lst):
		return lst2csv(self.out.GetFolder(csv2lst(lst, int)).childNames())

	#Get the number of items in the selected message path
	def GetLenItemsOnPath(self,lst):
		return self.out.GetFolder(csv2lst(lst, int)).LenItems()
		
	#Get the small preview box contents for the item on path lst at index dex
	def GetItemPreviewOnPath(self,lst,dex):
		return self.out.GetFolder(csv2lst(lst, int)).GetItem(int(dex)).Preview()
		
	#Get the main window contents for the item on path lst at index dex
	def GetItemContentsOnPath(self,lst,dex):
		return self.out.GetFolder(csv2lst(lst, int)).GetItem(int(dex)).Contents()
	
#Internal Outlook interface
class Outlook:
	def __init__(self):
		self.comobj = win32com.client.Dispatch("Outlook.Application")
		self.ns = self.comobj.GetNamespace("MAPI")
		
		self.root = Folder(self.ns, "root")
		
	def GetFolder(self, lst):
		curfol = self.root
		for dex in lst:
			curfol = curfol.childFolder(dex)
			
		return curfol

#Represents a Folder in the Outlook folder hierarchy
class Folder:
	#Create a new Folder with the given MAPIFolder object
	def __init__(self, obj, name=None):
		self.obj = obj
		
		if name is not None:
			self.name = name
		else:
			self.name = obj.Name
		self.assigned = False
		self.enumFolders = list()

	def GetName(self):
		return self.name

	def assignFolders(self):
		for dex in range(len(self.obj.Folders)):
			self.enumFolders.append(Folder(self.obj.Folders[dex+1]))

	#return a subfolder with the specified index
	def childFolder(self, dex):
		if not self.assigned:
			self.assignFolders()
			self.assigned = True
		return self.enumFolders[dex]
		
	#return a list of names of child folders in order
	def childNames(self):
		if not self.assigned:
			self.assignFolders()
			self.assigned = True
		names = []
		for fol in self.enumFolders:
			names.append(fol.GetName())
			
		return names
	
	#return the number of items contained in this Folder
	def LenItems(self):
		return len(self.obj.Items)
		
	#return a polymorphic Item representing 
	def GetItem(self, dex):
		iobj = self.obj.Items[dex+1]
		typ = iobj.__class__.__name__
		
		if typ == "_MailItem":
			return MailItem(iobj)
		else:
			return Item(iobj)

class Item:
	def __init__(self, obj):
		self.obj = obj;
	def Preview(self):
		return "unknown"
	def Contents(self):
		return str(self.obj);

#represents a MailItem
class MailItem(Item):
	#exemplifies how one might toss back an HTML string
	def Preview(self):
		return \
			"<div class='preview subject'>" + str(self.obj.Subject) + "</div>" + \
			"<div class='preview sender'>" + str(self.obj.SentOnBehalfOfName) + "</div>" + \
			"<div class='preview date'>" + str(self.obj.SentOn) + "</div>"
	def Contents(self):
		return self.obj.HTMLBody
	
if __name__ == "__main__":
	out = OutlookInterface()
	fol = out.out.root.childFolder(0).childFolder(5)
	print fol.GetName()
	#fol = out.out.root.childFolder(1)
	print "length:", out.GetLenItemsOnPath("0,5")
	print out.GetItemPreviewOnPath("0,5","5")