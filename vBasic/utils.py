########################################
#	IMPORTS
########################################

from __future__ import annotations
from enum import Enum, auto
from typing import Optional
import string

########################################
#	ENUMS
########################################



########################################
#	CONSTANTS
########################################

NUMBERS = "0123456789"
LETTERS_LOWERCASE = string.ascii_lowercase
LETTERS_UPPERCASE = string.ascii_uppercase
LETTERS = string.ascii_letters

KEYWORDS = [
	"PRINT"
]


########################################
#	CLASSES
########################################

class File:
	def __init__(self, filename: str, fileText: str) -> None:
		self.name = filename
		self.text = fileText

		self.length = len(self.text)

	def __repr__(self) -> str:
		if self.text.split("\n") == 1:
			return f"file({self.name}, '{self.text}')"
		else:
			return f"file({self.name}, '\n{self.text}\n')"

	def copy(self) -> File:
		return File(self.name, self.text)

class Position:
	def __init__(self, index: int, line: int, column: int, file: File) -> None:
		self.index = index
		self.line = line
		self.column = column
		self.file = file

	def __repr__(self) -> str:
		return f"position({str(self.index)}, ln: {str(self.line)}, cl: {str(self.column)}, {self.file.name})"

	def advance(self, newLine: bool = False):
		self.index += 1
		self.column += 1

		if newLine:
			self.column = 0
			self.line += 1

	def asStartEndPosition(self) -> StartEndPosition:
		return StartEndPosition(self.file.copy(), self.copy())

	def createStartEndPosition(self, end: Position) -> StartEndPosition:
		return StartEndPosition(self.file.copy(), self.copy, end.copy())
			
	def copy(self) -> Position:
		return Position(self.index, self.line, self.column, self.file.copy())

class StartEndPosition:
	def __init__(self, file: File, start: Position, end: Optional[Position] = None) -> None:
		self.file = file
		self.start = start
		self.end = end

		if not self.end:
			self.end = self.start
	
	def __repr__(self) -> str:
		return f"startEndPos({repr(self.start)}, {repr(self.end)}, {self.file.name})"
	
	def copy(self) -> StartEndPosition:
		return StartEndPosition(self.file.copy(), self.start.copy(), self.end.copy())