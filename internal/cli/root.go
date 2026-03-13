package cli

import "fmt"

var version = "dev"

func Run(args []string) error {
	if len(args) == 0 {
		printUsage()
		return nil
	}

	switch args[0] {
	case "analyze":
		return runAnalyze(args[1:])
	case "team":
		return runTeam(args[1:])
	case "version":
		fmt.Printf("eis v%s\n", version)
		return nil
	case "help", "-h", "--help":
		printUsage()
		return nil
	default:
		printUsage()
		return fmt.Errorf("unknown command: %s", args[0])
	}
}

func printUsage() {
	fmt.Println(`eis - Engineering Impact Score

Usage:
  eis analyze [path...]       Analyze git repos and output individual rankings
  eis team [path...]          Analyze and aggregate into team-level metrics
  eis version                 Print version
  eis help                    Show this help

Examples:
  eis analyze .                                  Analyze current repo
  eis analyze --recursive /path/to/workspace     Auto-detect repos under directory
  eis analyze --format json --recursive ~/work   Output as JSON
  eis team --recursive /path/to/workspace        Team analysis (auto-group by domain)
  eis team --config eis.yaml --recursive ~/work  Team analysis with team config

Options (shared by analyze and team):
  --config <path>             Config file (default: eis.yaml in CWD)
  --recursive                 Recursively find git repos under given paths
  --depth <n>                 Max directory depth for recursive search (default: 2)
  --tau <days>                Survival decay parameter (default: 180)
  --sample <n>                Max files to blame per repo (default: 500)
  --workers <n>               Number of concurrent blame workers (default: 4)
  --format <fmt>              Output format: table, csv, json (default: table)
  --active-days <n>           Days to consider author active (default: 30)
  --pressure-mode <mode>      Change pressure mode: include or ignore (default: include)
  --domain <name>             Filter to single domain
  --verbose                   Show detailed debug output (file-level timing, slow ops)

Config file (eis.yaml):
  aliases:                    Map git author names to canonical names
  exclude_authors:            Authors to exclude from analysis
  exclude_file_patterns:      File patterns to exclude from production
  architecture_patterns:      Patterns for design score
  blame_extensions:           File extensions for blame analysis
  weights:                    Axis weights (must sum to 1.0)
  tau:                        Survival decay (default: 180 days)
  active_days:                Days to consider author active (default: 30)
  debt_threshold:             Min events for debt score (default: 10)
  teams:                      Team definitions (optional, see config.example.yaml)`)
}
