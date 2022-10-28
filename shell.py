from vbasic.tokenizer import Tokenizer
from vbasic.parser import Parser
from vbasic.interpreter import Interpreter
from vbasic.contextclass import Context

while True:
	inputText = input("] ")
	t = Tokenizer("SHELL", inputText)
	tokens, error = t.tokenize()

	if error:
		print(repr(error))
		print("")
		continue
	
	print(tokens)
	p = Parser("SHELL", tokens)

	statements, error = p.parse()

	if error:
		print(repr(error))
		print("")
		continue

	print(statements)

	context = Context("SHELL")

	i = Interpreter(statements)
	out, error = i.interpret(context)

	if error:
		print(repr(error))
		print("")
		continue

	print(out)
	print(out[0].value)
		
