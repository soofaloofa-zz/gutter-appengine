#!/usr/bin/env bash
port=8080
admin_port=8090
usage="Usage: $0 [-p N] [-a N]"

while getopts ":p:a:" opt; do
  case ${opt} in
    p )
      port=$OPTARG ;;
    a )
      admin_port=$OPTARG ;;
    : )
      echo "Invalid Option: -$OPTARG requires an argument" 1>&2
      exit 1
      ;;
    \? )
      echo $usage
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))

dev_appserver.py --port=$port --admin_port=$admin_port --enable_sendmail --storage_path="./data/" --require_indexes=yes .
