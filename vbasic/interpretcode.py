from .parser import Parser
from .interpreter import Interpreter
from .contextclass import Context
from .tokenizer import Tokenizer

def interpret(code: str, name: str):
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
		
