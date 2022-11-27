import math

def add(parameters, context, error):
	return "abc", None

variables = {
	"PI": {
		"value": math.pi,
		"constant": True
	},
	"abc": {
		"value": [1,2,3],
		"constant": True
	},
	"dict": {
		"value": {"a": 1, "b": 2},
		"constant": True
	},
	"ADD": {
		"value": add,
		"constant": True,
		"parameters": [2, 2]
	}
}