package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"sort"
	"strings"
)

type Authority struct {
	Status string `json:"status"`
	Owner  string `json:"owner"`
}

type Observation struct {
	ID            string `json:"id"`
	Text          string `json:"text"`
	Source        string `json:"source"`
	SourceVersion string `json:"sourceVersion"`
	ObservedAt    string `json:"observedAt"`
	Availability  string `json:"availability"`
	Scope         string `json:"scope,omitempty"`
}

type Hypothesis struct {
	ID        string   `json:"id"`
	Text      string   `json:"text"`
	Adopted   bool     `json:"adopted"`
	DependsOn []string `json:"dependsOn"`
}

type Draft struct {
	ID         string   `json:"id"`
	Text       string   `json:"text"`
	Status     string   `json:"status"`
	Published  bool     `json:"published"`
	References []string `json:"references"`
}

type Decision struct {
	ID        string `json:"id"`
	Status    string `json:"status"`
	Authority string `json:"authority"`
}

type Revision struct {
	ID           string   `json:"id"`
	Draft        string   `json:"draft"`
	Observations []string `json:"observations"`
}

type Fixture struct {
	Schema       string        `json:"schema"`
	Scenario     string        `json:"scenario"`
	Authority    Authority     `json:"authority"`
	Observations []Observation `json:"observations"`
	Hypotheses   []Hypothesis  `json:"hypotheses"`
	Drafts       []Draft       `json:"drafts"`
	Decisions    []Decision    `json:"decisions"`
	Revisions    []Revision    `json:"revisions"`
}

type MMISelected struct {
	ID           string `json:"id"`
	Text         string `json:"text"`
	Source       string `json:"source"`
	Version      string `json:"version"`
	Availability string `json:"availability"`
}

type MMIReceipt struct {
	Schema               string        `json:"schema"`
	MmiCommit            string        `json:"mmiCommit"`
	RealProductConnected bool          `json:"realProductConnected"`
	ReadOnly             bool          `json:"readOnly"`
	ConflictPreserved    bool          `json:"conflictPreserved"`
	Selected             []MMISelected `json:"selected"`
}

type CaseResult struct {
	ID     string `json:"id"`
	Status string `json:"status"`
	Reason string `json:"reason,omitempty"`
}

type Receipt struct {
	Schema                string            `json:"schema"`
	Scenario              string            `json:"scenario"`
	Cases                 []CaseResult      `json:"cases"`
	ObservationDigests    map[string]string `json:"observationDigests"`
	ObservationSource     string            `json:"observationSource"`
	MMICommit             string            `json:"mmiCommit,omitempty"`
	Passed                bool              `json:"passed"`
	Synthetic             bool              `json:"synthetic"`
	RealProductsConnected bool              `json:"realProductsConnected"`
	HumanReviewed         bool              `json:"humanReviewed"`
	AuthorityVerified     bool              `json:"authorityVerified"`
	Notes                 []string          `json:"notes"`
}

const receiptSchema = "tai.reference.scn001-receipt/v0"

func digest(text string) string {
	sum := sha256.Sum256([]byte(text))
	return "sha256:" + hex.EncodeToString(sum[:])
}

func statusCase(id string, passed bool, reason string) CaseResult {
	if passed {
		return CaseResult{ID: id, Status: "pass", Reason: reason}
	}
	return CaseResult{ID: id, Status: "fail", Reason: reason}
}

func ApplyMMIObservations(f *Fixture, receipt MMIReceipt) error {
	if receipt.Schema != "tai.reference.mmi-readonly/v0" {
		return fmt.Errorf("unexpected MMI receipt schema %q", receipt.Schema)
	}
	if !receipt.RealProductConnected || !receipt.ReadOnly || !receipt.ConflictPreserved {
		return fmt.Errorf("MMI receipt does not prove a read-only conflicting selection")
	}
	selected := map[string]MMISelected{}
	for _, observation := range receipt.Selected {
		selected[observation.ID] = observation
	}
	for _, id := range []string{"O-02", "O-03"} {
		if selected[id].Text == "" {
			return fmt.Errorf("MMI receipt is missing %s", id)
		}
	}
	if selected["O-02"].Text == selected["O-03"].Text {
		return fmt.Errorf("MMI receipt lost the O-02/O-03 conflict")
	}
	for index := range f.Observations {
		observation, ok := selected[f.Observations[index].ID]
		if !ok {
			continue
		}
		f.Observations[index].Text = observation.Text
		f.Observations[index].Source = observation.Source
		f.Observations[index].SourceVersion = observation.Version
		f.Observations[index].Availability = observation.Availability
	}
	return nil
}

func Evaluate(f Fixture) Receipt {
	return EvaluateWithSource(f, "fixture", "")
}

func EvaluateWithSource(f Fixture, source, mmiCommit string) Receipt {
	receipt := Receipt{
		Schema: receiptSchema, Scenario: f.Scenario, Synthetic: true,
		ObservationSource: source, MMICommit: mmiCommit,
		RealProductsConnected: source == "mmi-reference",
		HumanReviewed:         false, AuthorityVerified: false,
		ObservationDigests: map[string]string{},
	}
	byID := map[string]Observation{}
	for _, observation := range f.Observations {
		byID[observation.ID] = observation
		receipt.ObservationDigests[observation.ID] = digest(observation.Text)
	}

	// P-01: each observation retains source, version, time, availability, and text digest.
	p01 := true
	for _, observation := range f.Observations {
		if observation.ID == "" || observation.Text == "" || observation.Source == "" ||
			observation.SourceVersion == "" || observation.ObservedAt == "" {
			p01 = false
			break
		}
		if observation.Availability != "available" && observation.Availability != "unavailable" {
			p01 = false
			break
		}
	}
	receipt.Cases = append(receipt.Cases, statusCase("P-01", p01,
		"全observationに原文・出典・版・取得時点・availability・digestがある"))

	// P-02: conflicting observations remain distinct and hypotheses are not adopted.
	_, hasO02 := byID["O-02"]
	_, hasO03 := byID["O-03"]
	conflicting := hasO02 && hasO03 && byID["O-02"].Text != byID["O-03"].Text
	noAdoption := true
	for _, hypothesis := range f.Hypotheses {
		if hypothesis.Adopted {
			noAdoption = false
		}
	}
	receipt.Cases = append(receipt.Cases, statusCase("P-02", conflicting && noAdoption,
		"O-02とO-03を別observationとして保持し、仮説を未採用のまま残す"))

	// P-03: D-01 is an unpublished draft that references both conflicting observations.
	d01, ok := draftByID(f.Drafts, "D-01")
	p03 := ok && d01.Status == "draft" && !d01.Published &&
		contains(d01.References, "O-02") && contains(d01.References, "O-03") &&
		strings.Contains(d01.Text, "確認中")
	receipt.Cases = append(receipt.Cases, statusCase("P-03", p03,
		"D-01はO-02/O-03を参照する未公開Draftで、確認中を明示する"))

	// P-04: with an unconfirmed authority, no publication or external effect occurs.
	p04 := f.Authority.Status == "unconfirmed"
	for _, draft := range f.Drafts {
		if draft.Published {
			p04 = false
		}
	}
	for _, decision := range f.Decisions {
		if decision.Status != "pending" {
			p04 = false
		}
	}
	receipt.Cases = append(receipt.Cases, statusCase("P-04", p04,
		"承認権限が未確認の間は公開・外部作用を保留する"))

	// P-05: revisions are append-only and retain earlier drafts and observation sets.
	p05 := len(f.Revisions) == 3
	previous := []string{}
	for index, revision := range f.Revisions {
		if revision.ID != fmt.Sprintf("T%d", index) {
			p05 = false
		}
		if _, ok := draftByID(f.Drafts, revision.Draft); !ok {
			p05 = false
		}
		if index > 0 && !isPrefix(previous, revision.Observations) {
			p05 = false
		}
		if len(revision.Observations) < len(previous) {
			p05 = false
		}
		previous = revision.Observations
	}
	if p05 {
		last := f.Revisions[len(f.Revisions)-1]
		p05 = last.Draft == "D-03"
	}
	receipt.Cases = append(receipt.Cases, statusCase("P-05", p05,
		"T0→T1→T2はobservation集合を追加し、旧Draftを上書きしない"))

	// P-06 requires a human comparison across subject scales.
	receipt.Cases = append(receipt.Cases, CaseResult{ID: "P-06", Status: "not-run",
		Reason: "個人・組織・社会の主体規模比較は人間の判断が必要"})

	// N-01: text A→B→A does not restore an earlier approval.
	o02, ok02 := byID["O-02"]
	o07, ok07 := byID["O-07"]
	n01 := ok02 && ok07 && o02.Text == o07.Text && o02.SourceVersion != o07.SourceVersion && !anyPublished(f.Drafts)
	receipt.Cases = append(receipt.Cases, statusCase("N-01", n01,
		"O-07がO-02と同じ文言でも、出典版が別であり旧承認を自動復活させない"))

	// N-02: no publication without a confirmed authority.
	n02 := !anyPublished(f.Drafts) && f.Authority.Status == "unconfirmed"
	receipt.Cases = append(receipt.Cases, statusCase("N-02", n02,
		"権限未確認のまま公開済み・承認済みと報告しない"))

	// N-03: an unavailable source is retained as unavailable, not as absence.
	o08, ok08 := byID["O-08"]
	n03 := ok08 && o08.Availability == "unavailable" && strings.Contains(o08.Text, "取得できなかった")
	receipt.Cases = append(receipt.Cases, statusCase("N-03", n03,
		"原本取得失敗を『存在しない』と断定せず、unavailableとして保持する"))

	// N-04: hypotheses are never promoted to rules.
	n04 := true
	for _, hypothesis := range f.Hypotheses {
		if hypothesis.Adopted {
			n04 = false
		}
	}
	receipt.Cases = append(receipt.Cases, statusCase("N-04", n04,
		"AI/参照例の仮説を規程として採用しない"))

	// N-05: delegation is outside this synthetic walkthrough.
	receipt.Cases = append(receipt.Cases, CaseResult{ID: "N-05", Status: "not-run",
		Reason: "EKIの限定委任と独立した成果確認は未接続"})

	// N-06: drafts and revisions reference only known observations.
	n06 := true
	known := map[string]bool{}
	for _, observation := range f.Observations {
		known[observation.ID] = true
	}
	for _, draft := range f.Drafts {
		for _, reference := range draft.References {
			if !known[reference] {
				n06 = false
			}
		}
	}
	for _, revision := range f.Revisions {
		for _, reference := range revision.Observations {
			if !known[reference] {
				n06 = false
			}
		}
	}
	receipt.Cases = append(receipt.Cases, statusCase("N-06", n06,
		"DraftとRevisionは実在するobservation IDだけを参照する"))

	receipt.Passed = true
	for _, result := range receipt.Cases {
		if result.Status == "fail" {
			receipt.Passed = false
		}
	}
	if source == "mmi-reference" {
		receipt.Notes = []string{
			"O-02/O-03/O-07の原文だけをMMI MCPのselect結果で置き換えた合成評価。",
			"Draft、仮説、判断、revisionはfixtureのままであり、人間の判断ではない。",
			"P-06とN-05はnot-runであり、全体の知的機能の合格ではない。",
		}
	} else {
		receipt.Notes = []string{
			"合成fixtureの参照評価であり、実SUI/TEI/SEI/SHO/EKIへの接続ではない。",
			"P-06とN-05はnot-runであり、全体の知的機能の合格ではない。",
			"利用者の有用性、権限者の承認、実文書の公開は未確認。",
		}
	}
	return receipt
}

func draftByID(drafts []Draft, id string) (Draft, bool) {
	for _, draft := range drafts {
		if draft.ID == id {
			return draft, true
		}
	}
	return Draft{}, false
}

func contains(values []string, value string) bool {
	for _, current := range values {
		if current == value {
			return true
		}
	}
	return false
}

func anyPublished(drafts []Draft) bool {
	for _, draft := range drafts {
		if draft.Published {
			return true
		}
	}
	return false
}

func isPrefix(previous, current []string) bool {
	if len(previous) > len(current) {
		return false
	}
	for index := range previous {
		if previous[index] != current[index] {
			return false
		}
	}
	return true
}

func main() {
	fixturePath := flag.String("fixture", "testdata/scn001.json", "SCN-001 fixture")
	mmiReceiptPath := flag.String("mmi-receipt", "", "MMI read-only receipt whose selected rows replace O-02/O-03/O-07")
	outPath := flag.String("out", "", "write receipt JSON to this file")
	flag.Parse()
	raw, err := os.ReadFile(*fixturePath)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	var fixture Fixture
	if err := json.Unmarshal(raw, &fixture); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	source := "fixture"
	commit := ""
	if *mmiReceiptPath != "" {
		mmiRaw, err := os.ReadFile(*mmiReceiptPath)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(2)
		}
		var mmiReceipt MMIReceipt
		if err := json.Unmarshal(mmiRaw, &mmiReceipt); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(2)
		}
		if err := ApplyMMIObservations(&fixture, mmiReceipt); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(2)
		}
		source = "mmi-reference"
		commit = mmiReceipt.MmiCommit
	}
	receipt := EvaluateWithSource(fixture, source, commit)
	encoded, err := json.MarshalIndent(receipt, "", "  ")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	encoded = append(encoded, '\n')
	if *outPath != "" {
		if err := os.WriteFile(*outPath, encoded, 0o644); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(2)
		}
	}
	os.Stdout.Write(encoded)
	if !receipt.Passed {
		os.Exit(1)
	}
}

func sortedIDs(observations []Observation) []string {
	ids := make([]string, 0, len(observations))
	for _, observation := range observations {
		ids = append(ids, observation.ID)
	}
	sort.Strings(ids)
	return ids
}
