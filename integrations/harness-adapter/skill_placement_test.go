package harnessadapter

import (
	"os"
	"path/filepath"
	"strings"
	"testing"
)

// writeSkill creates a Product Skill directory shaped like the real ones
// (skills/<id>/SKILL.md plus an optional references/ subtree).
func writeSkill(t *testing.T, dir, id string, withRefs bool) string {
	t.Helper()
	root := filepath.Join(dir, id)
	if err := os.MkdirAll(root, 0o755); err != nil {
		t.Fatal(err)
	}
	body := "---\nname: " + id + "\ndescription: test skill\n---\n\n# body\n"
	if err := os.WriteFile(filepath.Join(root, "SKILL.md"), []byte(body), 0o644); err != nil {
		t.Fatal(err)
	}
	if withRefs {
		refs := filepath.Join(root, "references")
		if err := os.MkdirAll(refs, 0o755); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(filepath.Join(refs, "r.md"), []byte("ref\n"), 0o644); err != nil {
			t.Fatal(err)
		}
	}
	return root
}

func TestSkillIDReadsFrontmatterName(t *testing.T) {
	dir := t.TempDir()
	src := writeSkill(t, dir, "yi-tei-modeling", false)
	id, err := SkillID(src)
	if err != nil {
		t.Fatalf("SkillID: %v", err)
	}
	if id != "yi-tei-modeling" {
		t.Fatalf("id = %q", id)
	}
}

// TestSkillIDRefusesToGuess keeps a malformed skill from being placed under an
// invented id, because an invisible skill is worse than a failed placement.
func TestSkillIDRefusesToGuess(t *testing.T) {
	dir := t.TempDir()
	cases := map[string]string{
		"no-frontmatter": "# just a body\n",
		"unclosed":       "---\nname: x\n",
		"no-name":        "---\ndescription: d\n---\n",
		"empty-name":     "---\nname:   \ndescription: d\n---\n",
	}
	for name, body := range cases {
		t.Run(name, func(t *testing.T) {
			root := filepath.Join(dir, name)
			if err := os.MkdirAll(root, 0o755); err != nil {
				t.Fatal(err)
			}
			if err := os.WriteFile(filepath.Join(root, "SKILL.md"), []byte(body), 0o644); err != nil {
				t.Fatal(err)
			}
			if _, err := SkillID(root); err == nil {
				t.Fatal("a malformed skill produced an id")
			}
		})
	}
}

// TestPlaceSkillDigestsActualBytes checks the placement record names the exact
// bytes written, and that the pin starts at "unknown" load state.
func TestPlaceSkillDigestsActualBytes(t *testing.T) {
	dir := t.TempDir()
	src := writeSkill(t, dir, "yi-tei-modeling", true)
	root := filepath.Join(t.TempDir(), "skills")
	pl, err := PlaceSkill(root, src, false)
	if err != nil {
		t.Fatalf("PlaceSkill: %v", err)
	}
	data, err := os.ReadFile(pl.PlacedPath)
	if err != nil {
		t.Fatalf("read placed: %v", err)
	}
	if pl.BytesSHA256 != DigestBytes(data) {
		t.Fatalf("digest does not match placed bytes: %s vs %s", pl.BytesSHA256, DigestBytes(data))
	}
	if pl.ByteCount != int64(len(data)) {
		t.Fatalf("byte count = %d, want %d", pl.ByteCount, len(data))
	}
	if !strings.Contains(pl.Note, "references") {
		t.Fatalf("placement did not disclose that references were left behind: %q", pl.Note)
	}
	pin := SkillPinFromPlacement(pl)
	if pin.LoadState != LoadUnknown {
		t.Fatalf("pin load state = %q, want unknown", pin.LoadState)
	}
}

// TestPlaceSkillWithReferences checks the opt-in path copies references and
// reports what it could not copy.
func TestPlaceSkillWithReferences(t *testing.T) {
	dir := t.TempDir()
	src := writeSkill(t, dir, "yi-tei-modeling", true)
	root := filepath.Join(t.TempDir(), "skills")
	pl, err := PlaceSkill(root, src, true)
	if err != nil {
		t.Fatalf("PlaceSkill: %v", err)
	}
	if pl.Note != "" {
		t.Fatalf("unexpected note: %q", pl.Note)
	}
	if _, err := os.Stat(filepath.Join(filepath.Dir(pl.PlacedPath), "references", "r.md")); err != nil {
		t.Fatalf("reference not copied: %v", err)
	}
}

// TestDSHSkillRootsOrder documents the vendor root order rather than hard-coding
// it as a contract other adapters must satisfy.
func TestDSHSkillRootsOrder(t *testing.T) {
	roots := DSHSkillRoots(`C:\repo`, `C:\u\.dsh`, `C:\u\.agents`)
	if len(roots) != 4 {
		t.Fatalf("expected 4 roots, got %d", len(roots))
	}
	for i := 1; i < len(roots); i++ {
		if roots[i-1].Rank > roots[i].Rank {
			t.Fatalf("roots out of rank order: %v", roots)
		}
	}
	if !strings.HasSuffix(roots[0].Path, filepath.Join(".dsh", "skills")) {
		t.Fatalf("first root is not the project .dsh root: %s", roots[0].Path)
	}
	for _, r := range roots {
		if r.Harness != "dsh" {
			t.Fatalf("root is not labelled as DSH-specific: %+v", r)
		}
	}
}
