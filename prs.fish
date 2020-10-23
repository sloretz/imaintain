#!/usr/bin/env fish

cd (dirname (status --current-filename))

for repo in (ls -d1 repos/*/*)
  cd ./$repo
  gh pr list
  cd -
end
