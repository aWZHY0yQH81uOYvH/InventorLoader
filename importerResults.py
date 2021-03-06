# -*- coding: utf-8 -*-

'''
importerResults.py:
Simple approach to read/analyse Autodesk (R) Invetor (R) part file's (IPT) browser view data.
The importer can read files from Autodesk (R) Invetor (R) Inventro V2010 on. Older versions will fail!
'''

from importerSegment import SegmentReader, checkReadAll
from importerClasses import ResultItem4
from importerUtils   import *
import importerSegNode

__author__     = 'Jens M. Plonka'
__copyright__  = 'Copyright 2018, Germany'
__url__        = "https://www.github.com/jmplonka/InventorLoader"

class ResultReader(SegmentReader):
	def __init__(self, segment):
		super(ResultReader, self).__init__(segment)

	def Read_128AAF24(self, node):
		i = node.Read_Header0()
		if (getFileVersion() > 2016):
			i += 4
		else:
			i += 1
		i = node.ReadList4(i, importerSegNode._TYP_RESULT_1_, 'lst1')
		i = node.ReadList4(i, importerSegNode._TYP_RESULT_2_, 'lst2')
		i = node.ReadList4(i, importerSegNode._TYP_RESULT_3_, 'lst3')
		i = self.skipBlockSize(i)
		if (getFileVersion() > 2011):
			i = node.ReadList4(i, importerSegNode._TYP_RESULT_4_, 'lst4')
			if (getFileVersion() > 2016):
				i = node.ReadList6(i, importerSegNode._TYP_MAP_KEY_MAP_APP_1_, 'lst5')
			else:
				node.content += ' lst5={}'
				i += 1
		else:
			node.content += ' lst4={} lst5={}'
			i += 1
		i = node.ReadList4(i, importerSegNode._TYP_RESULT_5_, 'lst6')
		i = node.ReadList4(i, importerSegNode._TYP_RESULT_4_, 'lst7')
		i = node.ReadUInt8(i, 'u8_1')
		i = node.ReadList4(i, importerSegNode._TYP_RESULT_4_, 'lst8')
		i = node.ReadUInt8(i, 'u8_2')
		i = self.skipBlockSize(i)
		return i

	def Read_F645595C(self, node):
		i = node.Read_Header0()
		i = node.ReadUInt32(i, 'u32_0')
		i = self.skipBlockSize(i)
		i = node.ReadUInt32(i, 'schema')
		i = self.skipBlockSize(i)
		i = node.ReadUInt32(i, 'u32_2')
		i = node.ReadUInt8(i, 'u8_0')
		i = node.ReadSInt32(i, 's32_0')
		i = self.skipBlockSize(i)
		if (getFileVersion() > 2018): i += 1
		i = node.ReadChildRef(i, 'ref_1')
		i = node.ReadSInt32(i, 'lastKey')
		return i

	def Read_F78B08D5(self, node):
		i = node.Read_Header0('SatHistory')
		i = node.ReadSInt32(i, 's32_0')
		i = self.skipBlockSize(i)
		i = node.ReadParentRef(i)
		i = node.ReadList2(i, importerSegNode._TYP_UINT32_, 'numbers') # see "*_sat.history" file for details
		i = node.ReadList6(i, importerSegNode._TYP_MAP_KEY_REF_, 'delta_states')
		i = node.ReadChildRef(i, 'ref_1')
		return i

	def Read_Header1(self, node):
		i = self.skipBlockSize(0)
		i = node.ReadParentRef(i)
		return i

	def Read_09780457(self, node):
		i = self.Read_Header1(node)
		i = node.ReadSInt32(i, 'delta_state') # the number of the delta_states in the sat file
		i = node.ReadList2(i, importerSegNode._TYP_NODE_REF_, 'lst0')
		return i

	def Read_21830CED(self, node):
		i = self.Read_Header1(node)
		i = node.ReadUInt16A(i, 10, 'a0')
		return i

	def Read_36246381(self, node):
		i = self.Read_Header1(node)
		i = node.ReadUInt16A(i, 8, 'a0')
		return i

	def Read_69C3A76F(self, node):
		i = self.Read_Header1(node)
		i = node.ReadUInt16A(i, 16, 'a0')
		return i

	def Read_F434C70B(self, node):
		i = self.Read_Header1(node)
		i = node.ReadUInt16A(i, 10, 'a0')
		return i

	def Read_F8DD2C9D(self, node):
		i = self.Read_Header1(node)
		i = node.ReadUInt16A(i, 8, 'a0')
		return i

	####################
	# int Parent int int sections
	def Read_Header2(self, node):
		i = self.skipBlockSize(0)
		i = node.ReadUInt32(i, 'root')
		i = node.ReadParentRef(i)
		i = node.ReadUInt32(i, 'flags')
		i = self.skipBlockSize(i)
		i = node.ReadUInt32(i, 'ref_0')
		return i

	def Read_0E70AF5C(self, node):
		i = self.Read_Header2(node)
		i = node.ReadUInt32(i, 'dcBodyIdx')
		return i

	def Read_3E0040FD(self, node):
		i = self.Read_Header2(node)
		i = node.ReadUInt32(i, 'dcBodyIdx')
		i = node.ReadUInt32(i, 'dcCreatorIdx')
		return i

	def Read_6B9A3C47(self, node):
		i = self.Read_Header2(node)
		i = node.ReadUInt32(i, 'dcBodyIdx')
		return i

	def Read_809BE56F(self, node):
		i = self.Read_Header2(node)
		return i

	def Read_80CAECF1(self, node):
		i = self.Read_Header2(node)
		return i

	def Read_9147489A(self, node):
		i = self.Read_Header2(node)
		i = node.ReadUInt32(i, 'dcBodyIdx')
		return i

	def Read_A4645884(self, node):
		i = self.Read_Header2(node)
		return i

	def Read_E065E15A(self, node):
		i = self.Read_Header2(node)
		i = node.ReadUInt32(i, 'dcBodyIdx')
		i = node.ReadUInt32(i, 'u32_0')
		i = node.ReadUInt32(i, 'dcCreatorIdx')
		return i

	def Read_E9B04618(self, node):
		i = self.Read_Header2(node)
		return i
