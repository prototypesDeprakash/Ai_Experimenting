from sentence_transformers import SentenceTransformer
import numpy as np

print("Loading model... (first time downloads ~80MB, then it's cached)")
model = SentenceTransformer("all-MiniLM-L6-v2")
print("Model loaded.\n")

sentences = [
    "User's name is Prakash",
    "User is called Prakash",
    "User is building a desktop AI avatar in Unity",
]

query = "what's my name?"

# Convert all sentences + the query into vectors
sentence_vecs = model.encode(sentences)
query_vec = model.encode(query)

print(f"Each sentence became a vector of length: {len(sentence_vecs[0])}")
print(f"First 5 numbers of vector for '{sentences[0]}':")
print(sentence_vecs[0][:5])
print()

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print(f"Query: '{query}'\n")
for sent, vec in zip(sentences, sentence_vecs):
    sim = cosine_similarity(query_vec, vec)
    print(f"  similarity={sim:.4f}  ->  '{sent}'")