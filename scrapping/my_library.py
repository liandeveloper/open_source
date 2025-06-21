import os, datetime, time
from datetime import datetime as dt
import pandas as pd
from github import Github
import re, base64

# Initializing the csvs
if __name__== '__main__':
  import pandas as pd

  init_repos_df = pd.DataFrame(
      columns=[
        "id",
        "name",
        "full_name",
        "description",
        "readme",
        "url",
        "created_at",
        "updated_at",
        "pushed_at",
        "size",
        "downloads",
        "stars",
        "forks",
        "watchers",
        "issues",
        "open_issues",
        "pull_requests",
        "license",
        "topics",
        "language",
        "subscribers_count",
        "network_count",
        "has_wiki",
        "has_pages",
        "archived",
        "is_template",
        "parent",
        "source",
        "weekly_additions",
        "weekly_deletions",
        "contributors"])

  init_users_df = pd.DataFrame(
      columns=[
        "id",
        "login",
        "name",
        "email",
        "company",
        "location",
        "hireable",
        "bio",
        "public_repos",
        "followers",
        "following",
        "created_at",
        "updated_at",
        "type"])

  if 'repos.csv' not in os.listdir(): 
      init_repos_df.to_csv('repos.csv', index=False, compression='gzip')
      print('Created repos.csv')
  else: print('repos.csv has already been created')
  if 'users.csv' not in os.listdir(): 
    init_users_df.to_csv('users.csv', index=False, compression='gzip')
    print('Created users.csv')
  else: print('users.csv has already been created')

sort_criteria = [ 'watchers']
donde_criteria = ['stars', 'forks']

open_source_license = ['AGPL-3.0','GPL-3.0','CC-BY-4.0','MIT','Zlib','WTFPL','Unlicense',
                        'Vim','BSD-2-Clause','OFL-1.1','BSD-3-Clause','GPL-2.0'
                        'LGPL-3.0','ISC','CC0-1.0','Apache-2.0','CC-BY-SA-4.0','MPL-2.0']

# g = Github('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')
g = Github('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')

# For repo data
repos_df: pd.DataFrame = pd.read_csv(
    "repos.csv",
    compression='gzip',        # Specify compression type
    parse_dates=['created_at', 'updated_at', 'pushed_at'],  # Convert date columns
    dtype={                   # Optimize memory usage
        'stars': 'uint32',
        'forks': 'uint16',
        'license': 'category'
    }
)

# For user data
users_df: pd.DataFrame = pd.read_csv(
    "users.csv",
    compression='gzip',
    parse_dates=['created_at', 'updated_at'],
    dtype={
        'followers': 'uint32',
        'public_repos': 'uint16',
        'type': 'category'
    }
)

desc_df = repos_df[['id', 'name', 'topics', 'description', 'readme']].copy()
desc_df['readme'] = pd.Series(base64.b64decode(readme).decode("utf-8", errors='replace') for readme in desc_df['readme'])
desc_df['readme'] = pd.Series(re.sub(r'!\[.*?\]\(.*?\)', '', readme) for readme in desc_df['readme'])
desc_df['readme'] = pd.Series(re.sub(r'<.*?>', '', readme) for readme in desc_df['readme'])
desc_df['readme'] = pd.Series(re.sub(r'\#{2,}', '', readme) for readme in desc_df['readme'])

usage_df = pd.read_csv('descriptions_processed.csv')


if __name__ == '__main__':
    if 'description.csv' not in os.listdir(): 
        desc_df.to_csv('description.csv', index=False, compression='gzip')
        print('Created description.csv')
    else: print('description.csv has already been created')

def handle_rate_limit():
    rate_limit = g.get_rate_limit()
    if rate_limit.core.remaining < 10:
        reset_time = rate_limit.core.reset
        sleep_time = (reset_time - datetime.now(dt.timezone.utc)).total_seconds() + 10
        time.sleep(max(sleep_time, 0))

def get_repo_data(repo):
    try:    stats = repo.get_stats_code_frequency()
    except: stats = None
    return {
        "id": repo.id,
        "name": repo.name,
        "full_name": repo.full_name,
        "description": repo.description,
        "readme": repo.get_readme().content,
        "url": repo.html_url,
        "created_at": repo.created_at,
        "updated_at": repo.updated_at,
        "pushed_at": repo.pushed_at,
        "size": repo.size,
        "downloads": sum(asset.download_count for release in repo.get_releases() for asset in release.get_assets()),
        "stars": repo.stargazers_count,
        "forks": repo.forks_count,
        "watchers": repo.watchers_count,
        "issues": repo.get_issues().totalCount,
        "open_issues": repo.open_issues_count,
        "pull_requests":repo.get_pulls(state="all").totalCount,
        "license": repo.license.spdx_id if repo.license else None,
        "topics": repo.get_topics(),
        "language": repo.language,
        "subscribers_count": repo.subscribers_count,
        "network_count": repo.network_count,
        "has_wiki": repo.has_wiki,
        "has_pages": repo.has_pages,
        "archived": repo.archived,
        "is_template": repo.is_template,
        "parent": repo.parent.full_name if repo.parent else None,
        "source": repo.source.full_name if repo.source else None,
        "weekly_additions": sum(week.additions for week in stats) if stats else stats,
        "weekly_deletions": sum(week.deletions for week in stats) if stats else stats,
        "contributors": '//'.join([user.login for user in repo.get_contributors()])
    }

def get_user_data(user):
    return {
        "id": user.id,
        "login": user.login,
        "name": user.name,
        "email": user.email,
        "company": user.company,
        "location": user.location,
        "hireable": user.hireable,
        "bio": user.bio,
        "public_repos": user.public_repos,
        "followers": user.followers,
        "following": user.following,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "type": user.type,
    }

def fetch_repositories(criteria: str, query: str = None, verbose: bool = True, order: str = 'desc'):
    done_repos_ids: set = set(repos_df['id'])
    # Search by license with activity filtering

    # Split into multiple queries
    # license_chunks = [open_source_license[i:i+3] for i in range(0, len(open_source_license), 3)]

    # for chunk in license_chunks:
    #     chunk_query = " OR license:".join([l.lower() for l in chunk])
    #     chunk_query = f'(license:{chunk_query})'
    #     query = query + chunk_query
    #     print(query)
        
    # Process results

    repos = g.search_repositories(query=query, sort=criteria, order=order)
    
    with open('start.txt', 'r') as f:
        start = f.read()
    start = int(start)
    new_start = start

    for repo in repos[start:1000]:
        new_start += 1
        with open('start.txt', 'w') as f:
            f.write(str(new_start))
        try:
            handle_rate_limit()
            repo_tag = f'Repo: {repo.full_name} with id: {repo.id} and license: {repo.license}'
            if verbose: print(f'>> Analyzing {repo_tag}...')
            # Check if it was already scraped
            if repo.id in done_repos_ids:
                if verbose: print('  |__', repo_tag, ' has already been processed. :P')
                continue

            # El codigo original tenia una pila de condicionales aqui chequeando si el repositorio cumplia una serie de criterios pero los quite 
            # pq al estar chequeando los top 1000 repos me di cuenta que chequear si el repo cumplia con una serie de requisitos minimos muy generosos era una perdida de tiempo
            # Asi que el codigo actual esta cogiendo los 1000 primeros repos que cumplen cierto criterio
            
            # Store repo data
            repos_df.loc[len(repos_df)]= get_repo_data(repo)
            repos_df.to_csv('repos.csv', index=False, compression='gzip')   
            print('  |__' + repo_tag + 'has been added to the database!! :D')
            print(' -- Remaining API calls: ', g.get_rate_limit().core.remaining, ' -- ')
        except Exception as e:

            print(f"  |__Error: {str(e)}")
            time.sleep(3)

