// Package harnessadapter holds the vendor-neutral contract for calling an
// external AI harness (DSH, Codex, Claude Code, ...) on behalf of a YI
// Constellation product, plus the smallest set of adapters needed to prove the
// contract is interchangeable.
//
// Scope boundary (TAI #168 §9 P-1..P-6, TEI ADR-0048, TAI Draft #270 SK-02/03):
// the adapter covers session reference, context projection, tool invocation,
// skill use, result receipt, diagnostics and evidence tracking. It does NOT own
// product semantics, source revision authority, permission, information
// disclosure or real side effects. Those stay with the product, the host and
// the provider.
//
// Nothing in this package implements an agent loop, a model router, a central
// session server, a second registry or an authorization engine.
package harnessadapter
