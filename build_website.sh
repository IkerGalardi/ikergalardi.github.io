#!/bin/sh

./clean_website.sh

cd hugo/ 		|| exit
hugo 			|| exit
cp -r public/* ../ 	|| exit
