library(httr)
library(tidyverse)
library(jsonlite)
library(dotenv)

gather_projects <- function() {
  # limited to 25 for some reason
  r <- GET(url = paste0(Sys.getenv("REDMINE_URL"), "projects.json"),
           config = authenticate(Sys.getenv("REDMINE_USER"), Sys.getenv("REDMINE_PASSWORD"), type = "basic")
           )

  json_result <- fromJSON(content(r, as = "text"))$projects

  project_list <- json_result %>%
    as.data.frame()

  return(project_list)
}

gather_wikis <- function(identifier) {
  #Get the wikis for each project########
  r <- GET(url = paste0(Sys.getenv("REDMINE_URL"), "projects/", identifier, "/wiki/index.json"),
           config = authenticate(Sys.getenv("REDMINE_USER"), Sys.getenv("REDMINE_PASSWORD"), type = "basic")
           )

  json_result <- fromJSON(content(r, as = "text"))

  if (length(json_result$wiki_pages) == 0) {
    # this project has no wikis
    return(NA)
  }

  wikis <- fromJSON(content(r, as = "text"))$wiki_pages %>%
                                           select(title)

  return(wikis)
}

get_wiki_page_and_attachments <- function(identifier, wiki_title) {
  #Get the pages and attachments for each wiki###########
  r <- GET(url = paste0(Sys.getenv("REDMINE_URL"), "projects/", identifier, "/wiki/", wiki_title, ".json?include=attachments"),
           config = authenticate(Sys.getenv("REDMINE_USER"), Sys.getenv("REDMINE_PASSWORD"), type = "basic")
           )

  wiki_page <- fromJSON(content(r, as = "text"))$wiki_page

  # remove the attachments as it duplicates the rest of the dataframe
  wiki_page$attachments <- NA

  wiki_page_info <- wiki_page %>%
    as.data.frame()

  attachments <- fromJSON(content(r, as = "text"))$wiki_page$attachments

  if (length(attachments) > 0) {
    attachments <- attachments %>%
      mutate(project = identifier,
             wiki_title = wiki_title
             )
  }

  return(list(wiki_page_info, attachments))
}

# TODO: save the page content to a textile file in an appropriate subdirectory
# TODO: download all attachments
