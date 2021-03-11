# The VPN settings do not propagate to WSL correctly. This script can fix the issue:

import re

def main():
    with open("/etc/resolv.conf", 'rt') as f:
        lines = f.readlines()
    found = False
    for line in lines:
        if "10.50.10.50" in line:
            found = True
    if not found:
        lines.insert(0, "nameserver 10.50.10.50")
        lines.append("search corp.microsoft.com windeploy.ntdev.microsoft.com msft.net gtm.microsoft.com osdinfra.net qa.skype.gbl msstore.microsoftstore.com skype.net off svceng.com extest.microsoft.com ntdev.microsoft.com ap.gbl portal.gbl dns.microsoft.com phx.gbl sts.microsoft.com extranet.microsoft.com in-addr.arpa ip6.arpa sangam.microsoft.com ccc42azstack.com privatelink.database.windows.net privatelink.blob.core.windows.net privatelink.table.core.windows.net privatelink.queue.core.windows.net privatelink.file.core.windows.net privatelink.web.core.windows.net privatelink.dfs.core.windows.net ssc.microsoft.com local localdomain")
    with open("/etc/resolv.conf", 'wt') as f:
        f.write('\n'.join(lines))

if __name__ == '__main__':
    main()
