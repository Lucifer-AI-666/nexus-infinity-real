#!/usr/bin/env python3
"""
Test Suite per Nexus Infinity Real
Unit test e integration test
"""

import unittest
import os
import json
from memory import PersistentMemory
from approval_gate import ApprovalGate, ActionType
from monitoring import NexusMonitor, EventType

class TestPersistentMemory(unittest.TestCase):
    """Test della memoria persistente"""
    
    def setUp(self):
        self.memory = PersistentMemory("test_memory")
    
    def test_save_conversation(self):
        """Test salvataggio conversazione"""
        self.memory.save_conversation("user", "Ciao!")
        conversations = self.memory.get_conversations()
        self.assertEqual(len(conversations), 1)
        self.assertEqual(conversations[0]["role"], "user")
    
    def test_save_state(self):
        """Test salvataggio stato"""
        state = {"status": "online", "tasks": 5}
        self.memory.save_state(state)
        loaded_state = self.memory.load_state()
        self.assertEqual(loaded_state["status"], "online")
    
    def test_checkpoint(self):
        """Test checkpoint"""
        data = {"model": "llama-3.3-70b", "version": "1.0"}
        checkpoint_id = self.memory.create_checkpoint("Test Checkpoint", data)
        loaded = self.memory.load_checkpoint(checkpoint_id)
        self.assertEqual(loaded["model"], "llama-3.3-70b")
    
    def tearDown(self):
        self.memory.clear_memory()

class TestApprovalGate(unittest.TestCase):
    """Test del sistema di approvazioni"""
    
    def setUp(self):
        self.gate = ApprovalGate("test_approvals")
    
    def test_request_approval(self):
        """Test richiesta approvazione"""
        approval_id = self.gate.request_approval(
            ActionType.MODIFY_FILE,
            "Modifica test.py"
        )
        self.assertIsNotNone(approval_id)
    
    def test_approve(self):
        """Test approvazione"""
        approval_id = self.gate.request_approval(
            ActionType.EXECUTE_COMMAND,
            "Esegui comando"
        )
        self.gate.approve(approval_id)
        status = self.gate.get_approval_status(approval_id)
        self.assertEqual(status["status"], "approved")
    
    def test_reject(self):
        """Test rifiuto"""
        approval_id = self.gate.request_approval(
            ActionType.DELETE_FILE,
            "Elimina file"
        )
        self.gate.reject(approval_id, "Troppo rischioso")
        status = self.gate.get_approval_status(approval_id)
        self.assertEqual(status["status"], "rejected")

class TestMonitoring(unittest.TestCase):
    """Test del sistema di monitoring"""
    
    def setUp(self):
        self.monitor = NexusMonitor("test_logs")
    
    def test_log_event(self):
        """Test logging evento"""
        self.monitor.log_event(
            EventType.TASK_START,
            "Task test avviato"
        )
        events = self.monitor.get_events()
        self.assertGreater(len(events), 0)
    
    def test_log_api_call(self):
        """Test logging API call"""
        self.monitor.log_api_call("/api/chat", "POST", 200, 0.15)
        metrics = self.monitor.get_metrics()
        self.assertIn("api_call", metrics["events"])
    
    def test_metrics(self):
        """Test metriche"""
        self.monitor.log_event(EventType.DECISION, "Test decision")
        self.monitor.log_event(EventType.TASK_START, "Test task")
        metrics = self.monitor.get_metrics()
        self.assertGreater(len(metrics["events"]), 0)

class TestIntegration(unittest.TestCase):
    """Test di integrazione"""
    
    def setUp(self):
        self.memory = PersistentMemory("test_integration_memory")
        self.gate = ApprovalGate("test_integration_approvals")
        self.monitor = NexusMonitor("test_integration_logs")
    
    def test_full_workflow(self):
        """Test workflow completo"""
        # 1. Salva conversazione
        self.memory.save_conversation("user", "Modifica il file")
        
        # 2. Richiedi approvazione
        approval_id = self.gate.request_approval(
            ActionType.MODIFY_FILE,
            "Modifica main.py"
        )
        
        # 3. Log evento
        self.monitor.log_event(
            EventType.APPROVAL_REQUEST,
            "Richiesta di approvazione creata"
        )
        
        # 4. Approva
        self.gate.approve(approval_id)
        
        # 5. Log completamento
        self.monitor.log_event(
            EventType.APPROVAL_RESULT,
            "Approvazione concessa"
        )
        
        # Verifica
        conversations = self.memory.get_conversations()
        self.assertGreater(len(conversations), 0)
        
        status = self.gate.get_approval_status(approval_id)
        self.assertEqual(status["status"], "approved")
        
        events = self.monitor.get_events()
        self.assertGreater(len(events), 0)

def run_tests():
    """Esegui tutti i test"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestPersistentMemory))
    suite.addTests(loader.loadTestsFromTestCase(TestApprovalGate))
    suite.addTests(loader.loadTestsFromTestCase(TestMonitoring))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
