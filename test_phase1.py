import config
import logging
from orma_core import GraphMemory

# Mock config for testing
config.STM_CAPACITY = 5

def test_phase1():
    print("Testing Config...")
    assert config.EMBEDDING_MODEL == "all-MiniLM-L6-v2"
    print("✅ Config loaded.")

    print("Testing Memory Vectorization...")
    mem = GraphMemory("test_memory.json")
    
    # Add some data
    mem.add_triplet("python", "is", "awesome")
    mem.add_triplet("java", "is", "verbose")
    
    # Test Retrieval
    node, score = mem.find_similar_node("pythonic")
    print(f"Query: 'pythonic' -> Found: {node} (Score: {score:.2f})")
    
    assert node == "python"
    assert score > 0.6
    print("✅ Vector search working.")
    
    print("Test Complete.")

if __name__ == "__main__":
    test_phase1()
