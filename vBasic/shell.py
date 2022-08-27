import tokenizer

while True:
	inputText = input("] ")
	t = tokenizer.Tokenizer("SHELL", inputText)
	tokens, error = t.tokenize()

	if error:
		print(repr(error))
		print("")
	else:
		print(tokens)
