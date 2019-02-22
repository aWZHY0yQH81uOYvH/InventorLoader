# -*- coding: utf-8 -*-

'''
importer.py:
Collection of 3D Mesh importers
'''

import os, sys, FreeCAD, importerSAT, Import_IPT
from importerUtils import canImport, logWarning, logError, logAlways, viewAxonometric
from olefile       import isOleFile
import importerUtils, Acis, importerClasses

__author__     = "Jens M. Plonka"
__copyright__  = 'Copyright 2018, Germany'
__url__        = "https://www.github.com/jmplonka/InventorLoader"

def decode(name):
	"decodes encoded strings"
	decodedName = name
	try:
		decodedName = name.encode(sys.getfilesystemencoding()).decode("utf8")
	except:
		logWarning("    Couldn't determine character encoding for filename - using unencoded!\n")
	return decodedName

def insertGroup(doc, filename):
	grpName = os.path.splitext(os.path.basename(filename))[0]
	#There's a problem with adding groups starting with numbers!
	root = createGroup(doc, '_%s' %(grpName))
	root.Label = grpName

	return root

def read(doc, filename, readProperties):
	name, ext = os.path.splitext(filename)
	ext = ext.lower()
	if (ext == '.ipt'):
		if (Import_IPT.read(doc, filename, readProperties)):
			return Import_IPT
	elif (ext == '.sat'):
		if (importerSAT.readText(doc, filename)):
			return importerSAT
	elif (ext == '.sab'):
		if (importerSAT.readBinary(doc, filename)):
			return importerSAT
	elif (ext == '.iam'):
		logError(u"Sorry, AUTODESK assembly files not yet supported!")
	return None

def isFileValid(filename):
	if (not os.path.exists(os.path.abspath(filename))):
		logError(u"File doesn't exists (%s)!", os.path.abspath(filename))
		return False
	if (not os.path.isfile(filename)):
		logError(u"Can't import folders!")
		return False
	if (filename.split(".")[-1].lower() in ("ipt", "iam")):
		if (not isOleFile(filename)):
			logError(u"ERROR> '%s' is not a valid Autodesk Inventor file!", filename)
			return False
	return canImport()

def releaseMemory():
	importerUtils._thumbnail = None
	Acis.clearEntities()
	importerClasses.releaseModel()

def insert(filename, docname, skip = [], only = [], root = None):
	'''
	opens an Autodesk Inventor file in the current document
	'''
	if (isFileValid(filename)):
		try:
			doc = FreeCAD.getDocument(docname)
			logAlways(u"Importing: %s", filename)
			reader = read(doc, filename, False)
			if (reader is not None):
				name = os.path.splitext(os.path.basename(filename))[0]
				name = decode(name)
				group = insertGroup(doc, name)
				reader.create3dModel(group, doc)
				viewAxonometric()
			releaseMemory()
		except:
			open(filename, skip, only, root)
	return

def open(filename, skip = [], only = [], root = None):
	'''
	opens an Autodesk Inventor file in a new document
	In addition to insert (import), the iProperties are as well added to the document.
	'''
	if (isFileValid(filename)):
		logAlways(u"Reading: %s", os.path.abspath(filename))
		name = os.path.splitext(os.path.basename(filename))[0]
		doc = FreeCAD.newDocument(decode(name))
		doc.Label = name
		reader = read(doc, filename, True)
		if (reader is not None):
			# Create 3D-Model in root (None) of document
			reader.create3dModel(None , doc)
			viewAxonometric()
		releaseMemory()
	return
