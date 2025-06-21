import pandas as pd
import json
import os

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

mapping = json.loads(mapping)
categories = mapping['Category']
platform = mapping['Platforms']
language = {**mapping['Main Programming Language'], **mapping['Programming Languages']}
techniques = mapping['Techniques']

mapping_r = {}
for column, terms in mapping.items():
    mapping_r[column] = {}
    for canonical, variants in terms.items():
        for variant in variants:
            mapping_r[column][variant.lower()] = canonical

def pile(instance):
    try:
      instance = instance.split('//')
    except:
        return instance
    return '//'.join([mapping_r[item] if item in mapping_r else item for item in instance ])

data = pd.read_csv('repo_data.csv', sep=';')
data[['categories', 'platforms', 
      'main_prog_language', 
      'programming_languages', 'technologies']].map(lambda x: pile(x))

data.to_csv('repo_data2.csv', sep = ';', index=False)