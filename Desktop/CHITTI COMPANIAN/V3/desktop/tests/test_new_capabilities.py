"""
Tests for new capabilities: Health, Analytics, Meeting Intelligence
"""
import sys
import time
from datetime import datetime

sys.path.insert(0, '.')

def test_health_capability():
    """Test Health & Wellness capability."""
    print("\n=== Testing Health Capability ===")
    
    from desktop.capabilities.health import HealthCapability
    
    health = HealthCapability()
    health.initialize()
    
    # Test screen time
    result = health.get_screen_time()
    assert "date" in result
    assert "total_hours" in result
    print(f"  ✅ get_screen_time: {result['total_hours']} hours")
    
    # Test break reminders
    result = health.set_break_reminder("short", 5)
    assert "id" in result
    assert result["break_type"] == "short"
    print(f"  ✅ set_break_reminder: {result['id']}")
    
    # Test list reminders
    result = health.list_break_reminders()
    assert result["count"] >= 1
    print(f"  ✅ list_break_reminders: {result['count']} reminders")
    
    # Test focus mode
    result = health.enable_focus_mode("pomodoro", 25)
    assert "id" in result
    assert result["mode"] == "pomodoro"
    print(f"  ✅ enable_focus_mode: session {result['id']}")
    
    # Test focus status
    result = health.get_focus_status()
    assert result["active"] == True
    print(f"  ✅ get_focus_status: {result['mode']} active")
    
    # Test disable focus
    result = health.disable_focus_mode()
    assert result["was_interrupted"] == False
    print(f"  ✅ disable_focus_mode: completed")
    
    # Test health summary
    result = health.get_health_summary()
    assert "score" in result
    assert "recommendations" in result
    print(f"  ✅ get_health_summary: score {result['score']}")
    
    # Test Pomodoro settings
    result = health.set_pomodoro_settings(30, 10, 20, 3)
    assert result["work_minutes"] == 30
    print(f"  ✅ set_pomodoro_settings: {result['work_minutes']} min work")
    
    # Test eye rest
    result = health.enable_eye_rest(30)
    assert result["enabled"] == True
    print(f"  ✅ enable_eye_rest: enabled")
    
    # Test hydration reminder
    result = health.get_hydration_reminder()
    assert "recommended_glasses" in result
    print(f"  ✅ get_hydration_reminder: {result['recommended_glasses']} glasses")
    
    # Test posture reminder
    result = health.get_posture_reminder()
    assert "checks" in result
    print(f"  ✅ get_posture_reminder: posture check shown")
    
    # Test discover tools
    tools = health.discover_tools()
    assert len(tools) >= 14
    print(f"  ✅ discover_tools: {len(tools)} tools")
    
    health.shutdown()
    print("✅ Health Capability: ALL TESTS PASSED")
    return True


def test_analytics_capability():
    """Test Personal Analytics capability."""
    print("\n=== Testing Personal Analytics Capability ===")
    
    from desktop.capabilities.analytics_cap import PersonalAnalyticsCapability
    
    analytics = PersonalAnalyticsCapability()
    analytics.initialize()
    
    # Test start time tracking
    result = analytics.start_time_tracking("Coding", "development", "Working on feature X")
    assert result["status"] == "tracking"
    assert result["category"] == "development"
    print(f"  ✅ start_time_tracking: {result['task_name']}")
    
    # Test get current tracking
    result = analytics.get_current_tracking()
    assert result["tracking"] == True
    print(f"  ✅ get_current_tracking: active tracking")
    
    # Test stop time tracking
    time.sleep(0.1)  # Small delay
    result = analytics.stop_time_tracking()
    assert result["duration_minutes"] >= 0
    print(f"  ✅ stop_time_tracking: {result['duration_minutes']} min recorded")
    
    # Test time summary
    result = analytics.get_time_summary()
    assert "total_hours" in result
    assert "by_category" in result
    print(f"  ✅ get_time_summary: {result['total_hours']} hours")
    
    # Test weekly report
    result = analytics.get_weekly_report()
    assert "days" in result
    assert "total_focus_hours" in result
    print(f"  ✅ get_weekly_report: {result['total_focus_hours']} focus hours")
    
    # Test create habit
    result = analytics.create_habit("Exercise", "daily", 7)
    assert "id" in result
    assert result["name"] == "Exercise"
    print(f"  ✅ create_habit: {result['name']}")
    
    # Test track habit
    result = analytics.track_habit("Exercise")
    assert result["success"] == True
    assert result["streak"] >= 1
    print(f"  ✅ track_habit: streak {result['streak']}")
    
    # Test get habit streak
    result = analytics.get_habit_streak("Exercise")
    assert "current_streak" in result
    print(f"  ✅ get_habit_streak: {result['current_streak']} days")
    
    # Test get all habits
    result = analytics.get_all_habits()
    assert result["count"] >= 1
    print(f"  ✅ get_all_habits: {result['count']} habits")
    
    # Test productivity score
    result = analytics.get_productivity_score()
    assert "score" in result
    assert "level" in result
    print(f"  ✅ get_productivity_score: {result['score']} ({result['level']})")
    
    # Test peak hours
    result = analytics.get_peak_hours()
    assert "peak_hours" in result
    print(f"  ✅ get_peak_hours: analysis complete")
    
    # Test set goal
    result = analytics.set_goal("Weekly coding", 20, "hours", "2026-12-31")
    assert "target" in result
    assert result["target"] == 20
    print(f"  ✅ set_goal: {result['target']} hours")
    
    # Test goal progress
    result = analytics.get_goal_progress("Weekly coding")
    assert "Weekly coding" in result
    assert result["Weekly coding"]["target"] == 20
    print(f"  ✅ get_goal_progress: {result['Weekly coding']['progress_percentage']}%")
    
    # Test focus breakdown
    result = analytics.get_focus_breakdown()
    assert "focus_percentage" in result
    print(f"  ✅ get_focus_breakdown: {result['focus_percentage']}% focus")
    
    # Test daily summary
    result = analytics.get_daily_summary()
    assert "productivity_score" in result
    print(f"  ✅ get_daily_summary: score {result['productivity_score']}")
    
    analytics.shutdown()
    print("✅ Personal Analytics Capability: ALL TESTS PASSED")
    return True


def test_meeting_intelligence_capability():
    """Test Meeting Intelligence capability."""
    print("\n=== Testing Meeting Intelligence Capability ===")
    
    from desktop.capabilities.meeting_intelligence import MeetingIntelligenceCapability
    
    meeting = MeetingIntelligenceCapability()
    meeting.initialize()
    
    # Test start recording
    result = meeting.start_meeting_recording(
        "Team Standup",
        participants=[
            {"name": "Alice", "role": "organizer"},
            {"name": "Bob", "role": "attendee"}
        ],
        tags=["daily", "team"]
    )
    assert result["status"] == "recording"
    assert result["participant_count"] == 2
    print(f"  ✅ start_meeting_recording: {result['id']}")
    
    # Test add note
    result = meeting.add_meeting_note("Discussed the new feature", "Alice", "note")
    assert "id" in result
    print(f"  ✅ add_meeting_note: {result['content'][:30]}...")
    
    # Test add action item
    result = meeting.add_action_item("Review PR #123", "Bob", "2026-07-25", "high")
    assert result["assignee"] == "Bob"
    assert result["priority"] == "high"
    print(f"  ✅ add_action_item: {result['description']}")
    
    # Test add decision
    result = meeting.add_meeting_note("We will use microservices", "Alice", "decision")
    assert result["type"] == "decision"
    print(f"  ✅ add_meeting_note (decision): recorded")
    
    # Test extract action items
    result = meeting.extract_action_items("TODO: Fix bug, @Bob will deploy")
    assert "items" in result
    print(f"  ✅ extract_action_items: {result['count']} items found")
    
    # Test stop recording
    result = meeting.stop_meeting_recording()
    assert result["status"] == "processed"
    assert result["notes_count"] >= 2
    print(f"  ✅ stop_meeting_recording: {result['duration_minutes']} min, {result['action_items_count']} actions")
    
    # Get the meeting ID for further tests
    meeting_id = result["id"]
    
    # Test get meeting notes
    result = meeting.get_meeting_notes(meeting_id)
    assert len(result["notes"]) >= 2
    print(f"  ✅ get_meeting_notes: {len(result['notes'])} notes")
    
    # Test list action items
    result = meeting.list_action_items()
    assert result["count"] >= 1
    print(f"  ✅ list_action_items: {result['count']} pending")
    
    # Test complete action item
    pending = meeting.list_action_items()
    if pending["items"]:
        item_id = pending["items"][0]["id"]
        result = meeting.complete_action_item(item_id)
        assert result["completed"] == True
        print(f"  ✅ complete_action_item: {item_id}")
    
    # Test search meetings
    result = meeting.search_meetings("Standup")
    assert "results" in result
    print(f"  ✅ search_meetings: found {result['count']} results")
    
    # Test get meeting summary
    result = meeting.get_meeting_summary(meeting_id)
    assert "summary" in result
    assert "pending_actions" in result
    print(f"  ✅ get_meeting_summary: {result['pending_actions']} pending actions")
    
    # Test generate summary
    result = meeting.generate_summary(meeting_id)
    assert "summary" in result
    print(f"  ✅ generate_summary: summary regenerated")
    
    # Test pending actions
    result = meeting.get_pending_actions()
    assert "total_pending" in result
    print(f"  ✅ get_pending_actions: {result['total_pending']} total")
    
    # Test overdue actions
    result = meeting.get_overdue_actions()
    assert "count" in result
    print(f"  ✅ get_overdue_actions: {result['count']} overdue")
    
    # Test set note template
    result = meeting.set_note_template("standup", "## Daily Standup\n\n### Today\n- ")
    assert "available_templates" in result
    print(f"  ✅ set_note_template: templates updated")
    
    # Test health check
    result = meeting.health_check()
    assert "status" in result
    print(f"  ✅ health_check: {result['status']}")
    
    # Test discover tools
    tools = meeting.discover_tools()
    assert len(tools) >= 15
    print(f"  ✅ discover_tools: {len(tools)} tools")
    
    meeting.shutdown()
    print("✅ Meeting Intelligence Capability: ALL TESTS PASSED")
    return True


def run_all_tests():
    """Run all capability tests."""
    print("\n" + "="*60)
    print("🧪 NEW CAPABILITIES TEST SUITE")
    print("="*60)
    
    tests = [
        ("Health & Wellness", test_health_capability),
        ("Personal Analytics", test_analytics_capability),
        ("Meeting Intelligence", test_meeting_intelligence_capability),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, "PASS", passed))
        except Exception as e:
            print(f"  ❌ {name}: FAILED - {e}")
            results.append((name, "FAIL", str(e)))
    
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, status, _ in results if status == "PASS")
    failed = sum(1 for _, status, _ in results if status == "FAIL")
    
    for name, status, _ in results:
        emoji = "✅" if status == "PASS" else "❌"
        print(f"  {emoji} {name}: {status}")
    
    print(f"\n  Total: {len(results)} tests")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {failed} TEST(S) FAILED")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
