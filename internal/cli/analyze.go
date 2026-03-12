package cli

import (
	"context"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"strings"
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
	recursive := fs.Bool("recursive", false, "Recursively find git repos under given paths")
	maxDepth := fs.Int("depth", 2, "Max directory depth for recursive search")

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

	// Recursive: find git repos under given paths
	if *recursive {
		var discovered []string
		for _, root := range repoPaths {
			repos, err := findGitRepos(root, *maxDepth)
			if err != nil {
				return fmt.Errorf("scan %s: %w", root, err)
			}
			discovered = append(discovered, repos...)
		}
		if len(discovered) == 0 {
			return fmt.Errorf("no git repos found under %v (depth=%d)", repoPaths, *maxDepth)
		}
		repoPaths = discovered
		fmt.Fprintf(os.Stderr, "Found %d git repos\n\n", len(repoPaths))
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

	// Print alias info if configured
	if len(cfg.Aliases) > 0 {
		fmt.Fprintf(os.Stderr, "Loaded %d author aliases from config\n", len(cfg.Aliases))
	}

	ctx := context.Background()
	start := time.Now()

	raw := metric.NewRawScores()
	qualityCounts := make(map[string]int) // track repo count per author for correct averaging

	// Track breadth (repos per author) with commit counts
	authorRepoCommits := make(map[string]map[string]int) // author -> repo -> commit count

	// Deduplicate repos by resolving to real paths
	seen := make(map[string]bool)
	var dedupedPaths []string
	for _, p := range repoPaths {
		real, err := filepath.EvalSymlinks(p)
		if err != nil {
			real = p
		}
		if !seen[real] {
			seen[real] = true
			dedupedPaths = append(dedupedPaths, p)
		} else {
			fmt.Fprintf(os.Stderr, "SKIP: %s (duplicate of already queued repo)\n", filepath.Base(p))
		}
	}
	repoPaths = dedupedPaths

	analyzedRepos := 0
	for _, repoPath := range repoPaths {
		// Verify it's a git repo
		if _, err := os.Stat(filepath.Join(repoPath, ".git")); os.IsNotExist(err) {
			fmt.Fprintf(os.Stderr, "SKIP: %s (not a git repo)\n", repoPath)
			continue
		}

		analyzedRepos++
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
		mergeMapAvg(raw.Quality, qual, qualityCounts)

		// Design
		design := metric.CalcDesign(commits, cfg.ArchitecturePatterns)
		mergeMap(raw.Design, design)

		// Track breadth with commit counts per repo
		for _, c := range commits {
			if _, ok := authorRepoCommits[c.Author]; !ok {
				authorRepoCommits[c.Author] = make(map[string]int)
			}
			authorRepoCommits[c.Author][repoName]++
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
		survResult := metric.CalcSurvival(blameLines, cfg.Tau, start)
		mergeMap(raw.Survival, survResult.Decayed)
		mergeMap(raw.RawSurvival, survResult.Raw)

		// Indispensability
		indisp, risks := metric.CalcIndispensability(blameLines, cfg.BusFactor.Critical, cfg.BusFactor.High)
		mergeMap(raw.Indispensability, indisp)

		// Step 3: Debt cleanup
		fmt.Fprintf(os.Stderr, "  [3/4] Debt analysis...\n")
		fixCommits := metric.GetFixCommits(commits)
		debt, _ := metric.CalcDebt(ctx, repoPath, fixCommits, 50, cfg.DebtThreshold, cfg.ResolveAuthor)
		mergeMap(raw.DebtCleanup, debt)

		// Step 4: Output per-repo bus factor
		if len(risks) > 0 {
			output.PrintBusFactorRisks(risks)
		}
	}

	// Breadth: count repos where author has >= 3 commits
	const minCommitsForBreadth = 3
	for author, repos := range authorRepoCommits {
		count := 0
		for _, commits := range repos {
			if commits >= minCommitsForBreadth {
				count++
			}
		}
		if count > 0 {
			raw.Breadth[author] = float64(count)
		}
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
	output.PrintSummary(filtered, analyzedRepos)
	output.PrintRankings(filtered)

	color.New(color.FgHiBlack).Printf("Completed in %s\n", elapsed.Round(time.Second))

	return nil
}

// findGitRepos walks a directory tree up to maxDepth and returns paths containing .git
func findGitRepos(root string, maxDepth int) ([]string, error) {
	var repos []string

	rootDepth := len(splitPath(root))

	err := filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return nil // skip errors
		}

		if !info.IsDir() {
			return nil
		}

		depth := len(splitPath(path)) - rootDepth
		if depth > maxDepth {
			return filepath.SkipDir
		}

		// Check if this directory is a git repo (not a submodule — submodules have .git as a file, not a dir)
		gitDir := filepath.Join(path, ".git")
		if fi, err := os.Stat(gitDir); err == nil {
			if fi.IsDir() {
				repos = append(repos, path)
			}
			// Whether .git is a dir or file (submodule), don't descend further
			return filepath.SkipDir
		}

		return nil
	})

	return repos, err
}

func splitPath(p string) []string {
	return strings.Split(filepath.ToSlash(p), "/")
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

// mergeMapAvg keeps a correct running average for quality scores across repos
func mergeMapAvg(dst, src map[string]float64, counts map[string]int) {
	for k, v := range src {
		n := counts[k]
		if n > 0 {
			// Cumulative average: (oldAvg * n + newValue) / (n + 1)
			dst[k] = (dst[k]*float64(n) + v) / float64(n+1)
		} else {
			dst[k] = v
		}
		counts[k] = n + 1
	}
}
