import logging
import time
import asyncio
from typing import Any, List, Optional, Dict
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timezone

from desktop.models.lifecycle import IRuntime, HealthState
from desktop.runtimes.capability.results import ExecutionResult, ExecutionStatus

logger = logging.getLogger(__name__)

class VerificationStatus(str, Enum):
    VERIFIED_SUCCESS = "VERIFIED_SUCCESS"
    VERIFIED_FAILURE = "VERIFIED_FAILURE"
    VERIFICATION_NOT_SUPPORTED = "VERIFICATION_NOT_SUPPORTED"

class VerificationStrategyType(str, Enum):
    PROCESS = "PROCESS"
    WINDOW = "WINDOW"
    GENERIC = "GENERIC"

class FailureCauseType(str, Enum):
    PROCESS_NOT_FOUND = "PROCESS_NOT_FOUND"
    PROCESS_STILL_RUNNING = "PROCESS_STILL_RUNNING"
    OCR_MISMATCH = "OCR_MISMATCH"
    TIMEOUT = "TIMEOUT"
    UNKNOWN = "UNKNOWN"

@dataclass
class FailureCause:
    cause_type: FailureCauseType
    description: str
    version: str = "1.0"
    stack_trace: Optional[str] = None
    visual_evidence_id: Optional[str] = None

from desktop.models.memory import EpisodeQuality


@dataclass
class VerificationContext:
    execution_result: ExecutionResult
    runtime_context: Any = None

@dataclass
class VerificationResult:
    status: VerificationStatus
    evidence: List[str]
    strategy_used: Optional[VerificationStrategyType]
    timestamp: float = field(default_factory=time.time)
    duration_ms: float = 0.0
    failure_cause: Optional[FailureCause] = None
    trace_id: Optional[str] = None
    version: str = "1.0"

class IVerificationStrategy:
    async def verify(self, context: VerificationContext) -> VerificationResult:
        raise NotImplementedError()

class ProcessVerificationStrategy(IVerificationStrategy):
    async def verify(self, context: VerificationContext) -> VerificationResult:
        start_time = time.time()
        vdata = context.execution_result.verification_data
        pid = vdata.get("pid")
        target_exe = vdata.get("target_exe")
        expected_state = vdata.get("expected_state", "running")
        
        evidence = []
        
        try:
            import psutil
        except ImportError:
            evidence.append("psutil not available")
            return VerificationResult(status=VerificationStatus.VERIFICATION_NOT_SUPPORTED, evidence=evidence, strategy_used=VerificationStrategyType.PROCESS)

        if expected_state == "running":
            if pid is None:
                evidence.append("No PID provided for running state verification")
                failure = FailureCause(cause_type=FailureCauseType.PROCESS_NOT_FOUND, description="No PID provided for running state verification")
                return VerificationResult(status=VerificationStatus.VERIFIED_FAILURE, evidence=evidence, strategy_used=VerificationStrategyType.PROCESS, duration_ms=(time.time()-start_time)*1000, failure_cause=failure)
            
            max_retries = 10
            for attempt in range(max_retries):
                if psutil.pid_exists(pid):
                    try:
                        p = psutil.Process(pid)
                        if p.is_running():
                            evidence.append(f"Process {pid} verified running (attempt {attempt+1})")
                            return VerificationResult(status=VerificationStatus.VERIFIED_SUCCESS, evidence=evidence, strategy_used=VerificationStrategyType.PROCESS, duration_ms=(time.time()-start_time)*1000)
                    except psutil.NoSuchProcess:
                        pass
                
                await asyncio.sleep(0.1)
                
            evidence.append(f"Process {pid} not found after {max_retries} attempts")
            failure = FailureCause(cause_type=FailureCauseType.PROCESS_NOT_FOUND, description=f"Process {pid} not found")
            return VerificationResult(status=VerificationStatus.VERIFIED_FAILURE, evidence=evidence, strategy_used=VerificationStrategyType.PROCESS, duration_ms=(time.time()-start_time)*1000, failure_cause=failure)

        elif expected_state == "terminated":
            if not target_exe:
                evidence.append("No target_exe provided for termination verification")
                failure = FailureCause(cause_type=FailureCauseType.PROCESS_NOT_FOUND, description="No target_exe provided for termination verification")
                return VerificationResult(status=VerificationStatus.VERIFIED_FAILURE, evidence=evidence, strategy_used=VerificationStrategyType.PROCESS, duration_ms=(time.time()-start_time)*1000, failure_cause=failure)
                
            max_retries = 20
            target_lower = target_exe.lower()
            for attempt in range(max_retries):
                found = False
                for p in psutil.process_iter(['name']):
                    try:
                        name = p.info['name']
                        if name and name.lower() == target_lower:
                            found = True
                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                        
                if not found:
                    evidence.append(f"Process {target_exe} verified terminated (attempt {attempt+1})")
                    return VerificationResult(status=VerificationStatus.VERIFIED_SUCCESS, evidence=evidence, strategy_used=VerificationStrategyType.PROCESS, duration_ms=(time.time()-start_time)*1000)
                    
                await asyncio.sleep(0.1)
                
            evidence.append(f"Process {target_exe} still running after {max_retries} attempts")
            failure = FailureCause(cause_type=FailureCauseType.PROCESS_STILL_RUNNING, description=f"Process {target_exe} still running")
            return VerificationResult(status=VerificationStatus.VERIFIED_FAILURE, evidence=evidence, strategy_used=VerificationStrategyType.PROCESS, duration_ms=(time.time()-start_time)*1000, failure_cause=failure)

        evidence.append(f"Unknown expected_state: {expected_state}")
        return VerificationResult(status=VerificationStatus.VERIFICATION_NOT_SUPPORTED, evidence=evidence, strategy_used=VerificationStrategyType.PROCESS, duration_ms=(time.time()-start_time)*1000)

class GenericVerificationStrategy(IVerificationStrategy):
    async def verify(self, context: VerificationContext) -> VerificationResult:
        start_time = time.time()
        return VerificationResult(status=VerificationStatus.VERIFICATION_NOT_SUPPORTED, evidence=["Generic capability needs no OS verification"], strategy_used=VerificationStrategyType.GENERIC, duration_ms=(time.time()-start_time)*1000)

class VerificationRuntime(IRuntime):
    def __init__(self):
        self.context = None
        self.strategies = {
            VerificationStrategyType.PROCESS: ProcessVerificationStrategy(),
            VerificationStrategyType.GENERIC: GenericVerificationStrategy()
        }

    @property
    def dependencies(self):
        return []

    async def initialize(self, context) -> bool:
        self.context = context
        return True

    async def start(self) -> bool:
        logger.info("[VerificationRuntime] Started.")
        return True

    async def stop(self) -> bool:
        logger.info("[VerificationRuntime] Stopped.")
        return True

    def health(self) -> HealthState:
        return HealthState.HEALTHY

    async def shutdown(self) -> bool:
        await self.stop()
        return True
    
    async def verify(self, result: ExecutionResult) -> VerificationResult:
        logger.info("[VerificationRuntime] Verifying execution result evidence.")
        start_time = time.time()
        
        if result.status != ExecutionStatus.SUCCESS:
            failure = FailureCause(cause_type=FailureCauseType.UNKNOWN, description="Execution failed before verification")
            return VerificationResult(status=VerificationStatus.VERIFIED_FAILURE, evidence=["Execution failed before verification"], strategy_used=None, duration_ms=(time.time()-start_time)*1000, failure_cause=failure)

        vdata = result.verification_data
        strategy_str = vdata.get("strategy")
        
        try:
            strategy_type = VerificationStrategyType(strategy_str) if strategy_str else VerificationStrategyType.GENERIC
        except ValueError:
            logger.warning(f"Unknown verification strategy requested: {strategy_str}")
            return VerificationResult(status=VerificationStatus.VERIFICATION_NOT_SUPPORTED, evidence=[f"Unknown strategy {strategy_str}"], strategy_used=None, duration_ms=(time.time()-start_time)*1000)
            
        strategy = self.strategies.get(strategy_type)
        if not strategy:
            return VerificationResult(status=VerificationStatus.VERIFICATION_NOT_SUPPORTED, evidence=[f"Strategy {strategy_type.value} not implemented"], strategy_used=strategy_type, duration_ms=(time.time()-start_time)*1000)
            
        ctx = VerificationContext(execution_result=result, runtime_context=self.context)
        return await strategy.verify(ctx)
