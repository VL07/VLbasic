from .tokenizer import Token
from .parser import Parser
from .interpreter import Interpreter
from .contextClass import Context
from .tokenizer import Tokenizer
from .runtimeValuesClass import RuntimeValue

def interpret(code, name) -> list[RuntimeValue]:
	t = Tokenizer(name, code)
	tokens, error = t.tokenize()

	if error:
		raise error
	
	p = Parser(name, tokens)

	statements, error = p.parse()

	if error:
		raise error

	context = Context(name)

	i = Interpreter(statements)
	out, error = i.interpret(context)

	if error:
		raise error

	return out
		
