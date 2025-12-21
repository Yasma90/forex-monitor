"""
Tests for the scheduler service.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch

from app.jobs.scheduler import (
    ScheduledTask,
    TaskScheduler
)


class TestScheduledTask:
    """Tests for ScheduledTask class"""

    @pytest.fixture
    def mock_func(self):
        """Create mock async function"""
        return AsyncMock()

    def test_task_creation(self, mock_func):
        """Test task is created with correct attributes"""
        task = ScheduledTask("test_task", mock_func, 300, enabled=True)
        assert task.name == "test_task"
        assert task.interval_seconds == 300
        assert task.enabled is True
        assert task.run_count == 0
        assert task.error_count == 0

    @pytest.mark.asyncio
    async def test_task_run_success(self, mock_func):
        """Test successful task execution"""
        task = ScheduledTask("test_task", mock_func, 300)
        result = await task.run()

        assert result is True
        assert task.run_count == 1
        assert task.last_run is not None
        mock_func.assert_called_once()

    @pytest.mark.asyncio
    async def test_task_run_disabled(self, mock_func):
        """Test disabled task doesn't run"""
        task = ScheduledTask("test_task", mock_func, 300, enabled=False)
        result = await task.run()

        assert result is False
        assert task.run_count == 0
        mock_func.assert_not_called()

    @pytest.mark.asyncio
    async def test_task_run_error(self):
        """Test task handles errors gracefully"""
        async def failing_func():
            raise ValueError("Test error")

        task = ScheduledTask("test_task", failing_func, 300)
        result = await task.run()

        assert result is False
        assert task.error_count == 1
        assert task.last_error == "Test error"

    def test_task_status(self, mock_func):
        """Test task status property"""
        task = ScheduledTask("test_task", mock_func, 300)
        status = task.status

        assert status["name"] == "test_task"
        assert status["interval_seconds"] == 300
        assert status["enabled"] is True
        assert status["run_count"] == 0
        assert status["error_count"] == 0


class TestTaskScheduler:
    """Tests for TaskScheduler class"""

    @pytest.fixture
    def scheduler(self):
        """Create fresh scheduler instance"""
        return TaskScheduler()

    @pytest.fixture
    def mock_task_func(self):
        """Create mock async task function"""
        return AsyncMock()

    def test_add_task(self, scheduler, mock_task_func):
        """Test adding a task"""
        scheduler.add_task("test_task", mock_task_func, 300)
        assert "test_task" in scheduler.tasks
        assert scheduler.tasks["test_task"].name == "test_task"

    def test_remove_task(self, scheduler, mock_task_func):
        """Test removing a task"""
        scheduler.add_task("test_task", mock_task_func, 300)
        result = scheduler.remove_task("test_task")
        assert result is True
        assert "test_task" not in scheduler.tasks

    def test_remove_nonexistent_task(self, scheduler):
        """Test removing nonexistent task"""
        result = scheduler.remove_task("nonexistent")
        assert result is False

    def test_enable_task(self, scheduler, mock_task_func):
        """Test enabling a task"""
        scheduler.add_task("test_task", mock_task_func, 300, enabled=False)
        result = scheduler.enable_task("test_task")
        assert result is True
        assert scheduler.tasks["test_task"].enabled is True

    def test_disable_task(self, scheduler, mock_task_func):
        """Test disabling a task"""
        scheduler.add_task("test_task", mock_task_func, 300, enabled=True)
        result = scheduler.disable_task("test_task")
        assert result is True
        assert scheduler.tasks["test_task"].enabled is False

    def test_enable_nonexistent_task(self, scheduler):
        """Test enabling nonexistent task"""
        result = scheduler.enable_task("nonexistent")
        assert result is False

    def test_scheduler_status(self, scheduler, mock_task_func):
        """Test scheduler status property"""
        scheduler.add_task("task1", mock_task_func, 300)
        scheduler.add_task("task2", mock_task_func, 600)

        status = scheduler.status
        assert status["running"] is False
        assert status["task_count"] == 2
        assert "task1" in status["tasks"]
        assert "task2" in status["tasks"]

    @pytest.mark.asyncio
    async def test_start_stop(self, scheduler, mock_task_func):
        """Test starting and stopping scheduler"""
        scheduler.add_task("test_task", mock_task_func, 1)

        await scheduler.start()
        assert scheduler._running is True

        # Let it run briefly
        await asyncio.sleep(0.1)

        await scheduler.stop()
        assert scheduler._running is False
        assert len(scheduler._task_handles) == 0
