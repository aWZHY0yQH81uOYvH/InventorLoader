# -*- coding: utf-8 -*-

'''
Import_IPT.py:
Simple approach to read/analyse Autodesk (R) Invetor (R) files.
'''

__author__     = "Jens M. Plonka"
__copyright__  = 'Copyright 2018, Germany'
__url__        = "https://www.github.com/jmplonka/InventorLoader"

import os, FreeCAD, FreeCADGui, importerBRep, importerSAT, io, importerUFRxDoc
from olefile           import OleFileIO
from importerUtils     import *
from importerReader    import *
from importerClasses   import Inventor
from importerFreeCAD   import FreeCADImporter
from importerSAT       import importModel, convertModel
from uuid              import UUID
from Acis              import setReader

def ReadIgnorable(fname):
	logInfo(u"    IGNORED: '%s'" %(fname[-1]))

def skip():
	return

def ReadElement(ole, fname, doc, counter, readProperties):
	name        = fname[-1]
	path        = PrintableName(fname)

	if (fname[0] == 'Protein'):
#		ReadProtein(ole.openstream(fname).read())
		ReadIgnorable(fname)
	elif (fname[0]=='CacheGraphics'):
		skip()
	elif (fname[0]=='RSeStorage'):
		if (isEmbeddings(fname)):
			if (name == 'Workbook'):
				ReadWorkbook(doc, ole.openstream(fname).read(), fname[-2], name)
			elif (name.endswith('Ole10Native')):
				ReadOle10Native(doc, ole.openstream(fname).read(), fname)
			else:
				skip()
		elif (name.startswith('M')):
			if not ('Templates' in fname):
				fnameB = []
				for n in (fname):
					fnameB.append(n)
				fnameB[-1] = 'B' + name[1:]
				seg = ReadRSeMetaDataM(ole.openstream(fname).read(), name[1:])
				seg.file = name[1:]
				seg.index = counter
				getModel().RSeMetaData[seg.name] = seg
				dataB = ole.openstream(fnameB).read()
				ReadRSeMetaDataB(dataB, seg)
			else:
				skip()
		else:
			ReadIgnorable(fname)
	return

def dumpRSeDBFile(db, log):
	log.write(u"Schema: %d\n"   %(db.schema))
	log.write(u"UID:    {%s}\n" %(db.uid))
	log.write(u"Date1:  %s\n"   %(db.dat1))
	log.write(u"Date2:  %s\n"   %(db.dat2))
	log.write(u"arr1:   [%s]\n" %(IntArr2Str(db.arr1, 3)))
	log.write(u"arr2:   [%s]\n" %(IntArr2Str(db.arr2, 3)))
	log.write(u"%s\n" %(db.txt))

	log.write(u"segInfo:\n")
	log.write(u"\tUID:   {%s}\n" %(db.segInfo.uid))
	log.write(u"\tDate:  %s\n"   %(db.segInfo.date))
	log.write(u"\tText:  '%s'\n" %(db.segInfo.text))
	log.write(u"\tU16:   %03X\n" %(db.segInfo.u16))
	log.write(u"\tText2: '%s'\n" %(db.segInfo.text2))
	log.write(u"\tarr1:  [%s]\n" %(IntArr2Str(db.segInfo.arr1, 3)))
	log.write(u"\tarr2:  [%s]\n" %(IntArr2Str(db.segInfo.arr2, 4)))
	log.write(u"\tarr3:  [%s]\n" %(IntArr2Str(db.segInfo.arr3, 4)))
	log.write(u"\tarr4:  [%s]\n" %(IntArr2Str(db.segInfo.arr4, 4)))
	log.write(u"\tUID1:\n")
	for n, txt in enumerate(db.segInfo.uidList1):
		log.write(u"\t\t[%02X]: '%s'\n" %(n, txt))
	log.write(u"\tUID2:\n")
	for n, txt in enumerate(db.segInfo.uidList2):
		log.write(u"\t\t[%02X]: '%s'\n" %(n, txt))
	log.write(u"\tSegments:\n")
	segments = sorted(db.segInfo.segments.values())
	for seg in segments:
		log.write(u"\t\t%s\n" %(seg))
	return

def dumpRSeDB(db):
	dumpFolder = getDumpFolder()
	if (not (dumpFolder is None)):
		with io.open(u"%s/RSeDb.log" %(dumpFolder), mode='w', encoding='utf-8') as log:
			dumpRSeDBFile(db, log)
	return

def dumpiProperties(iProps):
	dumpFolder = getDumpFolder()
	if (not (dumpFolder is None)):
		with io.open(u"%s/iProperties.log" %(dumpFolder), mode='w', encoding="utf-8") as file:
			setNames = sorted(iProps.keys())
			for setName in setNames:
				file.write(u"%s:\n" %(setName))
				setProps = iProps[setName]
				prpNames = sorted(setProps.keys())
				for prpNum in prpNames:
					val = setProps[prpNum]
					prpName = val[0]
					prpVal  = val[1]
					if (isinstance(prpVal, datetime.datetime)):
						if (prpVal.year > 1900):
							file.write(u"%3d - %26s: %s\n" %(prpNum, prpName, prpVal.strftime("%Y/%m/%d %H:%M:%S.%f")))
					else:
						file.write(u"%3d - %26s: %r\n" %(prpNum, prpName, prpVal))
				file.write(u"\n")
	return

def dumpRevisionInfo(revisions):
	dumpFolder = getDumpFolder()
	if (not (dumpFolder is None)):
		with io.open(u"%s/RSeDbRevisionInfo.log" %(dumpFolder), mode='w', encoding="utf-8") as file:
			for rev in revisions.infos:
				file.write(u"%s\n" %(rev))
	return

def read(doc, filename, readProperties):
	ufrxDoc        = None
	rSeDb          = None
	rSeSegInfo     = None
	rSeDbRevisions = None

	createNewModel()

	ole = setInventorFile(filename)
	setFileVersion(ole)

	elements = ole.listdir(streams=True, storages=False)
	counter  = 1
	list     = []
	handled  = {}

	if (readProperties):
		for fname in elements:
			name = fname[-1]
			if (name.startswith('\x05')):
				props = ole.getproperties(fname, convert_time=True)
				if (name == '\x05Aaalpg0m0wzvuhc41dwauxbwJc'):
					ReadOtherProperties(props, fname, Inventor_Document_Summary_Information)
					doc.Company = getProperty(props, KEY_DOC_SUM_INFO_COMPANY)
				elif (name == '\x05Zrxrt4arFafyu34gYa3l3ohgHg'):
					ReadInventorSummaryInformation(doc, props, fname)
				elif (name == '\x05Qz4dgm1gRjudbpksAayal4qdGf'):
					ReadOtherProperties(props, fname, Design_Tracking_Control)
				elif (name == '\x05PypkizqiUjudbposAayal4qdGf'):
					ReadOtherProperties(props, fname, Design_Tracking_Properties)
					setDescription(getProperty(props, 29))
				elif (name == '\x05Qm0qv30hP3udrkgvAaitm1o20d'):
					ReadOtherProperties(props, fname, Private_Model_Information)
				elif (name == '\x05Ynltsm4aEtpcuzs1Lwgf30tmXf'):
					ReadOtherProperties(props, fname, Inventor_User_Defined_Properties)
				elif (name == '\x05C3vnhh4uFrpeuhcsBpg4yptkTb'):
					ReadOtherProperties(props, fname, Inventor_Piping_Style_Properties)
				else:
					ReadOtherProperties(props, fname, {})
				handled[PrintableName(fname)] = True
			elif (name == 'UFRxDoc'):
				ufrxDoc = ole.openstream(fname).read()
				handled[PrintableName(fname)] = True
			elif (name == 'RSeDb'):
				rSeDb = ole.openstream(fname).read()
				handled[PrintableName(fname)] = True
			elif (name == 'RSeSegInfo'):
				rSeSegInfo = ole.openstream(fname).read()
				handled[PrintableName(fname)] = True
			elif (name == 'RSeDbRevisionInfo'):
				rSeDbRevisions = ole.openstream(fname).read()
				handled[PrintableName(fname)] = True

	chooseImportStrategy()

#	if (ufrxDoc):
#		getModel().UFRxDoc = importerUFRxDoc.read(ufrxDoc)

	if (rSeDb):
		ReadRSeDb(getModel().RSeDb, rSeDb)

	if (rSeSegInfo):
		if ((getModel().RSeDb is None) or (getModel().RSeDb.schema == 0x1F)):
			ReadRSeSegInfo1F(getModel().RSeDb, rSeSegInfo)
		elif (getModel().RSeDb.schema == 0x1E):
			ReadRSeSegInfo1E(getModel().RSeDb, rSeSegInfo)
		else:
			ReadRSeSegInfo1D(getModel().RSeDb, rSeSegInfo)

	if (rSeDbRevisions):
		ReadRSeDbRevisionInfo(getModel().RSeRevisions, rSeDbRevisions)

	for fname in elements:
		if (handled.get(PrintableName(fname), False) == False):
			if (not fname[-1].startswith('B')):
				list.append(fname)

	dumpiProperties(getModel().iProperties)
	dumpRSeDB(getModel().RSeDb)
#	dumpRevisionInfo(getModel().RSeRevisions)

	for fname in list:
		ReadElement(ole, fname, doc, counter, readProperties)
		counter += 1
	ole.close()

	now = datetime.datetime.now()
	if (len(doc.Comment) > 0):
		doc.Comment += '\n'
	doc.Comment = '# %s: read from %s' %(now.strftime('%Y-%m-%d %H:%M:%S'), filename)

	dumpFolder = getDumpFolder()
	if (not (dumpFolder is None)):
		logInfo(u"Dumped data to folder: '%s'", dumpFolder)

	return True

def resolveLinks():
	gr = getModel().getGraphics()
	dc = getModel().getDC()
	grp = gr.elementNodes.get(0x0001)
	if (grp is not None):
		parts = grp.get('parts')
		if (parts is not None):
			for part in parts:
				outlines = part.get('outlines')
				if (outlines is not None):
					for dcIndex in  outlines:
						outline = outlines[dcIndex]
						creator = dc.indexNodes.get(dcIndex, None)
						if (creator is not None):
							creator.outline = outline
						else:
							logWarning(u"    No outline-creator found for index=%04X!" %(dcIndex))
	return

def create3dModel(root, doc):
	strategy = getStrategy()
	if (strategy == STRATEGY_NATIVE):
		creator = FreeCADImporter()
		creator.importModel(root)
	else:
		brep = getModel().getBRep()
		for asm in brep.AcisList:
			setReader(asm.get('SAT'))
			if (strategy == STRATEGY_SAT):
				importModel(root)
			elif (strategy == STRATEGY_STEP):
				convertModel(root, doc.Name)
	return
