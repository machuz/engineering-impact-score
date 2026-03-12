package team

import (
	"github.com/machuz/engineering-impact-score/internal/scorer"
)

// TeamResult holds aggregated team-level metrics.
// Metrics are computed from active members only (RecentlyActive=true).
// TotalMemberCount includes inactive members for reference.
type TeamResult struct {
	Name             string
	Domain           string
	MemberCount      int // active members
	TotalMemberCount int // all members (including inactive)
	RepoCount        int
	Members          []scorer.Result // active members only

	// Member axis averages (0-100)
	AvgProduction       float64
	AvgQuality          float64
	AvgSurvival         float64
	AvgRobustSurvival   float64
	AvgDormantSurvival  float64
	AvgDesign           float64
	AvgBreadth          float64
	AvgDebtCleanup      float64
	AvgIndispensability float64
	AvgTotal            float64

	// Role/Style/State distribution counts
	RoleDist  map[string]int
	StyleDist map[string]int
	StateDist map[string]int

	// Team health scores (0-100)
	Health TeamHealth

	// Team 5-axis classification (Structure/Culture/Phase/Risk + composite Character)
	Classification TeamClassification
}

// TeamHealth holds the health axis scores.
type TeamHealth struct {
	Complementarity     float64
	GrowthPotential     float64
	Sustainability      float64
	DebtBalance         float64
	ProductivityDensity float64
	QualityConsistency  float64
	RiskRatio           float64 // percentage of risk members (0-100)

	// Structure metrics
	AAR                  float64 // Architect-to-Anchor Ratio (raw ratio, not 0-100)
	AnchorDensity        float64 // Anchors / Active members (0-1)
	ArchitectureCoverage float64 // (Architects + Anchors) / Team size (0-1)
}

// Aggregate computes team-level metrics from individual results.
// Only active members (RecentlyActive=true) are used for health/averages.
// If memberFilter is nil, all results are considered (then filtered to active).
func Aggregate(name, domain string, repoCount int, results []scorer.Result, memberFilter []string) TeamResult {
	allMembers := filterMembers(results, memberFilter)
	if len(allMembers) == 0 {
		return TeamResult{Name: name, Domain: domain, RepoCount: repoCount}
	}

	// Filter to active members for team condition
	var activeMembers []scorer.Result
	for _, m := range allMembers {
		if m.RecentlyActive {
			activeMembers = append(activeMembers, m)
		}
	}
	if len(activeMembers) == 0 {
		return TeamResult{
			Name:             name,
			Domain:           domain,
			TotalMemberCount: len(allMembers),
			RepoCount:        repoCount,
		}
	}

	tr := TeamResult{
		Name:             name,
		Domain:           domain,
		MemberCount:      len(activeMembers),
		TotalMemberCount: len(allMembers),
		RepoCount:        repoCount,
		Members:          activeMembers,
		RoleDist:         make(map[string]int),
		StyleDist:        make(map[string]int),
		StateDist:        make(map[string]int),
	}

	var sumProd, sumQual, sumSurv, sumRobust, sumDormant float64
	var sumDesign, sumBreadth, sumDebt, sumIndisp, sumTotal float64

	for _, m := range activeMembers {
		sumProd += m.Production
		sumQual += m.Quality
		sumSurv += m.Survival
		sumRobust += m.RobustSurvival
		sumDormant += m.DormantSurvival
		sumDesign += m.Design
		sumBreadth += m.Breadth
		sumDebt += m.DebtCleanup
		sumIndisp += m.Indispensability
		sumTotal += m.Total

		tr.RoleDist[m.Role]++
		tr.StyleDist[m.Style]++
		tr.StateDist[m.State]++
	}

	n := float64(len(activeMembers))
	tr.AvgProduction = sumProd / n
	tr.AvgQuality = sumQual / n
	tr.AvgSurvival = sumSurv / n
	tr.AvgRobustSurvival = sumRobust / n
	tr.AvgDormantSurvival = sumDormant / n
	tr.AvgDesign = sumDesign / n
	tr.AvgBreadth = sumBreadth / n
	tr.AvgDebtCleanup = sumDebt / n
	tr.AvgIndispensability = sumIndisp / n
	tr.AvgTotal = sumTotal / n

	tr.Health = CalcHealth(tr)
	tr.Classification = Classify(tr)

	return tr
}

func filterMembers(results []scorer.Result, filter []string) []scorer.Result {
	if len(filter) == 0 {
		return results
	}
	allowed := make(map[string]bool, len(filter))
	for _, name := range filter {
		allowed[name] = true
	}
	var out []scorer.Result
	for _, r := range results {
		if allowed[r.Author] {
			out = append(out, r)
		}
	}
	return out
}
