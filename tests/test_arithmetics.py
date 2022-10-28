import pytest
from vbasic.interpretCode import interpret

def interpretCode(code):
	return interpret(code, "TEST")[0]

class TestArithmetics:
	def testAdd(self):
		assert interpretCode("1 + 1").value == 2
		assert interpretCode("55 + 45").value == 100
		assert interpretCode("3872178372891 + 9823180932891").value == 13695359305782
		assert interpretCode("99 + 99").value == 198
		assert interpretCode("-44 + 30").value == -14
		assert interpretCode("-44 + -44").value == -88
		assert interpretCode("1 + -1").value == 0
		
	def testSubtract(self):
		assert interpretCode("1 - 1").value == 0
		assert interpretCode("55 - 45").value == 10
		assert interpretCode("3872178372891 - 9823180932891").value == -5951002560000
		assert interpretCode("100 - 99").value == 1
		assert interpretCode("-44 - 30").value == -74
		assert interpretCode("-44 - -44").value == 0
		assert interpretCode("1 - -1").value == 2

	def testMultiply(self):
		assert interpretCode("1 * 1").value == 1
		assert interpretCode("55 * 45").value == 2475
		assert interpretCode("1234 * 1234").value == 1522756
		assert interpretCode("99 * 99").value == 9801
		assert interpretCode("-44 * 30").value == -1320
		assert interpretCode("-44 * -44").value == 1936
		assert interpretCode("1 * -1").value == -1

	def testDivide(self):
		assert interpretCode("1 / 1").value == 1
		assert interpretCode("50 / 20").value == 2.5
		assert interpretCode("99 / 33").value == 3
		assert interpretCode("-10 / 20").value == -0.5
		assert interpretCode("-44 / -44").value == 1
		assert interpretCode("1 / -1").value == -1

	def testParenthesis(self):
		assert interpretCode("(1 + 1) * 2").value == 4
		assert interpretCode("(5 + 5) * (5 + 5)").value == 100
		assert interpretCode("1 / (0 + 1)").value == 1
