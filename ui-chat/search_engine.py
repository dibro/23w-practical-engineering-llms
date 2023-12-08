import numpy as np 
import json 
from sentence_transformers import SentenceTransformer
import os 

def search_mathematicians(search_query, k):

    db_embedding_path = os.path.join(os.getcwd(), 'data', 'mathematicians.npz')
    job_db = np.load(db_embedding_path, allow_pickle=True)
    job_db_np = job_db['arr_0']
    sentences = job_db['arr_1']

    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    qemb = model.encode(search_query)

    k = np.round(k).astype(int)
    diff = np.abs(np.subtract(qemb, job_db_np))
    diff = np.sum(diff, axis=1)
    best_mathematicians_idx = np.argpartition(diff, -k)[-k:]
    best_mathematicians_idx_sorted = best_mathematicians_idx[np.argsort(diff[best_mathematicians_idx])]

    diff = np.abs(np.subtract(qemb, job_db_np))
    diff = np.sum(diff, axis=1)
    best_mathematicians_idx = np.argpartition(diff, -k)[-k:]
    best_mathematicians_idx_sorted = best_mathematicians_idx[np.argsort(diff[best_mathematicians_idx])]

    results_as_string = ""
    for j, mat_idx in enumerate(best_mathematicians_idx_sorted):
        results_as_string += f"{j}: {sentences[mat_idx]}\n"
    return results_as_string

def search_job(search_query, k): # = input("What would you like to learn?\n")

    db_metadata_path = os.path.join(os.getcwd(), 'data', 'jobs.npz')
    metadata_db = np.load(db_metadata_path, allow_pickle=True)
    job_titles = metadata_db['arr_0']
    salaries = metadata_db['arr_1']
    job_description = metadata_db['arr_2']
    companies = metadata_db['arr_3']
    locations = metadata_db['arr_4']

    db_embedding_path = os.path.join(os.getcwd(), 'data', 'data_scientist_jobs_embeddings.npz')
    job_db = np.load(db_embedding_path, allow_pickle=True)
    job_db_np = job_db['arr_0']

    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    qemb = model.encode(search_query)

    #pdb.set_trace()
    k = np.round(k).astype(int)
    diff = np.abs(np.subtract(qemb, job_db_np))
    diff = np.sum(diff, axis=1)
    best_jobs_idx = np.argpartition(diff, -k)[-k:]
    best_jobs_idx_sorted = best_jobs_idx[np.argsort(diff[best_jobs_idx])]

    diff = np.abs(np.subtract(qemb, job_db_np))
    diff = np.sum(diff, axis=1)
    best_jobs_idx = np.argpartition(diff, -k)[-k:]
    best_jobs_idx_sorted = best_jobs_idx[np.argsort(diff[best_jobs_idx])]
    #ind = np.argpartition(diff, -k)[-k:]
    #topk = diff[ind]

    #best_jobs = ind[np.argsort(diff[ind])]

    results_as_string = ""
    for j, job_idx in enumerate(best_jobs_idx):
        company = companies[job_idx]
        if company.find("\n") > 0:
            company = company[:company.find("\n")]
        results_as_string += f"{j}: {job_titles[job_idx]} @ {company} (Location: {locations[job_idx]} // Est. Salary: {salaries[job_idx]})\n"
        results_as_string += f"Full description: {job_description[job_idx]}\n\n"
    
    md_table = "# Quick Overview of the results\n\n| **rank** | **Job Title** | **Company** | **Location** | **Salary** |\n|:----|:----|:----|:----|:----|\n"
    for j, job_idx in enumerate(best_jobs_idx):
        company = companies[job_idx]
        if company.find("\n") > 0:
            company = company[:company.find("\n")]
        
        md_table += f"| {j} | **{job_titles[job_idx]}** | {company} | {locations[job_idx]} | {salaries[job_idx]} |\n"
    return md_table, results_as_string
