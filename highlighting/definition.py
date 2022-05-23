# This file defines the special regexes

# list of symbols recognized as characters (with non-Latin characters)
CHARACTER = '0-9_A-Za-zÀ-ÿء-ي'

# definition of word
WORD = f'([{CHARACTER}]+)'
# space
SPACE     = "( +)"

# beginning and end of one line, including space 
START_LINE = '(^ *)'
END_LINE = '( *$)'

# beginning and end of words
START_WORD = '(^| )'
END_WORD = f'(?![{CHARACTER}])'

TRANSLATE_WORD = [
	"print",
	"ask",
	"echo",
	"forward",
	"turn",
	"color",
	"black",
	"blue",
	"brown",
	"gray",
	"green",
	"orange",
	"pink",
	"purple",
	"red",
	"white",
	"yellow",
	"right",
	"left",
	"is",
	"sleep",
	"add",
	"to_list",
	"remove",
	"from",
	"at",
	"random",
	"in",
	"if",
	"else",
	"and",
	"repeat",
	"times",
	"for",
	"range",
	"to",
	"step",
	"elif",
	"input",
	"or",
	"while",
	"length"
]

def K(word):
	return f"(__{word}__)" if word in TRANSLATE_WORD else f"({word})"
