#!/bin/bash

set -e
declare -gA pvc2Pod
declare -gA snapshot2Volume
declare -gA volume2Tags
declare -gA volume2PVC
declare -gA volume2PV
declare -gA volume2AZ
declare -gA volume2Size
declare -gA dpl2Replica
declare -gA pvc2NewVolume

logStep() {
  echo
  echo -e "\033[1;32m*** $1 ***\033[0m"
}

askDescription() {
  default_desc="Omaha Backup"

  read -p "What is the description of the backup to restore: " desc

  if [ "" = "$desc" ] ; then
    echo "Nothing provided, will use $default_desc"
    desc=$default_desc
  fi

  echo "Restoring $desc..."
}

createVolume() {
  local snap=$1
  local volume=${snapshot2Volume[$snap]}
  
  IFS=$'\n'
  for result in `aws ec2 create-volume --snapshot-id $snap --availability-zone ${volume2AZ[$volume]} --tag-specifications "ResourceType=volume,Tags=[${volume2Tags[$volume]}]"`; do
    if [[ "$result" = *VolumeId* ]]; then
      local new_vol=`echo $result| cut -d '"' -f 4`
    fi

    if [[ "$result" = *Size* ]]; then
      local size=`echo $result| awk '{print $2}'`
    fi
  done
  
  volume2Size[$new_vol]=$size
  volume2AZ[$new_vol]=${volume2AZ[$volume]}
  pvc2NewVolume[${volume2PVC[$volume]}]=$new_vol
 
  while true; do
    local result=`aws ec2 describe-volumes --volume-ids $new_vol --query "Volumes[*].State" --output text`
    [[ "$result" = "available" ]] && break
    echo "Waiting for $new_vol to be available... ($result)"
    sleep 5
  done
  echo "$new_vol created !"
}

fillPVCInfo() {
  logStep "Scanning PVC data"
  pvc2Pod["pvc-a87f0c51-3eb8-48d6-94ae-a086bc4f9f79"]='postgres-pvc-v12'
}

fillSnapshotInfo() {
  logStep "Scanning AWS snapshots"
  snapshot2Volume['snap-0ca0eb7ef7bc5cdb4']='vol-0e69abef562a3e356'

  for snap in ${!snapshot2Volume[@]}; do
    local volume=${snapshot2Volume[$snap]}
    fillVolumeInfo $volume
    echo "Found $snap for $volume (bound to ${volume2PV[$volume]} [${volume2PVC[$volume]}], mounted by ${pvc2Pod[${volume2PVC[$volume]}]})"
  done
}

fillVolumeInfo() {
  IFS=$'\n'
  
  for data in `aws ec2 describe-volumes --volume-ids $1 --query "Volumes[*].{AZ:AvailabilityZone,Tags:Tags[*]}" --output text`; do
 
	  if [[ $data == TAGS* ]] ; then
      #local tagn=$(echo $data| cut -f 2)
      #local tagv=$(echo $data| cut -f 3)
      #if [ "$tagn" = "kubernetes.io/created-for/pvc/name" ] ; then
        #local pvc=$tagv
      #elif [ "$tagn" = "kubernetes.io/created-for/pv/name" ] ; then
        #local pv=$tagv
      #fi
      local pvc="postgres-pvc-v12"
      local pv="pvc-a87f0c51-3eb8-48d6-94ae-a086bc4f9f79"
      local tagspec="{Key=kubernetes.io/cluster/DW,Value=owned}"
            tagspec="$tagspec,{Key=kubernetes.io/created-for/pv/name,Value=$pv}"
            tagspec="$tagspec,{Key=kubernetes.io/created-for/pvc/name,Value=$pvc}"
            tagspec="$tagspec,{Key=kubernetes.io/created-for/pvc/namespace,Value=omaha}"
    elif ! [ -z "$data" ] ; then
      local az=$data
    fi
  done
  unset IFS

  if [ -z "${pvc2Pod['pvc-a87f0c51-3eb8-48d6-94ae-a086bc4f9f79']}" ] || [ -z "$az" ] ; then
    echo "Could not find all volume info for volume $1"
    exit 1
  fi

  volume2Tags[$1]=$tagspec
  volume2PVC[$1]=$pvc
  volume2PV[$1]=$pv
  volume2AZ[$1]='ca-central-1a'
}

createPVCs() {
  logStep "Recreating PVCs (and their PVs)"
  for pvc in ${!pvc2NewVolume[@]}; do
    local volume=${pvc2NewVolume[$pvc]}
    createPV pv-$pvc $volume ${volume2AZ[$volume]} ${volume2Size[$volume]}
    createPVC $pvc pv-$pvc ${volume2Size[$volume]}
  done
}

createPV(){
  local name=$1
  local vol=$2
  local az=$3
  local region=${az::-1}
  local size=$4
  
  # Remove PV if present
  kubectl get pv $name >/dev/null 2>&1 && kubectl delete pv $name
  echo "Creating PV $name"
  cat <<EOF | kubectl apply -f -
kind: PersistentVolume
apiVersion: v1
metadata:
  name: $name
  labels:
    failure-domain.beta.kubernetes.io/region: $region
    failure-domain.beta.kubernetes.io/zone: $az
spec:
  capacity:
    storage: ${size}Gi
  accessModes:
  - ReadWriteOnce
  awsElasticBlockStore:
    fsType: ext4
    volumeID: aws://$az/$vol
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: failure-domain.beta.kubernetes.io/zone
          operator: In
          values:
          - $az
        - key: failure-domain.beta.kubernetes.io/region
          operator: In
          values:
          - $region
  storageClassName: gp2

EOF
}

createPVC(){
  local name=$1
  local pv=$2
  local size=$3

  # Remove PVC if present
  kubectl get pvc $name >/dev/null 2>&1 && kubectl delete pvc $name
  echo "Creating pvc $name"
  cat <<EOF | kubectl apply -f -
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: $name
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: ${size}Gi
  storageClassName: gp2
  volumeName: $pv
EOF
}

deletePVCs() {
  logStep "Deleting all PVCs (and the PVs they are bound with)"
  for pvc in ${!pvc2Pod[@]}; do
    local pv=`kubectl get pvc $pvc -o jsonpath='{.spec.volumeName}'`
    echo "Retaining pv $pv"
    kubectl patch pv $pv -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'
    echo "Deleting pvc $pvc"
    kubectl delete pvc $pvc
    echo "Deleting pv  $pv"
    kubectl delete pv $pv
  done
}

createVolumes() {
  logStep "Creating Volumes"
  for snap in ${!snapshot2Volume[@]}; do
    createVolume $snap
  done
}

scaleDown() {
  logStep "Scaling down deployments"
  for dpl in `kubectl get deployment.apps/postgres -o name`; do
    dpl2Replica[$dpl]=`kubectl get $dpl -o jsonpath='{.status.replicas}'`
    kubectl scale $dpl --replicas=0 --timeout=10m
  done
}			

scaleUp() {
  logStep "Scaling up deployments"
  kubectl scale deployment postgres --replicas=1 --timeout=10m
}

unit_test() {
  #fillPVCInfo
  #snapshot2Volume["snap-09b6341b84d48c70d"]="vol-0f984b9ee06014555"

  #fillVolumeInfo "vol-0f984b9ee06014555"
  #createVolume "snap-09b6341b84d48c70d"

  #kubectl scale sts sentry-sentry-postgresql --replicas 0
  #kubectl patch pv pvc-740a18b2-1734-4860-bfa4-d61008294aac -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'
  #kubectl delete pvc data-sentry-sentry-postgresql-0
  #kubectl patch pvc data-sentry-sentry-postgresql-0 -p '{"metadata":{"name":"data-sentry-sentry-postgresql-0-bkp"}}'
  #kubectl patch pvc data-sentry-sentry-postgresql-0 -p '{"metadata":{"selfLink": "/api/v1/namespaces/production/persistentvolumeclaims/data-sentry-sentry-postgresql-0-bkp"}}'
  #kubectl patch pvc data-sentry-sentry-postgresql-0 -p '{"spec":{"volumeName":"pvc-e1d437cc-291b-4a09-bfb1-16c61624f098"}}'
  #pvc2Pod["data-sentry-sentry-postgresql-0"]="sentry-postgresql-0"
  #deletePVCs
  #createPV pv-postgres vol-0f984b9ee06014555 ca-central-1a 16
  #createPVC data-sentry-sentry-postgresql-0 pv-postgres 16
  #scaleDown
  #scaleUp
  #pvc2NewVolume["data-sentry-postgres"]="vol-123"
  #volume2AZ["vol-123"]="ca-central-1"
  #volume2Size["vol-123"]=16
  #volume2AZ["vol-123"]="ca-central-1"
  #volume2Size["vol-123"]=16
  #createPVs
  #fillPVCInfo
  #fillSnapshotInfo
  #scaleDown
  #volume2AZ["vol-123"]="ca-central-1"
  #volume2Size["vol-123"]=16
  #createPVs
  snapshot2Volume['snap-0ca0eb7ef7bc5cdb4']='vol-0e69abef562a3e356'
  askDescription
  fillPVCInfo
  fillSnapshotInfo
  createVolumes
  scaleDown
  #deletePVCs
  createPVCs
  scaleUp
  exit
}

#unit_test

performRestoration(){
  askDescription
  fillPVCInfo
  fillSnapshotInfo
  createVolumes
  scaleDown
  deletePVCs
  createPVCs
  scaleUp
}

unit_test
