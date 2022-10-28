import tokenizer
import parser
import interpreter
import contextclass

while True:
	inputText = input("] ")
	t = tokenizer.Tokenizer("SHELL", inputText)
	tokens, error = t.tokenize()

	if error:
		print(repr(error))
		print("")
		continue
	
	print(tokens)
	p = parser.Parser("SHELL", tokens)

	statements, error = p.parse()

	if error:
		print(repr(error))
		print("")
		continue

	print(statements)

	context = contextClass.Context("SHELL")

	i = interpreter.Interpreter(statements)
	out, error = i.interpret(context)

	if error:
		print(repr(error))
		print("")
		continue

	print(out)
	print(out[0].value)
		
