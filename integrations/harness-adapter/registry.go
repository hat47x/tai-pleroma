package harnessadapter

import (
	"fmt"
	"sort"
	"strings"
)

// Registry is a name → Adapter lookup for one process. It is deliberately not a
// plugin registry, not a discovery service and not a second source of truth: it
// is the in-process table a caller builds explicitly from the adapters it
// constructed. Nothing is discovered, nothing is loaded from disk, and an
// adapter's presence here says nothing about whether it can run today.
type Registry struct {
	adapters map[string]Adapter
	order    []string
}

// NewRegistry builds an empty registry.
func NewRegistry() *Registry {
	return &Registry{adapters: map[string]Adapter{}}
}

// Register adds an adapter. Registering the same name twice replaces it, so a
// caller can rebuild the table between trials without leaking the old one.
func (r *Registry) Register(a Adapter) {
	if _, ok := r.adapters[a.Name()]; !ok {
		r.order = append(r.order, a.Name())
	}
	r.adapters[a.Name()] = a
}

// Get returns one adapter by name.
func (r *Registry) Get(name string) (Adapter, bool) {
	a, ok := r.adapters[name]
	return a, ok
}

// Names returns registered names in registration order.
func (r *Registry) Names() []string {
	out := append([]string(nil), r.order...)
	sort.Strings(out)
	return out
}

// Resolve picks the first registered adapter whose name is in want. It returns
// an error listing what is actually registered rather than silently falling
// back, so an unavailable harness is never papered over by a different one.
func (r *Registry) Resolve(want ...string) (Adapter, error) {
	available := r.Names()
	for _, w := range want {
		if a, ok := r.adapters[w]; ok {
			return a, nil
		}
	}
	return nil, fmt.Errorf("no registered adapter in %v; registered: %s", want, strings.Join(available, ", "))
}
