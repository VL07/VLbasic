from .tokenizer import Token
from .parser import Parser
from .interpreter import Interpreter
from .contextclass import Context, VariableTable
from .tokenizer import Tokenizer
from .runtimevaluesclass import RuntimeValue

v = VariableTable()
i: Interpreter = None
context: Context = None

def resetVariables():
	v.variables = {}
	if i and context:
		i.addDefaultVariables(context)

def interpret(code, name) -> list[RuntimeValue]:
	global i
	global context

	t = Tokenizer(name, code)
	tokens, error = t.tokenize()

	if error:
		raise error
	
	p = Parser(name, tokens)

	statements, error = p.parse()

	if error:
		raise error

	context = Context("SHELL")
	context.setVariableTable(v)

	i = Interpreter(statements)
	i.addDefaultVariables(context)
	out, error = i.interpret(context)

	if error:
		raise error

	return out
		
