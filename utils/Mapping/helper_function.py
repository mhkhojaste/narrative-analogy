from sentence_transformers import SentenceTransformer, util
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sentence_transformers import SentenceTransformer
import torch
import networkx as nx
from networkx.algorithms import bipartite

_model_emb = None  

def get_embedding_model():
    global _model_emb
    if _model_emb is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        _model_emb = SentenceTransformer('all-MiniLM-L6-v2', device=device)
        # _model_emb = SentenceTransformer('msmarco-distilbert-base-v4', device=device)
    return _model_emb

def similarity(sentence1, sentence2, model):
    emb1 = model.encode(sentence1, convert_to_tensor=True)
    emb2 = model.encode(sentence2, convert_to_tensor=True)
    return round(util.pytorch_cos_sim(emb1, emb2).item(), 3)
    
def cluster_sentences(sentences, model, distance_threshold=0.5):
    if len(sentences) <= 1:
        return {0: sentences} if sentences else {}

    embeddings = model.encode(sentences, convert_to_numpy=True)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

    clustering = AgglomerativeClustering(
        n_clusters=None,
        distance_threshold=distance_threshold,
        metric='cosine', 
        linkage='average'
    )
    labels = clustering.fit_predict(embeddings)

    clustered = {}
    for label, sentence in zip(labels, sentences):
        clustered.setdefault(label, []).append(sentence)
    
    clustered = dict(sorted(clustered.items()))
    clustered = {int(k): v for k, v in clustered.items()}
    return clustered
    
def is_none(val):
    if not val:
        return True
    if val == 'None' or val == 'none':
        return True
    return False
    
def get_edge_score(prop1, prop2, model):
    return similarity(prop1, prop2, model)
    
def get_ordered_edges_similarity(cluster1, cluster2, model):
    edges = [
        (s1, s2, similarity(s1, s2, model))
        for s1 in cluster1
        for s2 in cluster2
    ]
    return sorted(edges, key=lambda x: x[2], reverse=True)
    
    
def get_maximum_weighted_match(edge1, edge2, model):
    def to_cluster_format(edge):
        # if already clustered, keep it
        if isinstance(edge, dict):
            return edge
        # if flat list, wrap into a single cluster
        return {0: edge}

    cluster1 = to_cluster_format(edge1)
    cluster2 = to_cluster_format(edge2)

    keys1 = list(cluster1.keys())
    keys2 = list(cluster2.keys())

    B = nx.Graph()
    B.add_nodes_from(range(len(keys1)), bipartite=0)
    B.add_nodes_from(range(len(keys1), len(keys1) + len(keys2)), bipartite=1)

    for i, k1 in enumerate(keys1):
        for j, k2 in enumerate(keys2):
            props1 = cluster1[k1]
            props2 = cluster2[k2]

            max_sim = 0
            for p1 in props1:
                for p2 in props2:
                    sim = similarity(p1, p2, model)
                    max_sim = max(max_sim, sim)

            B.add_edge(i, len(keys1) + j, weight=1 - max_sim)

    matching = bipartite.matching.minimum_weight_full_matching(B, weight='weight')

    results = []
    seen = set()
    for i, j in matching.items():
        if i < len(keys1) and (i, j) not in seen and (j, i) not in seen:
            cid1 = keys1[i]
            cid2 = keys2[j - len(keys1)]
            sim = 1 - B[i][j]['weight']
            results.append((cid1, cid2, round(sim, 3)))
            seen.add((i, j))

    return results
