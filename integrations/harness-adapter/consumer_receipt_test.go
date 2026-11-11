package harnessadapter

import (
	"os"
	"path/filepath"
	"testing"
)

// TestFileReadbackCompleteRequiresMatchingDigest is the strong form: a separate
// reader read bytes on disk and they match what the producer recorded.
func TestFileReadbackCompleteRequiresMatchingDigest(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "answer.md")
	content := []byte("# answer\n\nthe total is std.money\n")
	if err := os.WriteFile(path, content, 0o644); err != nil {
		t.Fatal(err)
	}
	got := FileReadback("sho-assembler", path, DigestBytes(content))
	if got.State != ReceiptComplete {
		t.Fatalf("state = %q, want complete (%s)", got.State, got.Note)
	}
	if got.Matches == nil || !*got.Matches {
		t.Fatal("the digest match was not recorded")
	}
	if got.BytesSHA256 != DigestBytes(content) {
		t.Fatalf("digest = %q", got.BytesSHA256)
	}
}

// TestFileReadbackPartialWhenDigestMissing keeps a real read from being called
// complete without a producer digest to compare against.
func TestFileReadbackPartialWhenDigestMissing(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "answer.md")
	if err := os.WriteFile(path, []byte("x"), 0o644); err != nil {
		t.Fatal(err)
	}
	got := FileReadback("reader", path, "")
	if got.State != ReceiptPartial {
		t.Fatalf("state = %q, want partial", got.State)
	}
	if got.Matches != nil {
		t.Fatal("a comparison was claimed without an expected digest")
	}
}

// TestFileReadbackMismatchIsPartialNotComplete keeps a wrong file from reading as
// a receipt.
func TestFileReadbackMismatchIsPartialNotComplete(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "answer.md")
	if err := os.WriteFile(path, []byte("different"), 0o644); err != nil {
		t.Fatal(err)
	}
	got := FileReadback("reader", path, DigestString("expected"))
	if got.State == ReceiptComplete {
		t.Fatal("a mismatched file was reported complete")
	}
	if got.Matches == nil || *got.Matches {
		t.Fatalf("the mismatch was not recorded: %+v", got.Matches)
	}
}

// TestFileReadbackAbsentIsNotObserved keeps a missing file from being an empty
// success.
func TestFileReadbackAbsentIsNotObserved(t *testing.T) {
	got := FileReadback("reader", filepath.Join(t.TempDir(), "missing.md"), "sha256:x")
	if got.State != ReceiptNotObserved {
		t.Fatalf("state = %q, want not-observed", got.State)
	}
	if got.Note == "" {
		t.Fatal("an absent file carried no explanation")
	}
}

// TestFileReadbackEmptyFileIsPartial keeps a zero-byte read from being complete.
func TestFileReadbackEmptyFileIsPartial(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "empty.md")
	if err := os.WriteFile(path, nil, 0o644); err != nil {
		t.Fatal(err)
	}
	got := FileReadback("reader", path, "")
	if got.State != ReceiptPartial {
		t.Fatalf("state = %q, want partial", got.State)
	}
	if got.Note == "" {
		t.Fatal("an empty read carried no explanation")
	}
}

// TestDirectReadbackIsLabelledWeak is the anti-overclaim guard: the weak form must
// never report `complete`, and its note must say nothing independent consumed it.
func TestDirectReadbackIsLabelledWeak(t *testing.T) {
	res := &Result{Adapter: "dsh-headless", FinalText: "the answer"}
	got := DirectReadback("adapter-self-check", res, DigestString("the answer"))
	if got.State == ReceiptComplete {
		t.Fatal("the weak readback reported complete")
	}
	if got.State != ReceiptPartial {
		t.Fatalf("state = %q, want partial", got.State)
	}
	if got.Matches == nil || !*got.Matches {
		t.Fatal("the digest comparison was not recorded")
	}
	if !containsSubstring(got.Note, "no independent consumer") {
		t.Fatalf("the weakness was not disclosed: %q", got.Note)
	}
}

// TestDirectReadbackNoAnswerIsNotObserved stops a silent arm from producing a
// receipt.
func TestDirectReadbackNoAnswerIsNotObserved(t *testing.T) {
	got := DirectReadback("reader", &Result{FinalText: "   "}, "sha256:x")
	if got.State != ReceiptNotObserved {
		t.Fatalf("state = %q, want not-observed", got.State)
	}
}

// TestApplyReceiptIsTheConsumersWrite checks the contract boundary: a receipt
// appears only when a consumer writes it.
func TestApplyReceiptIsTheConsumersWrite(t *testing.T) {
	res := &Result{Adapter: "x", Receipt: Receipt{State: ReceiptNotObserved, Consumer: "x"}}
	if res.Receipt.State != ReceiptNotObserved {
		t.Fatal("a fresh result did not start at not-observed")
	}
	ApplyReceipt(res, ConsumerReceipt{Consumer: "reader", State: ReceiptComplete, BytesSHA256: "sha256:a", ByteCount: 1})
	if res.Receipt.State != ReceiptComplete || res.Receipt.Consumer != "reader" {
		t.Fatalf("the consumer's receipt was not applied: %+v", res.Receipt)
	}
}

func containsSubstring(s, sub string) bool {
	return len(s) >= len(sub) && (s == sub || (len(sub) > 0 && indexOfStr(s, sub) >= 0))
}

func indexOfStr(s, sub string) int {
	for i := 0; i+len(sub) <= len(s); i++ {
		if s[i:i+len(sub)] == sub {
			return i
		}
	}
	return -1
}
