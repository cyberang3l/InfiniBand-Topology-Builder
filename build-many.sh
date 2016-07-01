#!/bin/bash

chmod +x FatTreeBuilder.py

dest_dir=built-topologies
mkdir "${dest_dir}" 2> /dev/null

for ((oo=1; oo<=4; oo*=2)); do
	for ((nn=2; nn<=4; nn++)); do
		for ((kk=2; kk<=19; kk++)); do
			if [[ ${nn} -eq 4 && ${kk} -gt 12 ]]; then
				break
			fi
			k=$(printf "%02d" ${kk})
			n=$(printf "%02d" ${nn})
			o=$(printf "%02d" ${oo})
			echo "Building k-ary-n tree with k=${k}, n=${n}, oversubscription=${o}"
			./FatTreeBuilder.py -q -k ${k} -n ${n} -o ${o} > "${dest_dir}"/k-${k}-n-${n}-o-${o}.topo 2> /dev/null
			ret=$?
			if [[ $ret -eq 0 ]]; then
				./FatTreeBuilder.py -q -k ${k} -n ${n} -o ${o} -f > "${dest_dir}"/k-${k}-n-${n}-o-${o}-Full.topo 2> /dev/null
			else
				echo "   cannot build this topology - Too many ports per switch required"
				rm -f "${dest_dir}"/k-${k}-n-${n}-o-${o}.topo
			fi
		done
	done
done

echo "All topologies built. Find the topology files in the directory "${dest_dir}""
