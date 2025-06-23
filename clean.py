import pandas as pd
import json
import os
from library import *

# AI Mappings:
if True:
    mapping = '''{
    "Category": {
        "Web Development": ["webdev", "web development"],
        "Programming": ["programming"],
        "Learning": ["learning"],
        "Nonprofits": ["nonprofits"],
        "Education": ["education"],
        "Teachers": ["teachers"],
        "Certification": ["certification"],
        "Curriculum": ["curriculum"],
        "Math": ["math"],
        "Community": ["community"],
        "Hacktoberfest": ["hacktoberfest"],
        "Information Security": ["infosec", "information security"],
        "Quality Assurance": ["QA", "quality assurance"],
        "Data Analysis": ["data analysis"],
        "Machine Learning": ["ML", "machine learning"],
        "College Algebra": ["college algebra"]
    },
    "Platforms": {
        "Web": ["web"],
        "Node.js": ["Node", "Nodejs"],
        "React": ["react"],
        "D3": ["d3"],
        "Docker": ["docker"],
        "Git": ["git"],
        "Augmented Reality": ["AR", "augmented reality"],
        "Blockchain": ["blockchain"],
        "Cryptocurrency": ["cryptocurrency"],
        "Virtual Machine": ["VM", "virtual machine"],
        "Emulator": ["emulator"],
        "Command Line": ["CLI", "command line"]
    },
    "Main Programming Language": {
        "TypeScript": ["Typescript"],
        "JavaScript": ["JS", "javascript"],
        "Python": ["python", "python3"],
        "Go": ["Golang", "go"],
        "Java": ["java"],
        "C++": ["Cpp", "cpp"],
        "C#": ["Csharp", "c#"],
        "Ruby": ["ruby"],
        "Rust": ["rust"],
        "Scala": ["scala"],
        "Kotlin": ["kotlin"],
        "Clojure": ["clojure"],
        "Crystal": ["crystal"],
        "Haskell": ["haskell"],
        "Lisp": ["lisp"],
        "Nim": ["nim"],
        "Zig": ["zig"],
        "R": ["r"],
        "Shell": ["shell", "Bash"]
    },
    "Programming Languages": {
        "JavaScript": ["JS", "javascript"],
        "HTML": ["html"],
        "CSS": ["css"],
        "TypeScript": ["Typescript"],
        "Python": ["python", "python3"],
        "Go": ["Golang", "go"],
        "Java": ["java"],
        "C++": ["Cpp", "cpp"],
        "C#": ["Csharp", "c#"],
        "Ruby": ["ruby"],
        "Rust": ["rust"],
        "Scala": ["scala"],
        "Kotlin": ["kotlin"],
        "Clojure": ["clojure"],
        "Crystal": ["crystal"],
        "Haskell": ["haskell"],
        "Lisp": ["lisp"],
        "Nim": ["nim"],
        "Zig": ["zig"],
        "R": ["r"],
        "Shell": ["shell", "Bash"],
        "SQL": ["sql"],
        "NoSQL": ["nosql"],
        "Redis": ["redis"]
    },
    "Languages Available": {
        "English": ["english"]
    },
    "Techniques": {
        "Responsive Design": ["responsive design"],
        "Testing": ["testing"],
        "Frontend": ["front-end", "frontend"],
        "Backend": ["back-end", "backend"],
        "Full Stack": ["fullstack", "full-stack"],
        "Physics Engine": ["physics engine"],
        "Game Development": ["game dev", "game development"],
        "Search Engine": ["search engine"],
        "Text Editor": ["text editor"],
        "Template Engine": ["template engine"],
        "Regex": ["regex", "regular expression"],
        "Algorithm": ["algo", "algorithm"],
        "Data Structure": ["data structure"],
        "Functional Programming": ["functional programming"],
        "Object-Oriented Programming": ["OOP", "object-oriented programming"],
        "Asynchronous Programming": ["async programming", "asynchronous programming"],
        "Data Visualization": ["data visualization"]
    }
    }
    '''

with open('deepseek_mappings.json', 'r') as file:
    ds_mappings: dict[dict[list[str]]] = json.load(file)

invert_mappings = {item: [cl, key] for cl in ds_mappings for (key, values) in ds_mappings[cl].items() for item in values}
print(json.dumps(invert_mappings, indent=4))

def init_mappings():
    unique_values = repo_data[['Programming Languages used', 'Techniques used', 'Category', 'Platforms', 'Languages Available']]
    unique_values = unique_values.map(parse_to_list).apply(lambda x: list(extract_unique(x)), axis=0)
    with open('Objects.json', 'w') as file:
        file.write(json.dumps(dict(unique_values), indent=4))

# init_mappings()
# repo_data['Libraries'] = pd.Series([pd.NA] * len(repo_data['Name']))

for index, row in repo_data.iterrows():

    # if index == 0: print(row)
    
    columns = {
        'Programming Languages used':    row['Programming Languages used'],
        'Main Programming Language':     row['Main Programming Language'],
        'Platforms':                     row['Platforms'],
        'Techniques used':               row['Techniques used'],
        'Category':                      row['Category']
    }

    parsed_columns = {
        key: col.split('//') if isinstance(col, str) else [] for key, col in zip(columns.keys(), columns.values())
    }

    new_values = {
        key: [] for key in columns
    }

    for key, col in parsed_columns.items():
        for item in col:
            try:
                new_item = invert_mappings[item]
                # print(f'{key}\n{col}\n{item}\n{new_item}')
                if key == 'Main Programming Language':
                    new_values[key].append(new_item[1])
                else:
                    if new_item[0] == 'Languages':
                        new_values['Programming Languages used'].append(new_item[1])
                    else:
                        new_values[new_item[0]].append(new_item[1])
            except:
                if new_item[0] == 'Languages':
                    new_values['Programming Languages used'].append(new_item[1])
                else:
                    new_values[key].append(item.capitalize())
    
    # print(new_values)

    if  new_values['Main Programming Language'] and \
        new_values['Main Programming Language'][0] not in new_values['Programming Languages used'] :

        new_values['Programming Languages used'].append(new_values['Main Programming Language'][0])
    
    # print(new_values)

    for key in new_values:
        new_values[key] = list(set(new_values[key]))
        if '' in new_values[key]:
            new_values[key].remove('')
        repo_data.at[index, key] = '//'.join(new_values[key])
    
    repo_data.at[index, 'Languages Available'] = \
        '//'.join([lang.capitalize() for lang in repo_data.at[index, 'Languages Available'].split('//') \
                    if lang.lower() != 'sql' and lang.lower() != 'fish'])

    if 'linux' in row['Platforms'].lower() or 'debian' in row['Platforms'].lower() or\
    'fedora' in row['Platforms'].lower()\
        and not('//Linux' in row['Platforms'] or 'Linux//' in row['Platforms']):

        repo_data.at[index, 'Platforms'] = 'Linux//' + repo_data.at[index, 'Platforms']
    
    if row['Platforms'] == 'Linux//':
        repo_data.at[index, 'Platforms'] = 'Linux'


    # if index == 0: print('-----'); print(row)    
repo_data.to_csv('repo_data_clean.csv', sep = ';', index=False)
