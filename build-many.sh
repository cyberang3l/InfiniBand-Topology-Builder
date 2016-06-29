#!/bin/bash

chmod +x FatTreeBuilder.py

dest_dir=built-topologies
mkdir "${dest_dir}" 2> /dev/null

for ((n=2; n<=4; n++)); do
	for ((k=2; k<=19; k++)); do
		if [[ ${n} -eq 4 && ${k} -gt 12 ]]; then
			break
		fi
		echo "Building k-ary-n tree with k=${k}, n=${n}"
		./FatTreeBuilder.py -q -k ${k} -n ${n} > "${dest_dir}"/k-${k}-n-${n}.topo
		./FatTreeBuilder.py -q -k ${k} -n ${n} -f > "${dest_dir}"/k-${k}-n-${n}-Full.topo
	done
done

echo "All topologies built. Find the topology files in the directory "${dest_dir}""
