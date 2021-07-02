// run this on your projects page to get all projects rather than only 25
project_ids = ["project_identifier"]
$("a.project").each(function(i, e) {
  let project_id = e.href.split("/").slice(-1)[0];
  project_ids.push(
    project_id
  )
})

// copy the output of this and put it into a csv file
project_ids.join("\n")
