import tokenizer
import parser

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
		
