package cli

import "fmt"

const version = "0.1.0"

func Run(args []string) error {
	if len(args) == 0 {
		printUsage()
		return nil
	}

	switch args[0] {
	case "analyze":
		return runAnalyze(args[1:])
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
  eis analyze [path...]       Analyze git repos and output rankings
  eis version                 Print version
  eis help                    Show this help

Examples:
  eis analyze .                          Analyze current repo
  eis analyze /path/to/repo              Analyze a single repo
  eis analyze /path/to/repo1 /path/to/repo2  Analyze multiple repos

Options for analyze:
  --config <path>             Config file (default: eis.yaml in CWD)
  --tau <days>                Survival decay parameter (default: 180)
  --exclude <pattern>         File patterns to exclude (repeatable)
  --arch <pattern>            Architecture file patterns (repeatable)
  --json                      Output as JSON
  --sample <n>                Max files to blame per repo (default: 500)`)
}
