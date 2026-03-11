package git

import (
	"context"
	"strconv"
	"strings"
	"time"
)

type Commit struct {
	Hash      string
	Author    string
	Date      time.Time
	Subject   string
	FileStats []FileStat
}

type FileStat struct {
	Insertions int
	Deletions  int
	Filename   string
}

func ParseLog(ctx context.Context, repoPath string) ([]Commit, error) {
	lines, err := RunLines(ctx, repoPath,
		"log", "--all", "--no-merges",
		"--format=COMMIT:%H|%an|%ai|%s",
		"--numstat",
	)
	if err != nil {
		return nil, err
	}

	var commits []Commit
	var current *Commit

	for _, line := range lines {
		if strings.HasPrefix(line, "COMMIT:") {
			if current != nil {
				commits = append(commits, *current)
			}
			parts := strings.SplitN(line[7:], "|", 4)
			if len(parts) < 4 {
				continue
			}
			date, _ := time.Parse("2006-01-02 15:04:05 -0700", parts[2])
			current = &Commit{
				Hash:    parts[0],
				Author:  parts[1],
				Date:    date,
				Subject: parts[3],
			}
			continue
		}

		if current == nil || strings.TrimSpace(line) == "" {
			continue
		}

		// numstat line: insertions\tdeletions\tfilename
		parts := strings.Split(line, "\t")
		if len(parts) != 3 {
			continue
		}

		ins, _ := strconv.Atoi(parts[0])
		del, _ := strconv.Atoi(parts[1])
		current.FileStats = append(current.FileStats, FileStat{
			Insertions: ins,
			Deletions:  del,
			Filename:   parts[2],
		})
	}

	if current != nil {
		commits = append(commits, *current)
	}

	return commits, nil
}
