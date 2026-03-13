"""
File Watcher - Real-time monitoring of docs folder
Automatically reloads knowledge base when files are added/modified/deleted.

This makes the system TRULY REACTIVE in real-time.
"""

import os
import time
import threading
from typing import Callable, Optional
from pathlib import Path
from datetime import datetime


class FileWatcher:
    """
    Watches the docs folder for changes and triggers reload callbacks.
    Runs in a background thread.
    """
    
    def __init__(self, watch_path: str, callback: Callable, interval: float = 2.0):
        """
        Args:
            watch_path: Path to watch for changes
            callback: Function to call when changes detected
            interval: Check interval in seconds
        """
        self.watch_path = watch_path
        self.callback = callback
        self.interval = interval
        
        # Track file states
        self.file_states = {}
        self._scan_files()
        
        # Threading
        self.running = False
        self.thread = None
        
        print(f"👁️  File Watcher initialized (watching: {watch_path})")
    
    def _scan_files(self):
        """Scan all files and record their states"""
        new_states = {}
        
        if not os.path.exists(self.watch_path):
            return
        
        for root, dirs, files in os.walk(self.watch_path):
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    try:
                        stat = os.stat(filepath)
                        new_states[filepath] = {
                            'mtime': stat.st_mtime,
                            'size': stat.st_size
                        }
                    except:
                        pass
        
        self.file_states = new_states
    
    def _check_changes(self) -> dict:
        """Check for file changes"""
        changes = {
            'added': [],
            'modified': [],
            'deleted': []
        }
        
        # Scan current state
        current_states = {}
        for root, dirs, files in os.walk(self.watch_path):
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    try:
                        stat = os.stat(filepath)
                        current_states[filepath] = {
                            'mtime': stat.st_mtime,
                            'size': stat.st_size
                        }
                    except:
                        pass
        
        # Detect changes
        current_files = set(current_states.keys())
        previous_files = set(self.file_states.keys())
        
        # Added files
        changes['added'] = list(current_files - previous_files)
        
        # Deleted files
        changes['deleted'] = list(previous_files - current_files)
        
        # Modified files
        for filepath in current_files & previous_files:
            if current_states[filepath]['mtime'] != self.file_states[filepath]['mtime']:
                changes['modified'].append(filepath)
        
        # Update state
        self.file_states = current_states
        
        return changes
    
    def _watch_loop(self):
        """Main watch loop (runs in background thread)"""
        print(f"👁️  File Watcher started (interval: {self.interval}s)")
        
        while self.running:
            try:
                changes = self._check_changes()
                
                # If any changes detected, trigger callback
                if any(changes.values()):
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"\n🔄 [{timestamp}] File changes detected:")
                    
                    if changes['added']:
                        for f in changes['added']:
                            print(f"   ➕ Added: {os.path.basename(f)}")
                    
                    if changes['modified']:
                        for f in changes['modified']:
                            print(f"   ✏️  Modified: {os.path.basename(f)}")
                    
                    if changes['deleted']:
                        for f in changes['deleted']:
                            print(f"   ➖ Deleted: {os.path.basename(f)}")
                    
                    # Trigger callback
                    try:
                        self.callback(changes)
                    except Exception as e:
                        print(f"   ⚠️  Callback error: {e}")
                
                time.sleep(self.interval)
            
            except Exception as e:
                print(f"⚠️  Watcher error: {e}")
                time.sleep(self.interval)
        
        print("👁️  File Watcher stopped")
    
    def start(self):
        """Start watching in background thread"""
        if self.running:
            print("⚠️  Watcher already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.thread.start()
    
    def stop(self):
        """Stop watching"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def is_running(self) -> bool:
        """Check if watcher is running"""
        return self.running


class ReactiveKnowledgeBase:
    """
    Knowledge Base with automatic file watching.
    Reloads whenever files change.
    """
    
    def __init__(self, knowledge_base, watch_interval: float = 2.0):
        self.kb = knowledge_base
        self.watcher = None
        
        # Setup watcher if auto-discovery is enabled
        if hasattr(self.kb, 'auto_discovery') and self.kb.auto_discovery:
            watch_path = self.kb.auto_discovery.base_path
            self.watcher = FileWatcher(
                watch_path=watch_path,
                callback=self._on_file_change,
                interval=watch_interval
            )
    
    def _on_file_change(self, changes: dict):
        """Callback when files change"""
        print("   🔄 Reloading knowledge base...")
        self.kb.reload_if_changed()
        print(f"   ✅ Reload complete: {len(self.kb.documents)} documents")
    
    def start_watching(self):
        """Start watching for file changes"""
        if self.watcher:
            self.watcher.start()
            print("✅ Reactive mode enabled - will auto-reload on file changes")
        else:
            print("⚠️  Auto-discovery not enabled, cannot watch files")
    
    def stop_watching(self):
        """Stop watching"""
        if self.watcher:
            self.watcher.stop()
    
    def __getattr__(self, name):
        """Delegate all other methods to knowledge base"""
        return getattr(self.kb, name)


# Example usage
if __name__ == "__main__":
    from data.knowledge_base import KnowledgeBase
    
    # Create knowledge base with auto-discovery
    kb = KnowledgeBase(enable_auto_discovery=True)
    
    # Wrap with reactive watcher
    reactive_kb = ReactiveKnowledgeBase(kb, watch_interval=2.0)
    
    # Start watching
    reactive_kb.start_watching()
    
    print(f"\n{'='*60}")
    print("REACTIVE KNOWLEDGE BASE RUNNING")
    print(f"{'='*60}")
    print("\nTry adding/modifying/deleting .md files in the docs folder!")
    print("The system will automatically detect and reload them.")
    print("\nPress Ctrl+C to stop...\n")
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping...")
        reactive_kb.stop_watching()
        print("✅ Stopped")
