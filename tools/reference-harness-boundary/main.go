package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"os"
	"sort"
)

// ErrWriteDenied is returned when a harness tries to modify the product
// canonical store. The product, not the harness, owns this decision.
var ErrWriteDenied = errors.New("write denied: harness may not modify the product canonical store")

type Receipt struct {
	Schema                string   `json:"schema"`
	ReadOnly              bool     `json:"readOnly"`
	WriteDenied           bool     `json:"writeDenied"`
	CanonicalUnchanged    bool     `json:"canonicalUnchanged"`
	HandoffRecorded       bool     `json:"handoffRecorded"`
	DeferredRecorded      bool     `json:"deferredRecorded"`
	ProviderRecorded      bool     `json:"providerRecorded"`
	SessionEnded          bool     `json:"sessionEnded"`
	Passed                bool     `json:"passed"`
	Synthetic             bool     `json:"synthetic"`
	RealProductsConnected bool     `json:"realProductsConnected"`
	Notes                 []string `json:"notes"`
}

type Handoff struct {
	ContextID string `json:"contextId"`
	Version   string `json:"version"`
	Task      string `json:"task"`
	Deferred  bool   `json:"deferred"`
}

type Provider struct {
	ID      string `json:"id"`
	Version string `json:"version"`
}

type Encounter struct {
	ProviderID      string `json:"providerId"`
	ProviderVersion string `json:"providerVersion"`
	Task            string `json:"task"`
}

type ReadReceipt struct {
	Key             string `json:"key"`
	Value           string `json:"value"`
	ProductVersion  string `json:"productVersion"`
	ReadOnly        bool   `json:"readOnly"`
	CanonicalDigest string `json:"canonicalDigest"`
}

// Product is a synthetic canonical store. It exposes a read tool, rejects
// every write, and records context handoffs separately from the canonical
// values.
type Product struct {
	canonical map[string]string
	version   string
	handoffs  []Handoff
}

func NewProduct() *Product {
	return &Product{
		canonical: map[string]string{
			"policy": "会議室の予約は、施設の規程に従う。",
			"scope":  "internal-review",
		},
		version: "product-v1",
	}
}

func (p *Product) Digest() string {
	keys := make([]string, 0, len(p.canonical))
	for key := range p.canonical {
		keys = append(keys, key)
	}
	sort.Strings(keys)
	hash := sha256.New()
	for _, key := range keys {
		fmt.Fprintf(hash, "%s=%s\n", key, p.canonical[key])
	}
	return "sha256:" + hex.EncodeToString(hash.Sum(nil))
}

func (p *Product) Read(key string) (ReadReceipt, error) {
	value, ok := p.canonical[key]
	if !ok {
		return ReadReceipt{}, fmt.Errorf("unknown key %q", key)
	}
	return ReadReceipt{
		Key:             key,
		Value:           value,
		ProductVersion:  p.version,
		ReadOnly:        true,
		CanonicalDigest: p.Digest(),
	}, nil
}

func (p *Product) Write(key, value string) error {
	return ErrWriteDenied
}

func (p *Product) RecordHandoff(handoff Handoff) {
	p.handoffs = append(p.handoffs, handoff)
}

// Harness holds a session and a context handoff history. It may read the
// product and pass context to it, but it may not write the canonical store.
type Harness struct {
	product    *Product
	sessionID  string
	budget     int
	used       int
	ended      bool
	handoffs   []Handoff
	encounters []Encounter
}

func NewHarness(product *Product, sessionID string) *Harness {
	return &Harness{product: product, sessionID: sessionID, budget: 1}
}

func (h *Harness) Read(key string) (ReadReceipt, error) {
	if h.ended {
		return ReadReceipt{}, errors.New("session ended")
	}
	return h.product.Read(key)
}

func (h *Harness) Write(key, value string) error {
	if h.ended {
		return errors.New("session ended")
	}
	return h.product.Write(key, value)
}

func (h *Harness) Handoff(task string) (Handoff, error) {
	if h.ended {
		return Handoff{}, errors.New("session ended")
	}
	handoff := Handoff{ContextID: h.sessionID + "-ctx", Version: "v1", Task: task}
	if h.used >= h.budget {
		handoff.Deferred = true
	} else {
		h.used++
	}
	h.product.RecordHandoff(handoff)
	h.handoffs = append(h.handoffs, handoff)
	return handoff, nil
}

func (h *Harness) Encounter(provider Provider, task string) (Encounter, error) {
	if h.ended {
		return Encounter{}, errors.New("session ended")
	}
	if provider.ID == "" || provider.Version == "" {
		return Encounter{}, errors.New("provider id and version are required")
	}
	encounter := Encounter{ProviderID: provider.ID, ProviderVersion: provider.Version, Task: task}
	h.encounters = append(h.encounters, encounter)
	return encounter, nil
}

func (h *Harness) EndSession() {
	h.ended = true
}

// Run exercises the four boundary checks on a synthetic product and harness.
func Run() Receipt {
	receipt := Receipt{
		Schema:                "tai.reference.harness-boundary/v0",
		Synthetic:             true,
		RealProductsConnected: false,
		Notes: []string{
			"合成の製品とハーネスによる境界の参照実装。",
			"実製品の認可、監査、複数利用者を確かめない。",
			"ハーネスはセッションと受け渡しの記録を持ち、製品の正本を持たない。",
			"文脈の上限の後は、渡せなかったものを保留として記録する。",
			"提供元のIDと版を記録し、提供元を正本にしない。",
		},
	}
	product := NewProduct()
	before := product.Digest()
	harness := NewHarness(product, "session-1")

	read, err := harness.Read("policy")
	receipt.ReadOnly = err == nil && read.ReadOnly && read.CanonicalDigest == before

	writeErr := harness.Write("policy", "tampered")
	receipt.WriteDenied = errors.Is(writeErr, ErrWriteDenied)

	first, firstErr := harness.Handoff("会議室の予約要否を確認する")
	second, secondErr := harness.Handoff("未解決の予約条件を渡す")
	receipt.HandoffRecorded = firstErr == nil && !first.Deferred && len(product.handoffs) >= 1 && product.handoffs[0] == first
	receipt.DeferredRecorded = secondErr == nil && second.Deferred && len(product.handoffs) >= 2 && product.handoffs[1] == second

	encounter, encounterErr := harness.Encounter(Provider{ID: "provider-a", Version: "v1"}, "課題を処理する")
	receipt.ProviderRecorded = encounterErr == nil && len(harness.encounters) == 1 && harness.encounters[0] == encounter

	after := product.Digest()
	receipt.CanonicalUnchanged = before == after

	harness.EndSession()
	_, readErr := product.Read("policy")
	receipt.SessionEnded = readErr == nil

	receipt.Passed = receipt.ReadOnly && receipt.WriteDenied && receipt.CanonicalUnchanged &&
		receipt.HandoffRecorded && receipt.DeferredRecorded && receipt.ProviderRecorded && receipt.SessionEnded
	return receipt
}

func main() {
	out := flag.String("out", "", "write the receipt JSON to this file")
	flag.Parse()
	receipt := Run()
	raw, err := json.MarshalIndent(receipt, "", "  ")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Println(string(raw))
	if *out != "" {
		if err := os.WriteFile(*out, append(raw, '\n'), 0o644); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
	if !receipt.Passed {
		os.Exit(1)
	}
}
