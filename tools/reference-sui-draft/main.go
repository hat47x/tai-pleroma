package main

import (
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"strings"
)

type SUILink struct {
	Passed      bool     `json:"passed"`
	LinkedCards []string `json:"linkedCards"`
}

type Receipt struct {
	Schema             string   `json:"schema"`
	ArtifactDigest     string   `json:"artifactDigest"`
	LinkedCards        []string `json:"linkedCards"`
	PublicationBlocked bool     `json:"publicationBlocked"`
	Passed             bool     `json:"passed"`
	Reason             string   `json:"reason,omitempty"`
	Notes              []string `json:"notes"`
}

func digest(raw []byte) string {
	sum := sha256.Sum256(raw)
	return "sha256:" + hex.EncodeToString(sum[:])
}

func Link(link SUILink, artifact []byte) Receipt {
	text := string(artifact)
	receipt := Receipt{
		Schema: "tai.reference.sui-draft-link/v0", ArtifactDigest: digest(artifact),
		Notes: []string{
			"SUIのcard/island照合がD-04の観測行と公開境界に現れているかを確認する。",
			"意味の受理・公開承認・Authorityを検証しない。",
		},
	}
	if !link.Passed || len(link.LinkedCards) != 5 {
		receipt.Reason = "SUI link is not a passed 5-card link"
		return receipt
	}
	for _, id := range link.LinkedCards {
		if !strings.Contains(text, "| "+id+" |") {
			receipt.Reason = "artifact is missing linked card: " + id
			return receipt
		}
	}
	required := []string{
		"- 状態: `provisional`",
		"- 公開承認: **なし**",
		"- Authority: **未検証**",
		"- `review:real-object`",
	}
	for _, marker := range required {
		if !strings.Contains(text, marker) {
			receipt.Reason = "artifact is missing boundary marker: " + marker
			return receipt
		}
	}
	o08Unavailable := false
	for _, line := range strings.Split(text, "\n") {
		if strings.HasPrefix(line, "| O-08 |") && strings.Contains(line, "| unavailable |") {
			o08Unavailable = true
		}
	}
	if !o08Unavailable {
		receipt.Reason = "O-08 must remain unavailable in the artifact"
		return receipt
	}
	receipt.LinkedCards = append([]string(nil), link.LinkedCards...)
	receipt.PublicationBlocked = true
	receipt.Passed = true
	return receipt
}

func main() {
	linkPath := flag.String("sui-link", "", "SUI link receipt")
	artifactPath := flag.String("artifact", "", "D-04 artifact")
	outPath := flag.String("out", "", "write receipt")
	flag.Parse()
	if *linkPath == "" || *artifactPath == "" {
		fmt.Fprintln(os.Stderr, "-sui-link and -artifact are required")
		os.Exit(2)
	}
	rawLink, err := os.ReadFile(*linkPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	var link SUILink
	if err := json.Unmarshal(rawLink, &link); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	artifact, err := os.ReadFile(*artifactPath)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(2)
	}
	receipt := Link(link, artifact)
	encoded, _ := json.MarshalIndent(receipt, "", "  ")
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
