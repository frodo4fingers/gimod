#! /usr/bin/bash

GITBIN=/usr/bin/git
# this should work as an alias to use instead of "git"
VERSION=`$GITBIN describe`
# echo $VERSION
IFS='.' read -ra PARTS <<< "$VERSION"
MAJOR=`echo ${PARTS} | cut -d '-' -f2`
MINOR="${PARTS[1]}"
# PATCH="${PARTS[2]}"
COMMITS=`$GITBIN rev-list HEAD | wc -l`

ID=`$GITBIN rev-parse HEAD`
IDBRANCH=${ID:0:7}

BRANCH=`$GITBIN branch | grep \* | cut -d ' ' -f2`
# echo $BRANCH

if [[ $1 == "commit" ]] && [[ "$#" -ne 1 ]]
then
    let COMMITS+=1
elif [[ $1 == "push" ]]
then
    let COMMITS+=1
    let MINOR+=1
fi

VERSION=$BRANCH"-"$MAJOR"."$MINOR"."$COMMITS"-"$IDBRANCH
echo $VERSION
GITCMD=`$GITBIN tag -a "$VERSION" -m "new version"`
eval $GITCMD
echo $VERSION > version.json

# GITCMD="$GITBIN "
# for var in "$@"
# do
#     GITCMD="$GITCMD \"$var\""
# done
# eval $GITCMD
