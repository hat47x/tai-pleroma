package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

type Authority struct {
	Status string `json:"status"`
}

type Observation struct {
	ID            string `json:"id"`
	Text          string `json:"text"`
	Source        string `json:"source"`
	SourceVersion string `json:"sourceVersion"`
	ObservedAt    string `json:"observedAt"`
	Availability  string `json:"availability"`
}

type Draft struct {
	ID         string   `json:"id"`
	Text       string   `json:"text"`
	Status     string   `json:"status"`
	Published  bool     `json:"published"`
	References []string `json:"references"`
}

type Decision struct {
	ID                  string `json:"id"`
	Status              string `json:"status"`
	Draft               string `json:"draft"`
	Scope               string `json:"scope"`
	PublicationApproved bool   `json:"publicationApproved"`
	ReviewRequired      bool   `json:"reviewRequired"`
	ReviewTrigger       string `json:"reviewTrigger"`
}

type ProvisionalApproval struct {
	Basis               string `json:"basis"`
	Scope               string `json:"scope"`
	PublicationApproved bool   `json:"publicationApproved"`
	ReviewRequired      bool   `json:"reviewRequired"`
	ReviewTrigger       string `json:"reviewTrigger"`
}

type Fixture struct {
	Scenario     string               `json:"scenario"`
	Authority    Authority            `json:"authority"`
	Observations []Observation        `json:"observations"`
	Drafts       []Draft              `json:"drafts"`
	Decisions    []Decision           `json:"decisions"`
	Provisional  *ProvisionalApproval `json:"provisionalApproval"`
}

type Receipt struct {
	Schema         string `json:"schema"`
	Scenario       string `json:"scenario"`
	Status         string `json:"status"`
	DraftID        string `json:"draftId"`
	ArtifactPath   string `json:"artifactPath,omitempty"`
	ArtifactDigest string `json:"artifactDigest"`
	// ObservationDigests binds the rendered evidence rows to the evaluated input.
	ObservationDigests  map[string]string `json:"observationDigests,omitempty"`
	ProvisionalApproved bool              `json:"provisionalApproved"`
	PublicationApproved bool              `json:"publicationApproved"`
	ReviewRequired      bool              `json:"reviewRequired"`
	ReviewTrigger       string            `json:"reviewTrigger"`
	AuthorityVerified   bool              `json:"authorityVerified"`
	Passed              bool              `json:"passed"`
	Reason              string            `json:"reason,omitempty"`
	Notes               []string          `json:"notes"`
}

func digest(text string) string {
	sum := sha256.Sum256([]byte(text))
	return "sha256:" + hex.EncodeToString(sum[:])
}

func findDraft(drafts []Draft, id string) (Draft, bool) {
	for _, draft := range drafts {
		if draft.ID == id {
			return draft, true
		}
	}
	return Draft{}, false
}

func findDecision(decisions []Decision, id string) (Decision, bool) {
	for _, decision := range decisions {
		if decision.ID == id {
			return decision, true
		}
	}
	return Decision{}, false
}

func tableCell(text string) string {
	text = strings.ReplaceAll(text, "|", "\\|")
	text = strings.ReplaceAll(text, "\n", " ")
	return text
}

func Render(fixture Fixture) (string, Receipt, error) {
	receipt := Receipt{
		Schema: "tai.reference.scn001-review-artifact/v0", Scenario: fixture.Scenario,
		AuthorityVerified: false, Notes: []string{
			"development-review-onlyの仮承認に基づく内部レビュー用Draft。公開済みではない。",
			"実在の規程・権限・利用者による承認ではない。",
		},
	}
	prov := fixture.Provisional
	dec02, hasDec02 := findDecision(fixture.Decisions, "DEC-02")
	d04, hasD04 := findDraft(fixture.Drafts, "D-04")
	if prov == nil || prov.Basis == "" || prov.Scope != "development-review-only" ||
		prov.PublicationApproved || !prov.ReviewRequired || prov.ReviewTrigger != "real-object" ||
		!hasDec02 || dec02.Status != "provisional" || dec02.Draft != "D-04" ||
		dec02.Scope != "development-review-only" || dec02.PublicationApproved ||
		!dec02.ReviewRequired || dec02.ReviewTrigger != "real-object" ||
		!hasD04 || d04.Published || fixture.Authority.Status != "unconfirmed" {
		receipt.Reason = "provisional approval or D-04 is incomplete"
		return "", receipt, fmt.Errorf("%s", receipt.Reason)
	}
	known := map[string]bool{}
	for _, observation := range fixture.Observations {
		known[observation.ID] = true
	}
	for _, reference := range d04.References {
		if !known[reference] {
			receipt.Reason = "D-04 references an unknown observation"
			return "", receipt, fmt.Errorf("%s", receipt.Reason)
		}
	}

	var markdown strings.Builder
	markdown.WriteString("# SCN-001 D-04 暫定案内（内部レビュー用）\n\n")
	markdown.WriteString("- 状態: `provisional`\n")
	markdown.WriteString("- 対象: SCN-001\n")
	markdown.WriteString("- 仮承認の根拠: `" + prov.Basis + "`\n")
	markdown.WriteString("- 適用範囲: `" + prov.Scope + "`\n")
	markdown.WriteString("- 公開承認: **なし**\n")
	markdown.WriteString("- 再レビュー: **必須**（`" + prov.ReviewTrigger + "`）\n")
	markdown.WriteString("- Authority: **未検証**\n\n")
	markdown.WriteString("> これは内部レビュー用のDraftです。公開済みの案内ではありません。\n\n")
	markdown.WriteString("## 案内文\n\n")
	markdown.WriteString(d04.Text + "\n\n")
	markdown.WriteString("## 根拠observation\n\n")
	markdown.WriteString("| ID | 原文 | 出典 | 版 | 取得時点 | availability | digest |\n")
	markdown.WriteString("| --- | --- | --- | --- | --- | --- | --- |\n")
	rendered := map[string]string{}
	for _, observation := range fixture.Observations {
		for _, reference := range d04.References {
			if observation.ID == reference {
				markdown.WriteString(fmt.Sprintf("| %s | %s | %s | %s | %s | %s | `%s` |\n",
					tableCell(observation.ID), tableCell(observation.Text), tableCell(observation.Source),
					tableCell(observation.SourceVersion), tableCell(observation.ObservedAt),
					tableCell(observation.Availability), digest(observation.Text)))
				rendered[observation.ID] = digest(observation.Text)
			}
		}
	}
	markdown.WriteString("\n## 未決\n\n")
	markdown.WriteString("- `authority:unknown`\n")
	markdown.WriteString("- `publication:unapproved`\n")
	markdown.WriteString("- `review:real-object`\n\n")
	markdown.WriteString("## 境界\n\n")
	markdown.WriteString("- 仮承認は`development-review-only`であり、公開承認ではない。\n")
	markdown.WriteString("- 実物ベースの再レビュー（R-01〜R-07）が完了するまで公開しない。\n")
	markdown.WriteString("- この文書は合成fixtureから生成した参照成果物であり、実在の規程を示さない。\n")

	content := markdown.String()
	receipt.Status = "provisional"
	receipt.DraftID = d04.ID
	receipt.ProvisionalApproved = true
	receipt.PublicationApproved = false
	receipt.ReviewRequired = true
	receipt.ReviewTrigger = prov.ReviewTrigger
	receipt.ArtifactDigest = digest(content)
	receipt.ObservationDigests = rendered
	receipt.Passed = true
	return content, receipt, nil
}

func main() {
	fixturePath := flag.String("fixture", "", "SCN-001 fixture")
	outPath := flag.String("out", "", "write the review artifact Markdown")
	flag.Parse()
	if *fixturePath == "" || *outPath == "" {
		fmt.Fprintln(os.Stderr, "-fixture and -out are required")
		os.Exit(2)
	}
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
	content, receipt, err := Render(fixture)
	if err != nil {
		encoded, _ := json.MarshalIndent(receipt, "", "  ")
		os.Stdout.Write(append(encoded, '\n'))
		os.Exit(1)
	}
	if err := os.MkdirAll(filepath.Dir(*outPath), 0o755); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	if err := os.WriteFile(*outPath, []byte(content), 0o644); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	receipt.ArtifactPath = *outPath
	encoded, err := json.MarshalIndent(receipt, "", "  ")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	os.Stdout.Write(append(encoded, '\n'))
}
