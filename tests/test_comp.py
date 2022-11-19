import pytest
from vlbasic.interpretcode import interpret, resetVariables

def interpretCode(code):
	return interpret(code, "TEST")[0]

class TestComparisons:
	def testEquals(self):
		assert interpretCode("1 == 1").value == True
		assert interpretCode("1 == 2").value == False
		assert interpretCode("1 == TRUE").value == True
		assert interpretCode("1 == FALSE").value == False
		assert interpretCode("0 == TRUE").value == False
		assert interpretCode("0 == FALSE").value == True
		assert interpretCode("0 == NULL").value == False
		assert interpretCode("1 == NULL").value == False

	def testNotEquals(self):
		assert interpretCode("1 != 1").value == False
		assert interpretCode("1 != 2").value == True
		assert interpretCode("1 != TRUE").value == False
		assert interpretCode("1 != FALSE").value == True
		assert interpretCode("0 != TRUE").value == True
		assert interpretCode("0 != FALSE").value == False
		assert interpretCode("0 != NULL").value == True
		assert interpretCode("1 != NULL").value == True

	def testGraterThan(self):
		assert interpretCode("1 > 0").value == True
		assert interpretCode("1 > 1").value == False
		assert interpretCode("1 > 21321").value == False
		assert interpretCode("989012893 > -2310").value == True
		assert interpretCode("-23132 > 0").value == False

	def testLessThan(self):
		assert interpretCode("1 < 0").value == False
		assert interpretCode("1 < 1").value == False
		assert interpretCode("1 < 21321").value == True
		assert interpretCode("989012893 < -2310").value == False
		assert interpretCode("-23132 < 0").value == True

	def testGraterEquals(self):
		assert interpretCode("1 >= 0").value == True
		assert interpretCode("1 >= 1").value == True
		assert interpretCode("10 >= 11").value == False
		
	def testLessEquals(self):
		assert interpretCode("1 <= 0").value == False
		assert interpretCode("1 <= 1").value == True
		assert interpretCode("10 <= 11").value == True