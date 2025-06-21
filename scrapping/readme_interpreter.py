import pandas as pd
from my_library import desc_df
from tenacity import retry, stop_after_attempt
import json
import requests
import time

system_prompt = """You are an expert GitHub repository analyst. Analyze the README and output STRICT JSON with:
{
    "purpose": "1-sentence description exlaining the purpose of the repository.",
    "programming_languages": ["comma", "separated", "list", "max_5_items", "capitalized"],
    "natural_languages": ["comma", "separated", "list", "max_5_items", "capitalized"],
    "technologies": ["comma", "separated", "list", "max_5_items", "capitalized"],
    "dependencies": ["comma", "separated", "list", "max_5_items", "capitalized"],
    "functionality": "2-3 sentence summary explaining what the repository does in practice.",
    "categories": "["Web|Cryptography|Finance|PureMaths|AI/MachineLearning|MediaReproduction|Office|Drawing/VisualArt|Music|DevOps|Data|Learning|ProgrammingLibrary|Tool|Other",
                    "comma", "separated", "list", "max_3_items", "capitalized"],
    "platforms": ["comma", "separated", "list", "capitalized"],
}
RULES:
1. Output ONLY valid JSON - no additional text, thinking or explanations
2. Technologies refers to general techniques used in the creation of the project.
3. Dependencies refers to other programs that must be installed to use the current repo.
4. Technologies: Only list explicit mentions, do not list languages used.
5. Repos that provide information but no actual programs, libraries or data to work with on projects or as apps classify as inside the Learning Category. (Repos that list APIs, learning resources, webpages, etc)
6. Categories: Choose the MOST relevant ones (minimum:1, maximum: 3).
"""

url = "http://localhost:1234/v1/chat/completions"
headers = {"Content-Type": "application/json"}

@retry(stop=stop_after_attempt(3))
def analyze_repo(repo_row: pd.DataFrame):
  try:
    user_prompt = f"REPO: {repo_row['name']}\nTOPICS{repo_row['topics']}\nDESC: {repo_row['description'][:10000]}\nREADME:\n{repo_row['readme'][:5000]}"
    payload = {
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 400,
        "stop": ["\n\n", "[/INST]"],
    }
    
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    return response.json()['choices'][0]['message']['content']
  
  except Exception as e:
        return json.dumps({"error": f"API failure: {str(e)}"})
  
  

def parse_json(json_str: str) -> json:
    try:
        clean_str = json_str
        if "```json" in json_str:
            clean_str = json_str.split("```json")[1].split("```")[0].strip()
        result = json.loads(clean_str)        
        return result
        
    except Exception as e:
        return {"error": f"JSON parse error: {str(e)}"}

def process_dataframe(df, batch_size=None):
    new_df = pd.read_csv('descriptions_processed.csv')
    for index, row in df.iterrows():
        try:
            print(f'Processing repo {row['name']}')
            if pd.notna(new_df.at[index,'purpose']) or pd.notna(new_df.at[index,'analysis_error']):
                print('This repo has been processed already.')
                continue
            raw_response = analyze_repo(row)
            # new_df.at[index, 'analysis_raw'] = raw_response
            parsed = parse_json(raw_response)
            if "error" in parsed:
                new_df.at[index, 'analysis_error'] = parsed["error"]
            else:
                new_df.at[index, 'purpose'] = parsed.get("purpose")
                new_df.at[index, 'technologies'] = "//".join(parsed.get("technologies", []))
                new_df.at[index, 'dependencies'] = "//".join(parsed.get("dependencies", []))
                new_df.at[index, 'programming_languages'] = "//".join(parsed.get("programming_languages", []))
                new_df.at[index, 'natural_languages'] = "//".join(parsed.get("natural_languages", []))
                new_df.at[index, 'categories'] = "//".join(parsed.get("categories", []))
                new_df.at[index, 'platforms'] = "//".join(parsed.get("platforms", []))
                new_df.at[index, 'functionality'] = parsed.get("functionality")
            print(json.dumps(parsed, indent=2))
            if (index+1)%10==0: print(f"Processed {index + 1}/{len(df)} repos")
            time.sleep(0.3)
        except Exception as e:
            new_df.at[index, 'analysis_error'] = f"Processing error: {str(e)}"
            print(f"Critical error on row {index}: {str(e)}")
        new_df.to_csv(f"descriptions_processed.csv", index=False)
    return df

if __name__ == '__main__':
  process_dataframe(desc_df)