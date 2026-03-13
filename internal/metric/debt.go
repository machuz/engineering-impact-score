package metric

import (
	"context"
	"math"

	"github.com/machuz/engineering-impact-score/internal/git"
)

type DebtData struct {
	Generated map[string]int
	Cleaned   map[string]int
}

// ResolveFunc maps a git author name to its canonical name
type ResolveFunc func(string) string

// ProgressFunc reports debt analysis progress (done, total fix commits)
type ProgressFunc func(done, total int)

// CalcDebt calculates debt cleanup scores on a 0-100 scale.
// 50 = neutral (equal generation and cleanup, or insufficient data)
// >50 = net cleaner, <50 = net debt creator
// Formula: 50 + 50 * (cleaned - generated) / (cleaned + generated)
func CalcDebt(ctx context.Context, repoPath string, fixCommits []git.Commit, maxSample int, debtThreshold int, resolve ResolveFunc, progressFn ProgressFunc) (map[string]float64, *DebtData) {
	generated := make(map[string]int)
	cleaned := make(map[string]int)

	if resolve == nil {
		resolve = func(s string) string { return s }
	}

	// Sample fix commits
	sample := fixCommits
	if len(sample) > maxSample {
		sample = sample[:maxSample]
	}

	total := len(sample)
	for i, fc := range sample {
		// Check context cancellation
		if ctx.Err() != nil {
			break
		}

		fixer := resolve(fc.Author)

		// Get changed files
		files, err := git.DiffTreeFiles(ctx, repoPath, fc.Hash)
		if err != nil {
			if progressFn != nil {
				progressFn(i+1, total)
			}
			continue
		}

		for _, f := range files {
			if f == "" {
				continue
			}
			// Blame at parent to find original authors
			authors, err := git.BlameFileAtParent(ctx, repoPath, fc.Hash, f)
			if err != nil {
				continue
			}

			for _, origAuthor := range authors {
				origAuthor = resolve(origAuthor)
				if origAuthor != fixer && origAuthor != "" {
					generated[origAuthor]++
					cleaned[fixer]++
				}
			}
		}

		if progressFn != nil {
			progressFn(i+1, total)
		}
	}

	// Calculate scores on 0-100 scale
	result := make(map[string]float64)

	// Collect all authors
	allAuthors := make(map[string]bool)
	for a := range generated {
		allAuthors[a] = true
	}
	for a := range cleaned {
		allAuthors[a] = true
	}

	for author := range allAuthors {
		gen := generated[author]
		cln := cleaned[author]
		total := gen + cln

		if total < debtThreshold {
			result[author] = 50 // neutral: insufficient data
			continue
		}

		// Score: 50 + 50 * (cleaned - generated) / (cleaned + generated)
		// Range: 0 (pure debt creator) to 100 (pure cleaner), 50 = balanced
		score := 50.0 + 50.0*float64(cln-gen)/float64(total)
		result[author] = math.Max(0, math.Min(100, score))
	}

	return result, &DebtData{Generated: generated, Cleaned: cleaned}
}
