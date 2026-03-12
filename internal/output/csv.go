package output

import (
	"encoding/csv"
	"fmt"
	"os"

	"github.com/machuz/engineering-impact-score/internal/scorer"
)

func PrintRankingsCSV(domain string, results []scorer.Result, writeHeader bool) {
	w := csv.NewWriter(os.Stdout)

	if writeHeader {
		w.Write([]string{"domain", "rank", "member", "active", "commits", "production", "quality", "survival", "robust_survival", "dormant_survival", "design", "breadth", "debt_cleanup", "indispensability", "gravity", "total", "role", "role_conf", "style", "style_conf", "state", "state_conf"})
	}

	for i, r := range results {
		active := "false"
		if r.RecentlyActive {
			active = "true"
		}
		w.Write([]string{
			domain,
			fmt.Sprintf("%d", i+1),
			r.Author,
			active,
			fmt.Sprintf("%d", r.TotalCommits),
			fmt.Sprintf("%.1f", r.Production),
			fmt.Sprintf("%.1f", r.Quality),
			fmt.Sprintf("%.1f", r.Survival),
			fmt.Sprintf("%.1f", r.RobustSurvival),
			fmt.Sprintf("%.1f", r.DormantSurvival),
			fmt.Sprintf("%.1f", r.Design),
			fmt.Sprintf("%.1f", r.Breadth),
			fmt.Sprintf("%.1f", r.DebtCleanup),
			fmt.Sprintf("%.1f", r.Indispensability),
			fmt.Sprintf("%.1f", r.Gravity),
			fmt.Sprintf("%.1f", r.Total),
			r.Role,
			fmt.Sprintf("%.2f", r.RoleConf),
			r.Style,
			fmt.Sprintf("%.2f", r.StyleConf),
			r.State,
			fmt.Sprintf("%.2f", r.StateConf),
		})
	}

	w.Flush()
}
