# # Obviamente da error porque le faltan una pila de librerias

# verbose = False

# MIN_STARS = 10
# MIN_FORKS = 5
# MIN_CONTRIBUTORS = 2
# MAX_LAST_UPDATED_DAYS = 365*2  # 2 years
# MIN_COMMITS = 10
# MIN_SIZE_KB = 100  # 100KB codebase

# for criteria in query_criteria:
#     print(f'Checking repos with the most amount of {criteria}')
#     for license in open_source_license:
#         print(f'Checking repos with license {license}')
#         try:
#             # Search by license with activity filtering
#             query = f"license:{license} stars:>={MIN_STARS} forks:>={MIN_FORKS}"
#             repos = g.search_repositories(query=query, sort=criteria, order="desc")
            
#             for repo in repos[:1000]:
#                 handle_rate_limit()
#                 repo_tag = f'Repo: {repo.full_name} with id: {repo.id}'

#                 # Check if it was already scraped
#                 if repo.id in done_repos_ids:
#                     if verbose: print(repo_tag + ' has already been processed. :P')
#                     continue

#                 # Apply additional filters
#                 if (repo.size < MIN_SIZE_KB or
#                     (datetime.now(dt.timezone.utc) - repo.pushed_at).days > MAX_LAST_UPDATED_DAYS or
#                     repo.get_commits().totalCount < MIN_COMMITS):
#                     if verbose: print(repo_tag + "doesn't match the criteria for scraping. :'(")
#                     continue
                    
#                 # Get contributors
#                 contributors = repo.get_contributors()
#                 if contributors.totalCount < MIN_CONTRIBUTORS:
#                     if verbose: print(repo_tag + "doesn't match the criteria for scraping. Not enough contributors. :'(")
#                     continue
                    
#                 # Store repo data
#                 repos_df.loc[len(repos_df)] = get_repo_data(repo)
#                 print('<< ' + repo_tag + 'has been added to the database!! :D >>')
                
#                 # Collect user data
#                 for contributor in contributors:
#                     if contributor.id not in done_users_ids:
#                         users_df.loc[len(users_df)] = get_user_data(contributor)
#                         print(f'Contributor {contributor.login} has been added to the database! :D')
#                     elif verbose: print(contributor.login + ' has already been processed. :P')
                        
#         except Exception as e:
#             print(f"Error processing license {license}: {str(e)}")
#             time.sleep(60)