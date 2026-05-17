package config

import (
	"fmt"
	"math"
	"os"

	"gopkg.in/yaml.v3"
)

type Config struct {
	Tau                  float64              `yaml:"tau"`
	SampleSize           int                  `yaml:"sample_size"`
	DebtThreshold        int                  `yaml:"debt_threshold"`
	ExcludeFilePatterns  []string             `yaml:"exclude_file_patterns"`
	ArchitecturePatterns []string             `yaml:"architecture_patterns"`
	BlameExtensions      []string             `yaml:"blame_extensions"`
	ExcludeAuthors       []string             `yaml:"exclude_authors"`
	Aliases              map[string]string    `yaml:"aliases"`
	Weights              Weights              `yaml:"weights"`
	BusFactor            BusFactor            `yaml:"bus_factor"`
	DefaultDomains       *bool                `yaml:"default_domains"`
	Domains              DomainsConfig        `yaml:"domains"`
	Teams                map[string]TeamEntry `yaml:"teams"`
	ProductionDailyRef   float64              `yaml:"production_daily_ref"`
	ExcludeRepos         []string             `yaml:"exclude_repos"`
	ActiveDays           int                  `yaml:"active_days"`
	BlameTimeout         int                  `yaml:"blame_timeout"`
	// ModuleConventionDirs is the set of monorepo-convention top-level
	// directories used by module resolution. When a file path's FIRST
	// component is one of these, the module is its first 2 components
	// (e.g. "services/ace"). When this list is set in config it REPLACES
	// the built-in default set (services, packages, apps, modules, libs);
	// when empty, the default set is used.
	ModuleConventionDirs []string `yaml:"module_convention_dirs"`
	// Breadth controls how the Breadth axis counts an author's reach.
	Breadth Breadth `yaml:"breadth"`
	// MaxBlameFileBytes is the upper bound (in bytes) for files passed to
	// git blame. Files whose blob size exceeds this are skipped before the
	// blame call, which protects against pathological huge single-line
	// dumps (e.g. SQL bulk inserts) that would otherwise stall git blame
	// for minutes per file. <= 0 disables the filter.
	MaxBlameFileBytes int64 `yaml:"max_blame_file_bytes"`
	// UntestedSurvivalWeight multiplies the survival contribution of blame lines
	// whose source file is not guarded by a test. 1.0 disables the weighting and
	// matches pre-v2 behaviour; 0.5 (default) treats untested code as half-value.
	UntestedSurvivalWeight float64 `yaml:"untested_survival_weight"`
}

// TeamEntry defines a named team with its members and optional domain scope.
type TeamEntry struct {
	Domain  string   `yaml:"domain"`
	Members []string `yaml:"members"`
}

// DomainsConfig maps domain names to their configuration.
// Supports both legacy format (list of repo patterns) and new format (object with repos + extensions).
//
//	legacy:  backend: [api, worker]
//	new:     mobile: { repos: [ios-app], extensions: [.swift, .kt] }
type DomainsConfig map[string]DomainEntry

// DomainEntry defines repo patterns and file extensions for a domain.
type DomainEntry struct {
	Repos      []string `yaml:"repos"`
	Extensions []string `yaml:"extensions"`
}

// UnmarshalYAML supports both legacy format (list of strings) and new format (object).
func (e *DomainEntry) UnmarshalYAML(value *yaml.Node) error {
	// Try list of strings first (legacy format: repo patterns only)
	var list []string
	if err := value.Decode(&list); err == nil {
		e.Repos = list
		return nil
	}
	// Object format
	type raw DomainEntry
	var r raw
	if err := value.Decode(&r); err != nil {
		return err
	}
	*e = DomainEntry(r)
	return nil
}

type Weights struct {
	Production       float64 `yaml:"production"`
	Quality          float64 `yaml:"quality"`
	Survival         float64 `yaml:"survival"`
	Design           float64 `yaml:"design"`
	Breadth          float64 `yaml:"breadth"`
	DebtCleanup      float64 `yaml:"debt_cleanup"`
	Indispensability float64 `yaml:"indispensability"`
}

type BusFactor struct {
	Critical float64 `yaml:"critical"`
	High     float64 `yaml:"high"`
}

// Breadth configures the unit and threshold of the Breadth axis.
//
// Unit decides what an author's reach is counted over:
//   - "auto"   — repo unit for multi-repo analysis, module unit for a
//     single-repo (monorepo) analysis. The unit is decided once per
//     analysis run, so every author in one run is counted the same way.
//   - "repo"   — always count distinct repos.
//   - "module" — always count distinct modules (convention-aware).
//
// MinCommits is the minimum commit count an author needs in a repo (or
// module) for that repo/module to count toward Breadth.
type Breadth struct {
	Unit       string `yaml:"unit"`
	MinCommits int    `yaml:"min_commits"`
}

func Default() *Config {
	return &Config{
		Tau:                    180,
		SampleSize:             500,
		DebtThreshold:          10,
		ActiveDays:             30,
		BlameTimeout:           120,
		MaxBlameFileBytes:      5 * 1024 * 1024,
		ProductionDailyRef:     1000,
		UntestedSurvivalWeight: 0.5,
		ExcludeFilePatterns: []string{
			"package-lock.json",
			"yarn.lock",
			"pnpm-lock.yaml",
			"go.sum",
			"docs/swagger*",
			"docs/doc.go",
			"docs/openapi*",
			"*generated*",
			"mock_*",
			"*.gen.*",
		},
		ArchitecturePatterns: []string{
			"*/repository/*interface*",
			"*/domainservice/",
			"*/router.go",
			"*/middleware/",
			"di/*.go",
			"*/core/",
			"*/stores/",
			"*/hooks/",
			"*/types/",
		},
		BlameExtensions: []string{
			"*.go", "*.ts", "*.tsx", "*.py", "*.rs", "*.java", "*.rb",
			"*.c", "*.h", "*.cpp", "*.hpp", "*.cc", "*.S",
			"*.scala", "*.hs", "*.ml", "*.mli",
		},
		ExcludeAuthors: []string{"github-actions[bot]", "renovate[bot]", "dependabot[bot]"},
		Aliases:        map[string]string{},
		Weights: Weights{
			Production:       0.15,
			Quality:          0.10,
			Survival:         0.25,
			Design:           0.20,
			Breadth:          0.10,
			DebtCleanup:      0.15,
			Indispensability: 0.05,
		},
		BusFactor: BusFactor{
			Critical: 0.80,
			High:     0.60,
		},
		Breadth: Breadth{
			Unit:       "auto",
			MinCommits: 3,
		},
	}
}

// Load reads a config file. If explicit is true (user passed --config),
// a missing file is an error. Otherwise, a missing file returns defaults.
func Load(path string, explicit bool) (*Config, error) {
	cfg := Default()

	data, err := os.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) && !explicit {
			return cfg, nil
		}
		return nil, err
	}

	if err := yaml.Unmarshal(data, cfg); err != nil {
		return nil, err
	}

	if err := cfg.Validate(); err != nil {
		return nil, err
	}

	return cfg, nil
}

func (c *Config) Validate() error {
	if c.Tau <= 0 {
		return fmt.Errorf("tau must be positive, got %f", c.Tau)
	}
	if c.SampleSize <= 0 {
		return fmt.Errorf("sample_size must be positive, got %d", c.SampleSize)
	}
	if c.DebtThreshold < 0 {
		return fmt.Errorf("debt_threshold must be non-negative, got %d", c.DebtThreshold)
	}
	if c.UntestedSurvivalWeight < 0 || c.UntestedSurvivalWeight > 1.0 {
		return fmt.Errorf("untested_survival_weight must be within [0.0, 1.0], got %f", c.UntestedSurvivalWeight)
	}

	w := c.Weights
	sum := w.Production + w.Quality + w.Survival + w.Design + w.Breadth + w.DebtCleanup + w.Indispensability
	if math.Abs(sum-1.0) > 0.01 {
		return fmt.Errorf("weights must sum to 1.0, got %f", sum)
	}

	if c.BusFactor.Critical <= c.BusFactor.High {
		return fmt.Errorf("bus_factor.critical (%f) must be greater than bus_factor.high (%f)", c.BusFactor.Critical, c.BusFactor.High)
	}

	switch c.Breadth.Unit {
	case "", "auto", "repo", "module":
		// ok ("" is treated as "auto" by the resolver)
	default:
		return fmt.Errorf("breadth.unit must be one of auto|repo|module, got %q", c.Breadth.Unit)
	}
	// MinCommits == 0 means "omitted" → BreadthMinCommits() falls back to 3.
	// A negative value is an explicit mistake.
	if c.Breadth.MinCommits < 0 {
		return fmt.Errorf("breadth.min_commits must be non-negative, got %d", c.Breadth.MinCommits)
	}

	return nil
}

// BreadthUnit returns the configured Breadth unit, normalizing the empty
// string (config omitted the key) to "auto".
func (c *Config) BreadthUnit() string {
	if c.Breadth.Unit == "" {
		return "auto"
	}
	return c.Breadth.Unit
}

// BreadthMinCommits returns the configured Breadth min-commits threshold,
// falling back to 3 when the config omitted the key (zero value).
func (c *Config) BreadthMinCommits() int {
	if c.Breadth.MinCommits < 1 {
		return 3
	}
	return c.Breadth.MinCommits
}

// UseDefaultDomains returns whether built-in domain extension mappings should be used.
// Defaults to true when default_domains is not set in config.
func (c *Config) UseDefaultDomains() bool {
	if c.DefaultDomains == nil {
		return true
	}
	return *c.DefaultDomains
}

// CustomExtensions returns a map of domain names to their custom extension lists.
// Used with domain.BuildExtMap to create the merged extension-to-domain map.
func (c *Config) CustomExtensions() map[string][]string {
	m := make(map[string][]string)
	for name, entry := range c.Domains {
		if len(entry.Extensions) > 0 {
			m[name] = entry.Extensions
		}
	}
	return m
}

func (c *Config) ResolveAuthor(name string) string {
	if canonical, ok := c.Aliases[name]; ok {
		return canonical
	}
	return name
}

func (c *Config) IsExcludedRepo(repoName string) bool {
	for _, excluded := range c.ExcludeRepos {
		if repoName == excluded {
			return true
		}
	}
	return false
}

func (c *Config) IsExcludedAuthor(name string) bool {
	resolved := c.ResolveAuthor(name)
	for _, excluded := range c.ExcludeAuthors {
		if resolved == excluded {
			return true
		}
	}
	return false
}
