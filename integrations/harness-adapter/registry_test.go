package harnessadapter

import (
	"strings"
	"testing"
)

// TestRegistryResolveRefusesSilentFallback is the rule that an unavailable
// harness is never quietly replaced by a different one.
func TestRegistryResolveRefusesSilentFallback(t *testing.T) {
	reg := NewRegistry()
	reg.Register(NewDirectControlAdapter())
	if _, err := reg.Resolve("dsh-headless"); err == nil {
		t.Fatal("an unregistered adapter resolved anyway")
	} else if !strings.Contains(err.Error(), "direct-control") {
		t.Fatalf("error does not list what is registered: %v", err)
	}
	a, err := reg.Resolve("direct-control")
	if err != nil {
		t.Fatalf("registered adapter did not resolve: %v", err)
	}
	if a.Name() != "direct-control" {
		t.Fatalf("resolved %q", a.Name())
	}
}

// TestRegistryReplaceAndList keeps the table a caller-owned structure, not a
// discovery service.
func TestRegistryReplaceAndList(t *testing.T) {
	reg := NewRegistry()
	first := NewDirectControlAdapter()
	reg.Register(first)
	reg.Register(first)
	if got := reg.Names(); len(got) != 1 {
		t.Fatalf("registering the same name twice produced %v", got)
	}
	second := &ScriptedAdapter{Family: "codex", Reachable: true}
	reg.Register(second)
	got := reg.Names()
	if len(got) != 2 || got[0] != "direct-control" || got[1] != "scripted-codex" {
		t.Fatalf("names = %v", got)
	}
	if _, ok := reg.Get("scripted-codex"); !ok {
		t.Fatal("registered adapter not retrievable")
	}
}
