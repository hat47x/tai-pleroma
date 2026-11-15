package harnessadapter

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// SkillPlacement describes where a Product Skill was made visible to a harness
// and what bytes were placed there.
//
// Placement is not loading. A skill sitting in a scanned root has been made
// discoverable; whether the model read it is a separate observation that only
// the harness's own tool calls can show (TAI #488, TAI Draft #270 SK-02 RD).
type SkillPlacement struct {
	// ID is the skill id from the Product Skill frontmatter `name`.
	ID string
	// SourcePath is the authoritative product location.
	SourcePath string
	// PlacedPath is where the harness scans.
	PlacedPath string
	// BytesSHA256 digests the bytes actually placed.
	BytesSHA256 string
	// ByteCount is the size of those bytes.
	ByteCount int64
	// Mode records how the bytes got there: "copy" or "symlink".
	Mode string
	// Note records anything a reader must know (e.g. "references not copied").
	Note string
}

// SkillRoot describes one harness skill root. Harnesses differ, so the root set
// is data, not a constant.
type SkillRoot struct {
	// Harness names the family the root belongs to.
	Harness string
	// Path is the scanned directory.
	Path string
	// Rank mirrors the harness's own priority when it publishes one.
	Rank int
}

// DSHSkillRoots returns the local skill roots DSH's filesystem provider scans,
// in its documented rank order. The project root is the nearest ancestor
// containing .git; without one, the cwd is used. This is a transcription of
// vendor-documented behaviour, not a DSH-specific contract other adapters must
// satisfy.
func DSHSkillRoots(projectRoot, dshHome, agentsHome string) []SkillRoot {
	return []SkillRoot{
		{Harness: "dsh", Path: filepath.Join(projectRoot, ".dsh", "skills"), Rank: 100},
		{Harness: "dsh", Path: filepath.Join(projectRoot, ".agents", "skills"), Rank: 200},
		{Harness: "dsh", Path: filepath.Join(dshHome, "skills"), Rank: 400},
		{Harness: "dsh", Path: filepath.Join(agentsHome, "skills"), Rank: 500},
	}
}

// SkillRootFor returns the skill root a named harness scans under projectRoot.
// It returns "" for a harness whose root this package does not know, so a caller
// reports the gap instead of placing bytes somewhere the harness never reads.
func SkillRootFor(harness, projectRoot string) string {
	switch harness {
	case "dsh-headless", "dsh":
		return filepath.Join(projectRoot, ".dsh", "skills")
	case "claude-code":
		return filepath.Join(projectRoot, ".claude", "skills")
	case "step-cli":
		// Step scans .agents/skills and .claude/skills in the cwd and ancestors.
		return filepath.Join(projectRoot, ".agents", "skills")
	}
	return ""
}

// PlaceSkill copies a Product Skill directory into a harness skill root as
// <root>/<id>/SKILL.md, mirroring the directory-bundle shape both DSH and
// Claude Code expect. It returns the placement record, including the digest of
// the bytes actually written.
//
// Only SKILL.md is copied by default. References and scripts are listed in the
// note so a reader knows the placed bundle is not the whole product skill, and
// a skill that needs its references must be re-placed with them explicitly.
func PlaceSkill(root, sourceDir string, withReferences bool) (SkillPlacement, error) {
	id, err := SkillID(sourceDir)
	if err != nil {
		return SkillPlacement{}, err
	}
	src := filepath.Join(sourceDir, "SKILL.md")
	data, err := os.ReadFile(src)
	if err != nil {
		return SkillPlacement{}, fmt.Errorf("read %s: %w", src, err)
	}
	destDir := filepath.Join(root, id)
	if err := os.MkdirAll(destDir, 0o755); err != nil {
		return SkillPlacement{}, fmt.Errorf("mkdir %s: %w", destDir, err)
	}
	dest := filepath.Join(destDir, "SKILL.md")
	if err := os.WriteFile(dest, data, 0o644); err != nil {
		return SkillPlacement{}, fmt.Errorf("write %s: %w", dest, err)
	}
	sum := sha256.Sum256(data)
	pl := SkillPlacement{
		ID:          id,
		SourcePath:  sourceDir,
		PlacedPath:  dest,
		BytesSHA256: "sha256:" + hex.EncodeToString(sum[:]),
		ByteCount:   int64(len(data)),
		Mode:        "copy",
	}
	var missing []string
	if withReferences {
		refs := filepath.Join(sourceDir, "references")
		entries, err := os.ReadDir(refs)
		if err == nil {
			destRefs := filepath.Join(destDir, "references")
			if err := os.MkdirAll(destRefs, 0o755); err != nil {
				return pl, fmt.Errorf("mkdir %s: %w", destRefs, err)
			}
			for _, e := range entries {
				if e.IsDir() {
					continue
				}
				b, err := os.ReadFile(filepath.Join(refs, e.Name()))
				if err != nil {
					missing = append(missing, e.Name())
					continue
				}
				if err := os.WriteFile(filepath.Join(destRefs, e.Name()), b, 0o644); err != nil {
					missing = append(missing, e.Name())
					continue
				}
			}
		}
	}
	if withReferences && len(missing) > 0 {
		pl.Note = "references not copied: " + strings.Join(missing, ", ")
	} else if !withReferences {
		pl.Note = "only SKILL.md placed; references and scripts are not visible to the harness"
	}
	return pl, nil
}

// SkillID reads the `name:` field from a Product Skill's YAML frontmatter. It
// parses the smallest possible subset of frontmatter and refuses to guess: a
// missing or malformed name is an error, because a skill placed under the wrong
// id is invisible rather than broken.
func SkillID(sourceDir string) (string, error) {
	data, err := os.ReadFile(filepath.Join(sourceDir, "SKILL.md"))
	if err != nil {
		return "", fmt.Errorf("read SKILL.md in %s: %w", sourceDir, err)
	}
	text := string(data)
	if !strings.HasPrefix(text, "---") {
		return "", fmt.Errorf("%s: SKILL.md has no YAML frontmatter", sourceDir)
	}
	rest := text[len("---"):]
	end := strings.Index(rest, "\n---")
	if end < 0 {
		return "", fmt.Errorf("%s: SKILL.md frontmatter is not closed", sourceDir)
	}
	for _, line := range strings.Split(rest[:end], "\n") {
		line = strings.TrimSpace(line)
		if !strings.HasPrefix(line, "name:") {
			continue
		}
		v := strings.TrimSpace(strings.TrimPrefix(line, "name:"))
		v = strings.Trim(v, `"'`)
		if v == "" {
			return "", fmt.Errorf("%s: SKILL.md frontmatter name is empty", sourceDir)
		}
		return v, nil
	}
	return "", fmt.Errorf("%s: SKILL.md frontmatter has no name field", sourceDir)
}

// SkillPinFromPlacement converts a placement into a contract SkillPin. The load
// state starts at unknown: only a harness tool call can change it.
func SkillPinFromPlacement(p SkillPlacement) SkillPin {
	return SkillPin{
		ID:          p.ID,
		PlacedPath:  p.PlacedPath,
		BytesSHA256: p.BytesSHA256,
		LoadState:   LoadUnknown,
	}
}
