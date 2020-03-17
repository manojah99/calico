from github import Github
import time
import sys
import subprocess
import os
from threading import Timer
from datetime import datetime

def execute_cmd(cmd):
  time.sleep(1)
  try:
    try:
      p = subprocess.Popen(
                [cmd],
                stdout = subprocess.PIPE,
                shell = True)
      timer = Timer(60, p.kill)
      try:
        timer.start()
        #p.wait()
        (result, error) = p.communicate()
      finally:
        timer.cancel()
    except ValueError:
      pass
  except subprocess.CalledProcessError as e:
        sys.stderr.write("common::run_command() : [ERROR]: output = %s, error code = %s\n"
            % (e.output, e.returncode))
  return result

def run_attribution(basepath, repo, file):
  repo_path = basepath + '/' + repo
  os.chdir(repo_path)
  hash = execute_cmd('git rev-parse --short HEAD')
  hash = hash.strip()
  now = datetime.now()
  dt_string = now.strftime("%d-%m-%Y_%H:%M:%S")
  dt_string = str(dt_string).strip()
  cmd = 'java -jar wss-unified-agent-20.2.1.jar -c wss-unified-agent.config -d ' \
        + repo_path + ' -apiKey 40448334219b4e0696e38c375188d990302371c58bdb46b8b896bfbdb51dd836 -product calico -productVersion 3.13.1 -project ' \
        + repo + ' -projectVersion ' + hash + ' -projectTag release:' + hash + ' -scanComment ' + dt_string
  print cmd, '\n'
  #print '\n',repo, hash
  #print cmd, '\n'
  file.write(cmd)
  file.write('\n')

if __name__ == "__main__":
  # repo details
  repos = [
      'calico',
      'calicoctl',
      'cni-plugin',
      'node',
      'app-policy',
      'felix',
      'kube-controllers',
      'networking-calico',
      'pod2daemon',
      'typha'
      ]
  untagged_repos = [
      'libcalico-go',
      'confd'
      ]
  tagname = 'v3.13.1'
  gitproject = 'projectcalico'

  #store wss configuration
  file = open('wss-unified-agent.config','w')
  file.write('''wss.url=https://app.whitesourcesoftware.com/agent
checkPolicies=false
forceCheckAllDependencies=true
forceUpdate=false
forceUpdate.failBuildOnPolicyViolation=false
log.level=debug
npm.runPreStep=true
npm.yarnProject=true
go.resolveDependencies=true
go.collectDependenciesAtRuntime=true
go.dependencyManager=module
html.resolveDependencies=true
python.resolveDependencies=true
includes=**/*.rb **/*.tpl **/*.mod **/*.sh **/*.go **/*.py **/*.js **/*.min.js
excludes=**/*sources.jar **/*javadoc.jar **/vendor/**
case.sensitive.glob=false
followSymbolicLinks=true
archiveExtractionDepth=7
archiveIncludes=**/*.war **/*.ear **/*.zip
''')
  file.close()

  # Clone libraries
  for repo in repos:
    if repo in untagged_repos:
      continue
    cmd = 'git clone -b ' + tagname + ' --single-branch https://github.com/' + gitproject + '/' + repo
    print execute_cmd(cmd)

  for repo in untagged_repos:
    if 'libcalico-go' == repo:
      new_tag = 'v3.13.0-0.dev'
      cmd = 'git clone -b ' + new_tag + ' --single-branch https://github.com/' + gitproject + '/' + repo
      print execute_cmd(cmd)
    if 'confd' == repo:
      new_tag = 'v3.13.0-0.dev'
      cmd = 'git clone -b ' + new_tag + ' --single-branch https://github.com/' + gitproject + '/' + repo
      print execute_cmd(cmd)

  # Generate attribution script
  basepath = os.getcwd()
  file = open('run.sh', 'w')

  for repo in repos:
    run_attribution(basepath, repo, file)
  for repo in untagged_repos:
    run_attribution(basepath, repo, file)
  file.close()
