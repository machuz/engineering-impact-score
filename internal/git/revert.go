package git

import (
	"context"
	"regexp"
	"strings"
)

var revertHashPattern = regexp.MustCompile(`This reverts commit ([0-9a-f]{7,40})`)

// FindRevertedCommits detects commits that have been reverted and returns
// the set of commit hashes that should be excluded from metric calculations.
//
// This handles:
//   - Non-merge reverts: `git revert <hash>` → excludes original + revert commit
//   - Merge reverts (PR reverts): excludes all commits in the merged branch
//   - Revert-of-revert: if a revert is itself reverted, the original is reinstated
//
// Both the reverted original commits and the revert commits themselves are excluded,
// so the net effect is as if the reverted changes never happened.
func FindRevertedCommits(ctx context.Context, repoPath string) (map[string]bool, error) {
	// Find commits containing "This reverts commit <hash>" in their body.
	// --all searches all branches; --format outputs a parseable record per commit.
	lines, err := RunLines(ctx, repoPath,
		"log", "--all",
		"--grep=This reverts commit",
		"--format=REVERT_RECORD:%H%n%B%n---END_REVERT_RECORD---",
	)
	if err != nil {
		return nil, err
	}

	// Parse revert relationships: revertHash → originalHash
	type revertPair struct {
		revertHash   string
		originalHash string
	}
	var pairs []revertPair

	var currentHash string
	var bodyLines []string

	flush := func() {
		if currentHash == "" {
			return
		}
		body := strings.Join(bodyLines, "\n")
		if m := revertHashPattern.FindStringSubmatch(body); len(m) > 1 {
			pairs = append(pairs, revertPair{
				revertHash:   currentHash,
				originalHash: m[1],
			})
		}
		currentHash = ""
		bodyLines = nil
	}

	for _, line := range lines {
		if strings.HasPrefix(line, "REVERT_RECORD:") {
			flush()
			currentHash = line[len("REVERT_RECORD:"):]
			continue
		}
		if line == "---END_REVERT_RECORD---" {
			flush()
			continue
		}
		if currentHash != "" {
			bodyLines = append(bodyLines, line)
		}
	}
	flush()

	if len(pairs) == 0 {
		return nil, nil
	}

	// Build revert graph: for each commit, which commits revert it?
	// revertedBy[A] = [B] means "B reverts A"
	revertedBy := make(map[string][]string)
	for _, p := range pairs {
		revertedBy[p.originalHash] = append(revertedBy[p.originalHash], p.revertHash)
	}

	// Determine which commits are "effectively reverted" by walking the chain.
	// A commit is effectively reverted if it has a reverter that is NOT itself
	// effectively reverted. This handles revert-of-revert chains correctly:
	//   A reverted by B, B reverted by C → B is effectively reverted → A is NOT.
	memo := make(map[string]bool)
	var isEffectivelyReverted func(hash string) bool
	isEffectivelyReverted = func(hash string) bool {
		if v, ok := memo[hash]; ok {
			return v
		}
		// Prevent infinite recursion (shouldn't happen in practice)
		memo[hash] = false
		reverters := revertedBy[hash]
		if len(reverters) == 0 {
			return false
		}
		// A commit is effectively reverted if ANY of its reverters is still active
		for _, r := range reverters {
			if !isEffectivelyReverted(r) {
				memo[hash] = true
				return true
			}
		}
		// All reverters were themselves reverted → this commit is reinstated
		return false
	}

	excluded := make(map[string]bool)

	// Collect all hashes involved in revert relationships
	allHashes := make(map[string]bool)
	for _, p := range pairs {
		allHashes[p.originalHash] = true
		allHashes[p.revertHash] = true
	}

	for hash := range allHashes {
		if !isEffectivelyReverted(hash) {
			continue
		}
		excluded[hash] = true

		// If the reverted commit is a merge, find all commits in the merged branch.
		// git rev-list <merge>^1..<merge> returns commits reachable from the merge
		// but not from its first parent — i.e., the commits on the merged branch.
		branchCommits, err := RunLines(ctx, repoPath,
			"rev-list", hash+"^1.."+hash,
		)
		if err == nil {
			for _, bc := range branchCommits {
				if bc = strings.TrimSpace(bc); bc != "" {
					excluded[bc] = true
				}
			}
		}
	}

	return excluded, nil
}
