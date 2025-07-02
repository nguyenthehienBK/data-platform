#!/bin/bash

# DOCKER IMAGE VERSION

# you need edit [version] of docker image
version="$1"
echo "version docker image to build: $version"

if [ -z "$version" ];
then
 echo "you need edit [version] of docker image"
 exit 0
fi

# init variable as flag to build image docker

is_build_image=1


if [ $is_build_image -eq 1 ];
then
  docker build --rm -t my-airflow:$version -f Dockerfile .
fi