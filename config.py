# Orma Configuration

# Embedding Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Memory Configuration
STM_CAPACITY = 10         # Short-Term Memory turn capacity
SIMILARITY_THRESHOLD = 0.65  # Confidence threshold for memory retrieval

# System Configuration
DEFAULT_MEMORY_FILE = "orma_memory.json"
DEFAULT_SOUL_FILE = "orma_soul.json"

# Generation Configuration
GENERATION_TEMPERATURE = 0.9  # 0.0=Robotic, 1.0=Creative
