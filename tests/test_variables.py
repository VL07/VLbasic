import pytest
from vbasic.interpretcode import interpret, resetVariables

def interpretCode(code):
	return interpret(code, "TEST")[0]

class TestVariables:
	def testLet(self):
		assert interpretCode("LET var = 10").value == 10
		resetVariables()

		assert interpretCode("LET var = -32").value == -32
		resetVariables()

		assert interpretCode("LET var = 10 * 20").value == 200
		resetVariables()

		assert interpretCode("LET var = 10 - 20").value == -10
		resetVariables()

		assert interpretCode("LET var = 5 + 5").value == 10
		resetVariables()

	def testConst(self):
		assert interpretCode("CONST var = 10").value == 10
		resetVariables()

		assert interpretCode("CONST var = -32").value == -32
		resetVariables()

		assert interpretCode("CONST var = 10 * 20").value == 200
		resetVariables()

		assert interpretCode("CONST var = 10 - 20").value == -10
		resetVariables()

		assert interpretCode("CONST var = 5 + 5").value == 10
		resetVariables()

	def testInAccess(self):
		interpretCode("LET var = 4")
		assert interpretCode("var * 3").value == 12
		resetVariables()

		interpretCode("LET var = 4")
		assert interpretCode("var + 3").value == 7
		resetVariables()

		interpretCode("LET var = 4")
		interpretCode("LET b = 2")
		assert interpretCode("var * b").value == 8
		resetVariables()

		interpretCode("LET var = 4")
		assert interpretCode("3 * var").value == 12
		resetVariables()

	def testSettingVariable(self):
		interpretCode("LET var = 4")
		interpretCode("var = 2")
		assert interpretCode("var * 2").value == 4
		resetVariables()

		interpretCode("LET var = 33")
		interpretCode("var = 66")
		assert interpretCode("var").value == 66
		resetVariables()

	def testBuiltIns(self):
		assert interpretCode("TRUE").value == True
		assert interpretCode("FALSE").value == False
		assert interpretCode("NULL").value == "NULL"