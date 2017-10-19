"""This profile mounts an Emulab hosted dataset on a number of servers through
an NFS server. 

Instructions:
The dataset is mounted on /mnt/dataset on the client nodes.  
"""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg

# Create a portal context.
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Create configuration parameter for the number of client nodes.
num_nodes = range(1,1000)
pc.defineParameter("num_nodes", "Number of Client Nodes", 
    portal.ParameterType.INTEGER, 1, num_nodes)

# Create configuration parameter for the dataset to mount.
datasets = [ ("urn:publicid:IDN+utah.cloudlab.us:ramcloud-pg0+stdataset+ldbc-snb-sf1000",
     "LDBC-SNB-SF1000") ]
pc.defineParameter("dataset", "Dataset to Mount", 
    portal.ParameterType.IMAGE, datasets[0], datasets)

params = pc.bindParameters()

node_names = ["nfs"]
for i in range(params.num_nodes):
  node_names.append("n%02d" % (i + 1))

# Setup a LAN for the clients
clan = request.LAN()
clan.best_effort = True
clan.vlan_tagging = True
clan.link_multiplexing = True

# Setup a LAN just for the blockstore
bslan = request.LAN()
bslan.best_effort = True
bslan.vlan_tagging = True
bslan.link_multiplexing = True

for name in node_names:
  node = request.RawPC(name)
  
  # Install and execute a script that is contained in the repository.
  node.addService(pg.Execute(shell="sh", command="/local/repository/setup.sh"))

  iface = node.addInterface("if1")

  clan.addInterface(iface)

  # If this is the NFS server, then connect the remote blockstore
  if name == "nfs":
    bs = request.RemoteBlockstore('b1', '/mnt/dataset', 'if1')
    bs.dataset = params.dataset
    bslan.addInterface(bs.interface)
    bsiface = node.addInterface("if2")
    bslan.addInterface(bsiface)

# Print the RSpec to the enclosing page.
pc.printRequestRSpec(request)
