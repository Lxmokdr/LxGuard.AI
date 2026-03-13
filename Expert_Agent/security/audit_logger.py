"""
Audit Logger - Comprehensive Audit Logging
Responsibilities:
- Log all queries and decisions
- Track RBAC checks and security events
- Record performance metrics
- Maintain audit trail for compliance
- Support forensic analysis

This ensures FULL AUDITABILITY.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import uuid


@dataclass
class AuditLogEntry:
    """Audit log entry"""
    log_id: str
    timestamp: str
    event_type: str
    domain_id: Optional[str]
    tenant_id: Optional[str]
    user: Dict[str, Any]
    query: Dict[str, Any]
    decision: Dict[str, Any]
    trace_id: str
    security: Optional[Dict[str, Any]] = None
    performance: Optional[Dict[str, Any]] = None
    meta_info: Optional[Dict[str, Any]] = None


class AuditLogger:
    """
    Comprehensive audit logger.
    Logs all system decisions for compliance and forensics.
    """
    
    def __init__(self, log_dir: str = "audit_db", deterministic_mode: bool = False):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.deterministic_mode = deterministic_mode
        self.enhanced_logging = True   # toggled via PUT /admin/settings
        self.version = "1.0.0"
        print(f"📝 Audit Logger initialized (dir: {log_dir}, deterministic: {deterministic_mode})")

    
    def log_query(self,
                 query: str,
                 user: Any,
                 intent: str,
                 decision: Dict[str, Any],
                 trace_id: str,
                 domain_id: Optional[str] = None,
                 tenant_id: Optional[str] = None,
                 security_check: Optional[Dict[str, Any]] = None,
                 performance: Optional[Dict[str, Any]] = None) -> str:
        """
        Log a query and decision.
        
        Args:
            query: User query
            user: User object
            intent: Final intent
            decision: Decision made by system
            trace_id: Reference to full reasoning trace
            security_check: Security check results
            performance: Performance metrics
        
        Returns:
            log_id: Unique log entry ID
        """
        log_id = self._generate_log_id()
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        # Extract user info
        user_info = {
            "user_id": user.id if user else "anonymous",
            "username": user.username if user else "anonymous",
            "role": user.role.value if hasattr(user, 'role') and hasattr(user.role, 'value') else "guest",
            "session_id": getattr(user, 'session_id', 'unknown')
        }
        
        # Query info
        query_info = {
            "text": query,
            "language": "en",  # TODO: detect from NLP
            "intent": intent,
            "risk_level": security_check.get("risk_level", "unknown") if security_check else "unknown"
        }
        
        # Create log entry
        entry = AuditLogEntry(
            log_id=log_id,
            timestamp=timestamp,
            event_type="query",
            domain_id=domain_id,
            tenant_id=tenant_id,
            user=user_info,
            query=query_info,
            decision=decision,
            trace_id=trace_id,
            security=security_check,
            performance=performance,
            meta_info={
                "version": self.version,
                "environment": "production",
                "deterministic_mode": self.deterministic_mode
            }
        )
        
        # Write to file
        self._write_log(entry)
        
        return log_id
    
    def log_rejection(self,
                     query: str,
                     user: Any,
                     reason: str,
                     trace_id: str,
                     domain_id: Optional[str] = None,
                     tenant_id: Optional[str] = None) -> str:
        """Log a rejected query"""
        log_id = self._generate_log_id()
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        user_info = {
            "user_id": user.id if user else "anonymous",
            "username": user.username if user else "anonymous",
            "role": user.role.value if hasattr(user, 'role') and hasattr(user.role, 'value') else "guest"
        }
        
        entry = AuditLogEntry(
            log_id=log_id,
            timestamp=timestamp,
            event_type="rejection",
            domain_id=domain_id,
            tenant_id=tenant_id,
            user=user_info,
            query={"text": query},
            decision={"action": "rejected", "reason": reason},
            trace_id=trace_id,
            security={"allowed": False, "risk_level": "blocked", "reason": reason},
            performance={"total_time_ms": 0}
        )
        
        self._write_log(entry)
        return log_id
    
    def log_security_event(self,
                          event_type: str,
                          user: Any,
                          details: Dict[str, Any]) -> str:
        """Log a security event"""
        log_id = self._generate_log_id()
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        user_info = {
            "user_id": user.id if user else "anonymous",
            "username": user.username if user else "anonymous",
            "role": user.role.value if hasattr(user, 'role') and hasattr(user.role, 'value') else "guest"
        }
        
        entry = AuditLogEntry(
            log_id=log_id,
            timestamp=timestamp,
            event_type=event_type,
            user=user_info,
            query={"text": "N/A"},
            decision=details,
            trace_id="security_event",
            security=details,
            performance={"total_time_ms": 0}
        )
        
        self._write_log(entry)
        return log_id
    
    def _generate_log_id(self) -> str:
        """Generate unique log ID"""
        if self.deterministic_mode:
            # Use timestamp-based ID for determinism
            return hashlib.md5(datetime.utcnow().isoformat().encode()).hexdigest()
        else:
            # Use UUID for uniqueness
            return uuid.uuid4().hex
    
    def _write_log(self, entry: AuditLogEntry):
        """Write log entry to file"""
        # Organize by date
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"audit_{date_str}.jsonl"
        
        # Convert to dict and write as JSON line
        entry_dict = asdict(entry)
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry_dict) + "\n")
    
    def query_logs(self,
                  user_id: Optional[str] = None,
                  event_type: Optional[str] = None,
                  start_date: Optional[str] = None,
                  limit: int = 100) -> List[Dict[str, Any]]:
        """
        Query audit logs.
        
        Args:
            user_id: Filter by user ID
            event_type: Filter by event type
            start_date: Filter by start date (YYYY-MM-DD)
            limit: Maximum number of results
        
        Returns:
            List of matching log entries
        """
        results = []
        
        # Determine which files to search
        if start_date:
            log_file = self.log_dir / f"audit_{start_date}.jsonl"
            files_to_search = [log_file] if log_file.exists() else []
        else:
            files_to_search = sorted(self.log_dir.glob("audit_*.jsonl"), reverse=True)
        
        # Search files
        for log_file in files_to_search:
            if len(results) >= limit:
                break
            
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    # Reverse lines to get most recent first within the file
                    for line in reversed(lines):
                        if len(results) >= limit:
                            break
                        
                        entry = json.loads(line)
                        
                        # Apply filters
                        if user_id and entry.get("user", {}).get("user_id") != user_id:
                            continue
                        
                        if event_type and entry.get("event_type") != event_type:
                            continue
                        
                        results.append(entry)
            except Exception as e:
                print(f"Error reading {log_file}: {e}")
        
        return results
    
    def get_statistics(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Get audit log statistics"""
        if date:
            log_file = self.log_dir / f"audit_{date}.jsonl"
            files = [log_file] if log_file.exists() else []
        else:
            files = list(self.log_dir.glob("audit_*.jsonl"))
        
        stats = {
            "total_entries": 0,
            "by_event_type": {},
            "by_user_role": {},
            "rejections": 0,
            "security_events": 0,
            "avg_response_time_ms": 0.0,
            "error_rate_percent": 0.0,
            "cache_hits": 0,
            "cache_hit_rate_percent": 0.0
        }
        
        total_response_time = 0.0
        entries_with_perf = 0
        cache_hits = 0
        
        for log_file in files:
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        entry = json.loads(line)
                        stats["total_entries"] += 1
                        
                        event_type = entry.get("event_type", "unknown")
                        stats["by_event_type"][event_type] = stats["by_event_type"].get(event_type, 0) + 1
                        
                        user_role = entry.get("user", {}).get("role", "unknown")
                        stats["by_user_role"][user_role] = stats["by_user_role"].get(user_role, 0) + 1
                        
                        if event_type == "rejection":
                            stats["rejections"] += 1
                        
                        if "security" in entry and entry["security"]:
                            stats["security_events"] += 1
                            
                        # Performance metrics
                        perf = entry.get("performance")
                        if perf:
                            if "total_time_ms" in perf:
                                total_response_time += perf["total_time_ms"]
                                entries_with_perf += 1
                            if perf.get("cache_hit"):
                                cache_hits += 1
            except Exception as e:
                print(f"Error reading {log_file}: {e}")
        
        stats["cache_hits"] = cache_hits
        
        if entries_with_perf > 0:
            stats["avg_response_time_ms"] = round(total_response_time / entries_with_perf, 2)
            
        if stats["total_entries"] > 0:
            stats["error_rate_percent"] = round((stats["rejections"] / stats["total_entries"]) * 100, 2)
            stats["cache_hit_rate_percent"] = round((cache_hits / stats["total_entries"]) * 100, 2)
        
        return stats


# Example usage
if __name__ == "__main__":
    from api.auth import User, UserRole
    
    logger = AuditLogger(deterministic_mode=False)
    
    # Test logging
    admin = User(id="1", username="Alice", role=UserRole.ADMIN)
    
    log_id = logger.log_query(
        query="How do I deploy to production?",
        user=admin,
        intent="Deployment",
        decision={
            "action": "approved",
            "reason": "User has admin role",
            "final_intent": "Deployment",
            "documents_accessed": ["deployment.md"],
            "rules_applied": ["RULE_DEPLOYMENT"]
        },
        trace_id="trace_12345",
        security_check={
            "rbac_check": True,
            "pii_detected": False,
            "risk_level": "high"
        },
        performance={
            "total_time_ms": 1250,
            "nlp_time_ms": 150,
            "retrieval_time_ms": 300,
            "generation_time_ms": 700,
            "validation_time_ms": 100
        }
    )
    
    print(f"Logged query with ID: {log_id}")
    
    # Get statistics
    stats = logger.get_statistics()
    print(f"\nAudit Log Statistics:")
    print(json.dumps(stats, indent=2))
