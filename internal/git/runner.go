package git

import (
	"bufio"
	"context"
	"fmt"
	"io"
	"os/exec"
)

func RunLines(ctx context.Context, repoPath string, args ...string) ([]string, error) {
	cmd := exec.CommandContext(ctx, "git", args...)
	cmd.Dir = repoPath

	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return nil, fmt.Errorf("stdout pipe: %w", err)
	}

	if err := cmd.Start(); err != nil {
		return nil, fmt.Errorf("start git %v: %w", args, err)
	}

	var lines []string
	scanner := bufio.NewScanner(stdout)
	scanner.Buffer(make([]byte, 1024*1024), 1024*1024)
	for scanner.Scan() {
		lines = append(lines, scanner.Text())
	}

	if err := cmd.Wait(); err != nil {
		return lines, nil // partial results ok for blame
	}

	return lines, scanner.Err()
}

func RunStream(ctx context.Context, repoPath string, args ...string) (io.ReadCloser, *exec.Cmd, error) {
	cmd := exec.CommandContext(ctx, "git", args...)
	cmd.Dir = repoPath

	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return nil, nil, fmt.Errorf("stdout pipe: %w", err)
	}

	if err := cmd.Start(); err != nil {
		return nil, nil, fmt.Errorf("start git %v: %w", args, err)
	}

	return stdout, cmd, nil
}
