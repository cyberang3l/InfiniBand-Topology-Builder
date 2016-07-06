#!/usr/bin/env python
#
# Copyright (C) 2016 Vangelis Tasoulas <vangelis@tasoulas.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
import os
import sys
import argparse
import logging
import time
from collections import OrderedDict

__all__ = [
    'print_', 'LOG'
]

PROGRAM_NAME = 'FatTreeBuilder'
VERSION = '0.2.2'
AUTHOR = 'Vangelis Tasoulas'

LOG = logging.getLogger('default.' + __name__)

################################################
############### HELPER FUNCTIONS ###############
################################################

#----------------------------------------------------------------------
def error_and_exit(message):
    """
    Prints the "message" and exits with status 1
    """
    print("\nFATAL ERROR:\n" + message + "\n", file=sys.stderr)
    exit(1)

#----------------------------------------------------------------------
def print_(value_to_be_printed, print_indent=0, spaces_per_indent=4, endl="\n"):
    """
    This function, among anything else, it will print dictionaries (even nested ones) in a good looking way

    # value_to_be_printed: The only needed argument and it is the
                           text/number/dictionary to be printed
    # print_indent: indentation for the printed text (it is used for
                    nice looking dictionary prints) (default is 0)
    # spaces_per_indent: Defines the number of spaces per indent (default is 4)
    # endl: Defines the end of line character (default is \n)

    More info here:
    http://stackoverflow.com/questions/19473085/create-a-nested-dictionary-for-a-word-python?answertab=active#tab-top
    """

    if(isinstance(value_to_be_printed, dict)):
        for key, value in value_to_be_printed.iteritems():
            if(isinstance(value, dict)):
                print_('{0}{1!r}:'.format(print_indent * spaces_per_indent * ' ', key))
                print_(value, print_indent + 1)
            else:
                print_('{0}{1!r}: {2}'.format(print_indent * spaces_per_indent * ' ', key, value))
    else:
        string = ('{0}{1}{2}'.format(print_indent * spaces_per_indent * ' ', value_to_be_printed, endl))
        sys.stdout.write(string)

#----------------------------------------------------------------------
def int_to_hex_str(number, hex_length = -2, prefix_with_0x = False):
    """
    Converts an int to a hex string with the number of hex_length zeros prepended
    """
    hex_str = "{0:#0{1}x}".format(number, hex_length + 2)

    if (not prefix_with_0x):
        hex_str = hex_str[2:len(hex_str)]

    return hex_str

#----------------------------------------------------------------------

########################################
###### Configure logging behavior ######
########################################
# No need to change anything here

def _configureLogging(loglevel):
    """
    Configures the default logger.

    If the log level is set to NOTSET (0), the
    logging is disabled

    # More info here: https://docs.python.org/2/howto/logging.html
    """
    numeric_log_level = getattr(logging, loglevel.upper(), None)
    try:
        if not isinstance(numeric_log_level, int):
            raise ValueError()
    except ValueError:
        error_and_exit('Invalid log level: %s\n'
        '\tLog level must be set to one of the following:\n'
        '\t   CRITICAL <- Least verbose\n'
        '\t   ERROR\n'
        '\t   WARNING\n'
        '\t   INFO\n'
        '\t   DEBUG    <- Most verbose'  % loglevel)

    defaultLogger = logging.getLogger('default')

    # If numeric_log_level == 0 (NOTSET), disable logging.
    if(not numeric_log_level):
        numeric_log_level = 1000
    defaultLogger.setLevel(numeric_log_level)

    logFormatter = logging.Formatter()

    defaultHandler = logging.StreamHandler()
    defaultHandler.setFormatter(logFormatter)

    defaultLogger.addHandler(defaultHandler)

#######################################################
###### Add command line options in this function ######
#######################################################
# Add the user defined command line arguments in this function

def _command_Line_Options():
    """
    Define the accepted command line arguments in this function

    Read the documentation of argparse for more advanced command line
    argument parsing examples
    http://docs.python.org/2/library/argparse.html
    """

    parser = argparse.ArgumentParser(description=PROGRAM_NAME + " will build a k-ary-n-tree of a given k/n. The output is in the format used by ibnetdiscover utility,"
                                     " meaning that you can use the topologies generated by this script directly in ibsim. The output is printed in STDOUT, so if you"
                                     " want to save the generated topology in a file for further analysis or use with different tools, you need to redirect the output"
                                     " of the script in a file.")

    parser.add_argument("-v", "--version",
                        action="version", default=argparse.SUPPRESS,
                        version=VERSION,
                        help="show program's version number and exit")

    loggingGroupOpts = parser.add_argument_group('Logging Options', 'List of optional logging options')
    loggingGroupOpts.add_argument("-q", "--quiet",
                                  action="store_true",
                                  default=False,
                                  dest="isQuiet",
                                  help="Disable logging in the console.")
    loggingGroupOpts.add_argument("-l", "--loglevel",
                                  action="store",
                                  default="INFO",
                                  dest="loglevel",
                                  metavar="LOG_LEVEL",
                                  help="LOG_LEVEL might be set to: CRITICAL, ERROR, WARNING, INFO, DEBUG. (Default: INFO)")

    parser.add_argument("-k", "--ftree-half-ports-of-each-switch",
                        action="store",
                        type=int,
                        required=True,
                        dest="k",
                        metavar="K",
                        help="k (k-ary-n-Tree) is half the number of ports for each switch")
    parser.add_argument("-n", "--ftree-levels",
                        action="store",
                        type=int,
                        required=True,
                        dest="n",
                        metavar="N",
                        help="n (k-ary-n-Tree) is the number of levels in the tree")
    parser.add_argument("-f", "--fully-connected-root-switches",
                        action="store_true",
                        default=False,
                        dest="fully_connected_roots",
                        help="In a k-ary-n-tree, the root switches will have only half of their ports connected. If this options is used, then another k-ary-(n-1)-tree will be connected to the empty ports of the root switches, effectively doubling the number of nodes in the network.")
    parser.add_argument("-o", "--oversubscription",
                        action="store",
                        choices=[1, 2, 3, 4],
                        type=int,
                        default=1,
                        dest="oversub",
                        help="Choose the oversubscription rate.")


    opts = parser.parse_args()

    if(opts.isQuiet):
        opts.loglevel = "NOTSET"

    return opts

##################################################
############### WRITE MAIN PROGRAM ###############
##################################################

if __name__ == '__main__':
    """
    Write the main program here
    """
    # Parse the command line options
    options = _command_Line_Options()
    # Configure logging
    _configureLogging(options.loglevel)

    LOG.info("{} v{} is running...\n".format(PROGRAM_NAME, VERSION))

    ######################################
    #LOG.critical("CRITICAL messages are printed")
    #LOG.error("ERROR messages are printed")
    #LOG.warning("WARNING messages are printed")
    #LOG.info("INFO message are printed")
    #LOG.debug("DEBUG messages are printed")

    # The output of ibnetdiscover looks like this:
    # vendid=0x0
    # devid=0x0
    # sysimgguid=0x200000
    # switchguid=0x200000(200000)
    # Switch  4 "S-0000000000200000"          # "Switch0" base port 0 lid 1 lmc 0
    # [1]     "S-0000000000200004"[3]         # "Switch4" lid 7 4xSDR
    # [2]     "S-0000000000200005"[3]         # "Switch5" lid 9 4xSDR
    # [3]     "H-0000000000100000"[1](100001)                 # "Hca0" lid 2 4xSDR
    # [4]     "H-0000000000100002"[1](100003)                 # "Hca1" lid 5 4xSDR
    #
    # vendid=0x0
    # devid=0x0
    # sysimgguid=0x10000e
    # caguid=0x10000e
    # Ca      1 "H-000000000010000e"          # "Hca7"
    # [1](10000f)     "S-0000000000200003"[4]         # lid 20 lmc 0 "Switch3" lid 6 4xSDR
    #
    # Based on this output, here I make template lines with placeholders for different purposes:
    # The place holders must be replced with:
    #    node_type_long = Switch or Hca
    #    node_type_short = S or H (for switch or hca respectively)
    #    total_port = total number of ports for this node
    #    node_guid = the GUID of this node
    #    node_name = the name of this node
    node_line = '{node_type_long}\t{total_ports} "{node_type_short}-{node_guid}"\t\t# "{node_name}"'
    #    local_port = An integer showing which local port is connected to a remote
    #    rem_node_type_short = S or H
    #    rem_node_guid = The guid of the remote node
    #    rem_port = the port of the remote node that we connect with
    #    rem_node_name = the name of the remote node
    #    link_speed = something like 4xSDR, 4xDDR, 4xQDR, 4xFDR, 4xEDR, 4xHDR indicating the link speed
    #    local_port_guid = If the local port is an HCA port, then we need to define the local port guid
    #    rem_port_guid = If the remote port is an HCA port, then we need to define the remote port guid
    port_lines = {}
    port_lines['switch'] = {}
    # line to use if local is a switch, remote is a switch
    port_lines['switch']['switch'] = '[{local_port}]\t"{rem_node_type_short}-{rem_node_guid}"[{rem_port}]\t\t# "{rem_node_name}" lid 0 {link_speed}'
    # line to use if local is a switch, remote is an hca
    port_lines['switch']['hca'] = '[{local_port}]\t"{rem_node_type_short}-{rem_node_guid}"[{rem_port}]({rem_port_guid}) \t\t# "{rem_node_name}" lid 0 {link_speed}'
    port_lines['hca'] = {}
    # line to use if local is an hca, remote is a switch
    port_lines['hca']['switch'] = '[{local_port}]({local_port_guid}) \t"{rem_node_type_short}-{rem_node_guid}"[{rem_port}]\t\t# lid 0 lmc 0 "{rem_node_name}" lid 0 {link_speed}'
    # line to use if local is an hca, remote is an hca
    port_lines['hca']['hca'] = '[{local_port}]({local_port_guid}) \t"{rem_node_type_short}-{rem_node_guid}"[{rem_port}]({rem_port_guid}) \t\t# lid 0 lmc 0 "{rem_node_name}" lid 0 {link_speed}'

    hca_guid_base = 0x1000000 # We want to define a GUID for each HCA and each port. The node GUID of the first Hca will be hca_guid_base
    port_guid_base = hca_guid_base + 0x1000000
    sw_guid_base = port_guid_base + 0x1000000
    default_link_speed = '4xEDR'
    max_sw_ports = 48 # Max ports per switch in the generated topology. If the user chooses some insanely huge topology
                      # that requires very many ports per sw, do not build the topology. At the moment, the OmniPath architecture
                      # offers switches with up to 48 ports, Oracle IB EDR Switches offer up to 38 4x ports and Mellanox switches
                      # offer up to 36 ports.

    k = options.k # k (k-ary-n-Tree) is half the number of ports for each switch
    n = options.n # n (k-ary-n-Tree) is the number of levels in the tree

    fully_connected_roots = options.fully_connected_roots # In a k-ary-n-tree, the root switches will have only half of their ports connected.
                                                          # If fully_connected_roots = True, then another k-ary-n-tree will be connected to the
                                                          # empty ports of the root switches, effectively doubling the number of nodes in the
                                                          # network.

    oversub = options.oversub

    # Find how many ports per switch are needed in the leaf level:
    #     k ports goes up, and k * oversub ports go down to the hosts.
    # If more than max_sw_ports, then exit.
    ports_per_sw = k + (k * oversub)
    if ports_per_sw > max_sw_ports:
        error_and_exit("{} ports are needed per switch, but the"
                       " max allowed ports per switch are {}".format(
                           ports_per_sw, max_sw_ports))

    sw_per_row = k**(n-1)

    if fully_connected_roots:
        number_of_sw  = sw_per_row * ((n * 2) - 1)
        number_of_hca = k**n * 2 * oversub
    else:
        number_of_sw  = sw_per_row * n
        number_of_hca = k**n * oversub

    topology = OrderedDict()

    # Initialize all switches
    for sw_no in xrange(number_of_sw):
        sw = "Switch{}".format(sw_no)
        topology[sw] = {}

        topology[sw]['node_type'] = 'switch'
        topology[sw]['ports'] = {}
        topology[sw]['guids'] = {}

        topology[sw]['guids']['node'] = sw_guid_base + sw_no
        for port in xrange(1, ports_per_sw + 1):
            topology[sw]['ports'][port] = None
        topology[sw]['total_ports'] = len(topology[sw]['ports'])

    # Initialize all Hca's
    for hca_no in xrange(number_of_hca):
        hca = "Hca{}".format(hca_no)
        topology[hca] = {}
        topology[hca]['node_type'] = 'hca'
        topology[hca]['guids'] = {}
        topology[hca]['ports'] = {}

        #topology[hca]['guids']['node'] = hca_guid_base + hca_no * 2
        topology[hca]['guids']['node'] = hca_guid_base + hca_no
        topology[hca]['ports'][1] = None
        topology[hca]['total_ports'] = len(topology[hca]['ports'])
        #topology[hca]['guids'][1] = topology[hca]['guids']['node'] + 1
        topology[hca]['guids'][1] = port_guid_base + hca_no

    # First connect the switches between them, to form the fat tree.
    for sw_no in xrange(number_of_sw):
        sw = "Switch{}".format(sw_no)
        level = sw_no // sw_per_row

        remote_port_offset = k
        remote_sw_offset = 0

        # If currently processed level is on the root switches, do nothing.
        # We start processing the connectivity from the leaf switches and we go upwards,
        # meaning that when we reach the root switches, the connectivity is already established.
        if (level == (n - 1)):
            continue
        # If the roots are fully connected, the level variable will take values
        # greater than n. This is an indication that we have to build a second
        # subtree.
        elif (level > (n - 1)):
            level -= n
            # If we are processing the level before the root switches on the second subtree
            # We need to have an offset in the remote switch IDs and the ports of the root switches,
            # because half of the ports are already occupied by the first subtree.
            if (level == (n - 2)):
                remote_port_offset = 0
                remote_sw_offset = n * sw_per_row

        # The first k ports connect to the second k ports of the
        # switches in the upwards direction.
        # level = 0 indicates we are on the leaf switches.
        # level > 0 indicates we are going upwards towards the root switches.

        start_sw_upper_row = (level * sw_per_row) + sw_per_row
        sw_index_this_row = sw_no - (level * sw_per_row)
        sw_per_port_step_upper_row = k**level
        pattern_multiplier = (sw_index_this_row // sw_per_port_step_upper_row // k) * sw_per_port_step_upper_row

        for port in xrange(1, k + 1):
            remote_sw_no = \
                start_sw_upper_row + \
                (port - 1) * sw_per_port_step_upper_row + \
                pattern_multiplier * k + \
                sw_index_this_row % sw_per_port_step_upper_row - \
                remote_sw_offset


            remote_sw = "Switch{}".format(remote_sw_no)

            remote_port = remote_port_offset + 1
            while topology[remote_sw]['ports'][remote_port] is not None:
                remote_port += 1

            topology[sw]['ports'][port] = {remote_sw: remote_port}
            topology[remote_sw]['ports'][remote_port] = {sw: port}


    # Then connect the HCAs to the leaf switches.
    for hca_no in xrange(number_of_hca):
        hca = "Hca{}".format(hca_no)
        sw_no = hca_no // (k * oversub)
        if (sw_no > sw_per_row - 1):
            sw_no += (n - 1) * sw_per_row
        sw = "Switch{}".format(sw_no)
        port = hca_no % (k * oversub) + (k + 1)
        if sw_no > sw_per_row:
            # For fully connected roots
            sw_no = n * sw_per_row + (sw_no - n * sw_per_row)

        topology[hca]['ports'][1] = {sw: port}
        topology[sw]['ports'][port] = {hca: 1}

    # Delete nodes that are not connected at all.
    # (This will never really delete anything with the current implementation
    # but keep it here for the future.)
    for node_name in topology.keys():
        empty = 1
        for port in xrange(1, topology[node_name]['total_ports'] + 1):
            if (topology[node_name]['ports'][port]):
                empty = 0
                break

        if (empty):
            del topology[node_name]


    # Print the topology
    print('#')
    print('# Topology file: generated with FatTreeBuilder.py on {}'.format(time.ctime()))
    print('# https://github.com/cyberang3l/InfiniBand-Topology-Builder/')
    print('#')
    print('# Topology description')
    print('# -------------------------------')
    print('# k = {}, n = {}, oversubscription = {}{fully_populated}'.format(k, n, oversub, fully_populated=', Fully populated' if fully_connected_roots else ''))
    print('# Total number of nodes: {}'.format(number_of_hca + number_of_sw))
    print('# Total number of Switches: {}'.format(number_of_sw))
    print('# Total number of HCAs: {}'.format(number_of_hca))
    print('#')
    print('')

    for local_node_name in topology.keys():
        node_type = topology[local_node_name]['node_type']
        node_type_long = "Ca" if node_type == 'hca' else "Switch"
        node_type_short = "H" if node_type == 'hca' else "S"
        node_guid = int_to_hex_str(topology[local_node_name]['guids']['node'], 16)


        print('vendid=0x0')
        print('devid=0x0')
        print('sysimgguid={node_guid_with_0x}'.format(node_guid_with_0x = int_to_hex_str(topology[local_node_name]['guids']['node'], prefix_with_0x=True)))
        if node_type == 'switch':
            print('switchguid={node_guid_with_0x}({node_guid})'.format(node_guid_with_0x = int_to_hex_str(topology[local_node_name]['guids']['node'],
                                                                                                          prefix_with_0x=True),
                                                                       node_guid = int_to_hex_str(topology[local_node_name]['guids']['node'])))
        elif node_type == 'hca':
            print('caguid={node_guid_with_0x}'.format(node_guid_with_0x = int_to_hex_str(topology[local_node_name]['guids']['node'], prefix_with_0x=True)))

        print(node_line.format(node_type_long = node_type_long,
                               total_ports = topology[local_node_name]['total_ports'],
                               node_type_short = node_type_short,
                               node_guid = node_guid,
                               node_name = local_node_name))
        for port in xrange(1, topology[local_node_name]['total_ports'] + 1):
            node_port_guid = int_to_hex_str(topology[local_node_name]['guids'][port]) if node_type == 'hca' else None
            if topology[local_node_name]['ports'][port]:
                rem_node_name = topology[local_node_name]['ports'][port].keys().pop()
                rem_node_port = topology[local_node_name]['ports'][port].values().pop()
                rem_node_type = topology[rem_node_name]['node_type']
                rem_node_type_long = "Ca" if rem_node_type == 'hca' else "Switch"
                rem_node_type_short = "H" if rem_node_type == 'hca' else "S"
                rem_node_guid = int_to_hex_str(topology[rem_node_name]['guids']['node'], 16)
                rem_node_port_guid = int_to_hex_str(topology[rem_node_name]['guids'][rem_node_port]) if rem_node_type == 'hca' else None

                print(port_lines[node_type][rem_node_type].format(local_port = port,
                                                                  rem_node_type_short = rem_node_type_short,
                                                                  rem_node_guid = rem_node_guid,
                                                                  rem_port = rem_node_port,
                                                                  rem_node_name = rem_node_name,
                                                                  link_speed = default_link_speed,
                                                                  rem_port_guid = rem_node_port_guid,
                                                                  local_port_guid = node_port_guid))

            if (port == topology[local_node_name]['total_ports']):
                print('')

    # Print the informational message in the STDERR with LOG, so that it doesn't get in the output file when STDOUT is redirected in a file.
    LOG.info("Total number of nodes: {}\n"
             "Total number of Switches: {}\n"
             "Total number of HCAs: {}\n".format(number_of_hca + number_of_sw, number_of_sw, number_of_hca))

    LOG.info("If you want to generate a dot file from the generated topology, please use the script InfiniBand-Graphviz-ualization.\n"
             "You can get a copy at: https://github.com/cyberang3l/InfiniBand-Graphviz-ualization.")

    # Uncomment the following to see how the topology looks like in the dictionary
    #print_(topology)
