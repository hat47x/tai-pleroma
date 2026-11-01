package main

// A handwritten candidate for the sui.card.text projection contract. It keeps
// missing, empty and unresolved distinct and never invents a value.

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"
)

type output struct {
	State string `json:"state"`
	Text  string `json:"text,omitempty"`
}

func emit(out output) {
	encoded, _ := json.Marshal(out)
	fmt.Println(string(encoded))
}

func main() {
	var in map[string]any
	if err := json.NewDecoder(os.Stdin).Decode(&in); err != nil {
		emit(output{State: "error"})
		os.Exit(2)
	}
	value, ok := in["text"]
	if !ok {
		emit(output{State: "missing"})
		return
	}
	if value == nil {
		emit(output{State: "unresolved"})
		return
	}
	text, ok := value.(string)
	if !ok {
		emit(output{State: "error"})
		os.Exit(2)
	}
	emit(output{State: "present", Text: strings.TrimSpace(text)})
}
