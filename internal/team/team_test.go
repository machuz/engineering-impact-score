package team

import (
	"testing"

	"github.com/machuz/engineering-impact-score/internal/scorer"
)

func TestAggregate_Basic(t *testing.T) {
	results := []scorer.Result{
		{Author: "alice", RecentlyActive: true, Production: 80, Quality: 90, Survival: 70, Design: 60, Breadth: 50, DebtCleanup: 55, Total: 65, Role: "Architect", Style: "Builder", State: "Active"},
		{Author: "bob", RecentlyActive: true, Production: 40, Quality: 85, Survival: 50, Design: 30, Breadth: 40, DebtCleanup: 60, Total: 45, Role: "Anchor", Style: "Balanced", State: "Growing"},
	}

	tr := Aggregate("backend-team", "Backend", 3, results, nil)

	if tr.MemberCount != 2 {
		t.Errorf("MemberCount = %d, want 2", tr.MemberCount)
	}
	if tr.AvgProduction != 60 {
		t.Errorf("AvgProduction = %f, want 60", tr.AvgProduction)
	}
	if tr.AvgQuality != 87.5 {
		t.Errorf("AvgQuality = %f, want 87.5", tr.AvgQuality)
	}
	if tr.RoleDist["Architect"] != 1 {
		t.Errorf("RoleDist[Architect] = %d, want 1", tr.RoleDist["Architect"])
	}
}

func TestAggregate_WithFilter(t *testing.T) {
	results := []scorer.Result{
		{Author: "alice", RecentlyActive: true, Production: 80, Quality: 90, Total: 65, Role: "Architect", Style: "Builder", State: "Active"},
		{Author: "bob", RecentlyActive: true, Production: 40, Quality: 85, Total: 45, Role: "Anchor", Style: "Balanced", State: "Growing"},
		{Author: "charlie", RecentlyActive: true, Production: 60, Quality: 70, Total: 55, Role: "Producer", Style: "Mass", State: "Active"},
	}

	tr := Aggregate("team", "Backend", 3, results, []string{"alice", "bob"})

	if tr.MemberCount != 2 {
		t.Errorf("MemberCount = %d, want 2", tr.MemberCount)
	}
	if tr.AvgProduction != 60 {
		t.Errorf("AvgProduction = %f, want 60", tr.AvgProduction)
	}
}

func TestAggregate_OnlyActiveMembers(t *testing.T) {
	results := []scorer.Result{
		{Author: "alice", RecentlyActive: true, Production: 80, Quality: 90, DebtCleanup: 70, Total: 65, Role: "Architect", Style: "Builder", State: "Active"},
		{Author: "bob", RecentlyActive: false, Production: 10, Quality: 50, DebtCleanup: 30, Total: 20, Role: "—", Style: "—", State: "Former"},
		{Author: "charlie", RecentlyActive: true, Production: 60, Quality: 80, DebtCleanup: 60, Total: 55, Role: "Producer", Style: "Mass", State: "Active"},
	}

	tr := Aggregate("team", "Backend", 3, results, nil)

	// Only active members counted
	if tr.MemberCount != 2 {
		t.Errorf("MemberCount = %d, want 2 (active only)", tr.MemberCount)
	}
	if tr.TotalMemberCount != 3 {
		t.Errorf("TotalMemberCount = %d, want 3", tr.TotalMemberCount)
	}
	// Averages should be from active members only
	if tr.AvgProduction != 70 {
		t.Errorf("AvgProduction = %f, want 70 (active only)", tr.AvgProduction)
	}
	// DebtCleanup should be 65, not dragged down by inactive bob's 30
	if tr.AvgDebtCleanup != 65 {
		t.Errorf("AvgDebtCleanup = %f, want 65 (active only)", tr.AvgDebtCleanup)
	}
}

func TestAggregate_AllInactive(t *testing.T) {
	results := []scorer.Result{
		{Author: "alice", RecentlyActive: false, Production: 80, Role: "Architect", Style: "Builder", State: "Former"},
	}

	tr := Aggregate("team", "Backend", 1, results, nil)

	if tr.MemberCount != 0 {
		t.Errorf("MemberCount = %d, want 0 (no active)", tr.MemberCount)
	}
	if tr.TotalMemberCount != 1 {
		t.Errorf("TotalMemberCount = %d, want 1", tr.TotalMemberCount)
	}
}

func TestAggregate_Empty(t *testing.T) {
	tr := Aggregate("empty", "Backend", 0, nil, nil)

	if tr.MemberCount != 0 {
		t.Errorf("MemberCount = %d, want 0", tr.MemberCount)
	}
}

func TestAggregate_AllFilteredOut(t *testing.T) {
	results := []scorer.Result{
		{Author: "alice", RecentlyActive: true, Production: 80, Role: "Architect", Style: "Builder", State: "Active"},
	}

	tr := Aggregate("team", "Backend", 1, results, []string{"nobody"})

	if tr.MemberCount != 0 {
		t.Errorf("MemberCount = %d, want 0", tr.MemberCount)
	}
}
