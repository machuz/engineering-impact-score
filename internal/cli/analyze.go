package cli

import (
	"context"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"time"

	"github.com/fatih/color"
	"github.com/machuz/engineering-impact-score/internal/config"
	"github.com/machuz/engineering-impact-score/internal/git"
	"github.com/machuz/engineering-impact-score/internal/metric"
	"github.com/machuz/engineering-impact-score/internal/output"
	"github.com/machuz/engineering-impact-score/internal/scorer"
)

func runAnalyze(args []string) error {
	fs := flag.NewFlagSet("analyze", flag.ExitOnError)
	configPath := fs.String("config", "eis.yaml", "Config file path")
	tau := fs.Float64("tau", 0, "Survival decay parameter (overrides config)")
	sampleSize := fs.Int("sample", 0, "Max files to blame per repo (overrides config)")
	workers := fs.Int("workers", 4, "Number of concurrent blame workers")

	if err := fs.Parse(args); err != nil {
		return err
	}

	repoPaths := fs.Args()
	if len(repoPaths) == 0 {
		repoPaths = []string{"."}
	}

	// Resolve to absolute paths
	for i, p := range repoPaths {
		abs, err := filepath.Abs(p)
		if err != nil {
			return fmt.Errorf("resolve path %s: %w", p, err)
		}
		repoPaths[i] = abs
	}

	// Load config
	cfg, err := config.Load(*configPath)
	if err != nil {
		return fmt.Errorf("load config: %w", err)
	}
	if *tau > 0 {
		cfg.Tau = *tau
	}
	if *sampleSize > 0 {
		cfg.SampleSize = *sampleSize
	}

	ctx := context.Background()
	start := time.Now()

	raw := metric.NewRawScores()

	// Track breadth (repos per author)
	authorRepos := make(map[string]map[string]bool)

	for _, repoPath := range repoPaths {
		// Verify it's a git repo
		if _, err := os.Stat(filepath.Join(repoPath, ".git")); os.IsNotExist(err) {
			fmt.Fprintf(os.Stderr, "SKIP: %s (not a git repo)\n", repoPath)
			continue
		}

		repoName := filepath.Base(repoPath)
		bold := color.New(color.Bold)
		bold.Printf("Analyzing: %s\n", repoName)

		// Step 1: Parse git log (feeds Production, Quality, Design)
		fmt.Fprintf(os.Stderr, "  [1/4] Parsing git log...\n")
		commits, err := git.ParseLog(ctx, repoPath)
		if err != nil {
			return fmt.Errorf("parse log %s: %w", repoName, err)
		}

		// Apply author aliases and filter excluded authors
		commits = filterCommits(commits, cfg)

		// Production
		prod := metric.CalcProduction(commits, cfg.ExcludeFilePatterns)
		mergeMap(raw.Production, prod)

		// Quality
		qual := metric.CalcQuality(commits)
		mergeMapAvg(raw.Quality, qual)

		// Design
		design := metric.CalcDesign(commits, cfg.ArchitecturePatterns)
		mergeMap(raw.Design, design)

		// Track breadth
		for _, c := range commits {
			if _, ok := authorRepos[c.Author]; !ok {
				authorRepos[c.Author] = make(map[string]bool)
			}
			authorRepos[c.Author][repoName] = true
		}

		// Step 2: Blame analysis (feeds Survival, Indispensability)
		fmt.Fprintf(os.Stderr, "  [2/4] Blame analysis...\n")
		files, err := git.ListFiles(ctx, repoPath, cfg.BlameExtensions)
		if err != nil {
			fmt.Fprintf(os.Stderr, "  Warning: could not list files: %v\n", err)
			continue
		}

		blameLines, err := git.ConcurrentBlameFiles(ctx, repoPath, files, cfg.SampleSize, *workers,
			func(done, total int) {
				fmt.Fprintf(os.Stderr, "  [2/4] Blame: %d/%d files\r", done, total)
			})
		if err != nil {
			fmt.Fprintf(os.Stderr, "  Warning: blame error: %v\n", err)
		}
		fmt.Fprintln(os.Stderr)

		// Apply aliases to blame lines
		for i := range blameLines {
			blameLines[i].Author = cfg.ResolveAuthor(blameLines[i].Author)
		}
		blameLines = filterBlameLines(blameLines, cfg)

		// Survival
		surv := metric.CalcSurvival(blameLines, cfg.Tau)
		mergeMap(raw.Survival, surv)

		// Indispensability
		indisp, risks := metric.CalcIndispensability(blameLines, cfg.BusFactor.Critical, cfg.BusFactor.High)
		mergeMap(raw.Indispensability, indisp)

		// Step 3: Debt cleanup
		fmt.Fprintf(os.Stderr, "  [3/4] Debt analysis...\n")
		fixCommits := metric.GetFixCommits(commits)
		debt, _ := metric.CalcDebt(ctx, repoPath, fixCommits, 50, cfg.DebtThreshold)
		mergeMap(raw.DebtCleanup, debt)

		// Step 4: Output per-repo bus factor
		if len(risks) > 0 {
			output.PrintBusFactorRisks(risks)
		}
	}

	// Breadth
	for author, repos := range authorRepos {
		raw.Breadth[author] = float64(len(repos))
	}

	// Score and rank
	results := scorer.Score(raw, cfg)

	// Filter out excluded authors from results
	var filtered []scorer.Result
	for _, r := range results {
		if !cfg.IsExcludedAuthor(r.Author) {
			filtered = append(filtered, r)
		}
	}

	// Output
	elapsed := time.Since(start)
	output.PrintSummary(filtered, len(repoPaths))
	output.PrintRankings(filtered)

	color.New(color.FgHiBlack).Printf("Completed in %s\n", elapsed.Round(time.Second))

	return nil
}

func filterCommits(commits []git.Commit, cfg *config.Config) []git.Commit {
	var result []git.Commit
	for _, c := range commits {
		c.Author = cfg.ResolveAuthor(c.Author)
		if cfg.IsExcludedAuthor(c.Author) {
			continue
		}
		result = append(result, c)
	}
	return result
}

func filterBlameLines(lines []git.BlameLine, cfg *config.Config) []git.BlameLine {
	var result []git.BlameLine
	for _, bl := range lines {
		if !cfg.IsExcludedAuthor(bl.Author) {
			result = append(result, bl)
		}
	}
	return result
}

func mergeMap(dst, src map[string]float64) {
	for k, v := range src {
		dst[k] += v
	}
}

// mergeMapAvg keeps a running average for quality scores across repos
func mergeMapAvg(dst, src map[string]float64) {
	for k, v := range src {
		if existing, ok := dst[k]; ok {
			dst[k] = (existing + v) / 2
		} else {
			dst[k] = v
		}
	}
}
