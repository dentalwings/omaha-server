#!/bin/bash
DEFAULT_NAMESPACE=omaha
DEFAULT_DESCRIPTION="OmahaBackup_$(date +'%Y-%m-%d')"

usage() { echo """Usage: $0 [-v <volume_names>] [-n <namespace>] [-d <description>] 

<volume_names>:
  a comma-separated list of AWS volume names in the form vol-XXXXX

<namespace>:
  a valid namespace in the cluster where volumes will be searched (not used when -v is specified)

<description>:
  the description used when creating the snapshots. Use quotes if it contains space(s)
""" 1>&2; exit 1; }

parseParams() {
  while getopts ":v:n:d:" o; do
      case "${o}" in
    v)
        volumes=${OPTARG}
        ;;
    d)
        description=${OPTARG}
        ;;
    n)
        namespace=${OPTARG}
        ;;
    *)
        usage
        ;;
      esac
  done
  shift "$((OPTIND-1))"
}

initVariables() {

  if [ -z "$namespace" ]; then
    namespace=$DEFAULT_NAMESPACE
  fi
  echo "Namespace: $namespace"

  if [ -z "$description" ]; then
    description=$DEFAULT_DESCRIPTION
  fi
  echo "Description: $description"

  if [ -z "$volumes" ]; then
    for pvc in `kubectl -n $namespace get pvc -o=jsonpath='{range .items[*]}{.spec.volumeName}{"\n"}{end}'`; do
      echo -n "Searching volumes for $pvc... "
      vol=`aws ec2 describe-volumes --query "Volumes[?not_null(Tags[?Value == '$pvc'].Value)].VolumeId" --output text`
      if [[ -z "$vol" ]]; then
        echo "None found"
      elif [[ $vol =~ [[:space:]]+ ]]; then
        echo "Multiple found ($vol)"
        exit
      else
        echo "Found $vol"
        if [ -z "$volumes" ]; then
          volumes=$vol
        else
          volumes="$volumes,$vol"
        fi
      fi
    done
  fi
  if [ -z "$volumes" ]; then
    echo "No volume found to backup"
    exit
  fi
  echo "Volume(s): $volumes"
}

getVolumeTags() {
  IFS=$'\n'
  for data in `aws ec2 describe-volumes --volume-ids $1 --query "Volumes[*].{Tags:Tags[*]}" --output text`; do
    local tagn=$(echo $data| cut -f 2)
    local tagv=$(echo $data| cut -f 3)
    if [ -z "$tagspec" ]; then
      tagspec="{Key=$tagn,Value=$tagv}"
    else
      tagspec="$tagspec,{Key=$tagn,Value=$tagv}"
    fi
  done
  unset IFS
}

createSnapshots() {
  echo "$volumes"
  IFS=','
  for vol in $volumes; do
    echo "Creating snapshot for $vol"
    tagspec=""
    getVolumeTags $vol
  
    IFS=$'\n'
    for result in `aws ec2 create-snapshot --volume-id $vol --tag-specifications "ResourceType=snapshot,Tags=[{Key=Software,Value=Omaha},{Key=Team,Value=Infra},{Key=env,Value=prod},$tagspec]" --description "$description"`; do
      if [[ "$result" = *SnapshotId* ]]; then
        local new_snap=`echo $result| cut -d '"' -f 4`
      fi
    done
    IFS=','

    while true; do
      local result=`aws ec2 describe-snapshots --snapshot-ids $new_snap --query "Snapshots[*].State" --output text`
      [[ "$result" = "completed" ]] && break
      echo "Waiting for $new_snap to be available... ($result)"
      sleep 5
    done
    echo "$new_snap created !"
  done
  unset IFS
}
parseParams "$@"
initVariables
createSnapshots
