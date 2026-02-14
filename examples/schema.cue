package example

#Gene: {
	symbol:      string
	source_a_id: *"" | string
	source_b_id: *"" | string
	in_source_a: *false | true
	in_source_b: *false | true
	function?:   string
	phenotypes?: [...string]
}

genes: [Symbol=string]: #Gene & {symbol: Symbol}
