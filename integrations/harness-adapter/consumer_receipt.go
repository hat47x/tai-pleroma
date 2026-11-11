package harnessadapter

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
	"path/filepath"
	"strings"
)

// ConsumerReceipt observes what a consumer actually read back. It is the only
// thing that may move a Result's Receipt away from `not-observed`.
//
// The rule the contract encodes: a harness reporting "delivered" is not a
// receipt, and neither is the adapter reading its own final text back. A receipt
// requires a reader that is not the producer, reading bytes from a location the
// producer wrote, and comparing the digest.
//
// This package provides two honest readers and no third:
//   - FileReadback: a separate process-free read of a file the producer wrote.
//   - DirectReadback: a bounded read of the final text compared byte-for-byte
//     against what the producer recorded, which is the weakest useful form and
//     is labelled as such.
//
// A reader never upgrades a receipt on the producer's word.
type ConsumerReceipt struct {
	// Consumer names the reader.
	Consumer string `json:"consumer"`
	// State is the observed receipt state.
	State ReceiptState `json:"state"`
	// Path is the file read, when the reader read a file.
	Path string `json:"path,omitempty"`
	// BytesSHA256 digests the bytes actually read.
	BytesSHA256 string `json:"bytesSha256,omitempty"`
	// ByteCount is the size of those bytes.
	ByteCount int64 `json:"byteCount,omitempty"`
	// ExpectedSHA256 is what the producer recorded, when it recorded one.
	ExpectedSHA256 string `json:"expectedSha256,omitempty"`
	// Matches reports whether the read bytes matched the expected digest. Nil
	// means no comparison was made, which is different from a mismatch.
	Matches *bool `json:"matches,omitempty"`
	// Note carries a non-secret explanation.
	Note string `json:"note,omitempty"`
}

// ReceiptFor converts the observation into a contract Receipt.
func (c ConsumerReceipt) ReceiptFor() Receipt {
	return Receipt{
		State:       c.State,
		Consumer:    c.Consumer,
		BytesSHA256: c.BytesSHA256,
		ByteCount:   c.ByteCount,
		Note:        c.Note,
	}
}

// String renders a one-line summary.
func (c ConsumerReceipt) String() string {
	m := "n/a"
	if c.Matches != nil {
		if *c.Matches {
			m = "true"
		} else {
			m = "false"
		}
	}
	return fmt.Sprintf("receipt %s: state=%s bytes=%d matches=%s", c.Consumer, c.State, c.ByteCount, m)
}

// FileReadback is the strong form: a reader opens a file the producer wrote, in
// a directory the consumer is allowed to read, and digests what is actually on
// disk.
//
// It does not go through the harness, does not use the adapter's recorded text,
// and does not trust the producer's claim that it wrote anything. It reports
// `not-observed` when the file is absent.
func FileReadback(consumer, path, expectedSHA256 string) ConsumerReceipt {
	c := ConsumerReceipt{Consumer: consumer, Path: path, ExpectedSHA256: expectedSHA256, State: ReceiptNotObserved}
	abs, err := filepath.Abs(path)
	if err != nil {
		c.Note = "path could not be resolved"
		return c
	}
	info, err := os.Stat(abs)
	if err != nil {
		c.Note = "no readable file at the expected location"
		return c
	}
	if !info.Mode().IsRegular() {
		c.Note = "the expected location is not a regular file"
		return c
	}
	b, err := os.ReadFile(abs)
	if err != nil {
		c.Note = "the file exists but could not be read"
		return c
	}
	c.ByteCount = int64(len(b))
	if len(b) == 0 {
		c.State = ReceiptPartial
		c.Note = "the consumer read an empty file; an empty receipt is not a full one"
		return c
	}
	sum := sha256.Sum256(b)
	c.BytesSHA256 = "sha256:" + hex.EncodeToString(sum[:])
	if expectedSHA256 == "" {
		// No expected digest was recorded, so the read is real but unverified
		// against the producer. That is `partial`, not `complete`.
		c.State = ReceiptPartial
		c.Note = "bytes were read, but the producer recorded no digest to compare against"
		return c
	}
	matches := c.BytesSHA256 == expectedSHA256
	c.Matches = &matches
	if matches {
		c.State = ReceiptComplete
		c.Note = "a separate reader read the bytes the producer wrote and the digest matched"
	} else {
		c.State = ReceiptPartial
		c.Note = "a separate reader read bytes at the location, but they do not match the producer's digest"
	}
	return c
}

// DirectReadback is the weak form: the consumer compares the arm's own final text
// against a digest the caller recorded independently.
//
// It exists because most pilots have no consumer at all, and a labelled weak
// receipt is more useful than a missing one — but it must never be presented as
// an independent read of the delivered bytes. The Note says so.
func DirectReadback(consumer string, res *Result, expectedSHA256 string) ConsumerReceipt {
	c := ConsumerReceipt{Consumer: consumer, ExpectedSHA256: expectedSHA256, State: ReceiptNotObserved}
	if res == nil || strings.TrimSpace(res.FinalText) == "" {
		c.Note = "the arm produced no final text"
		return c
	}
	c.ByteCount = int64(len(res.FinalText))
	c.BytesSHA256 = DigestString(res.FinalText)
	if expectedSHA256 == "" {
		c.State = ReceiptPartial
		c.Note = "weak receipt: the arm's own final text was digested; nothing independent consumed it"
		return c
	}
	matches := c.BytesSHA256 == expectedSHA256
	c.Matches = &matches
	if matches {
		c.State = ReceiptPartial
		c.Note = "weak receipt: the arm's final text matches the expected digest, but no independent consumer read the delivered bytes"
	} else {
		c.Note = "the arm's final text does not match the expected digest"
	}
	return c
}

// ApplyReceipt copies a consumer's observation onto a Result. The adapter never
// writes a receipt itself; this is the consumer's write.
func ApplyReceipt(res *Result, c ConsumerReceipt) {
	if res == nil {
		return
	}
	res.Receipt = c.ReceiptFor()
}
