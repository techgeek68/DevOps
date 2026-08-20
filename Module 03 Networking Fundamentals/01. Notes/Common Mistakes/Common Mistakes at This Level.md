# Common Mistakes at This Level

---
**Diagnosing top down instead of bottom up.** 

Jumping straight into application logs before confirming basic reachability wastes time. Always confirm Layer 3 and Layer 4 first.

---
**Treating TTL as a value you only think about when first creating a record.** 

TTL needs active management around any planned infrastructure change, not just at creation time.

---
**Defaulting to sticky sessions instead of fixing the underlying architecture.** 

Sticky sessions are a workaround for stateful application servers, not a goal in themselves. The better long term fix is almost always moving session state to a shared store.

---
**Writing one giant security group rule instead of several specific ones.**

A rule allowing all traffic from `0.0.0.0/0` on all ports is sometimes added "temporarily" for convenience during testing and then forgotten. Default deny only protects you if the specific rules you add stay tightly scoped.

---
**Sizing a subnet for today's needs with no room for growth.** 

Address space is cheap to allocate generously up front and expensive to redesign later once real resources depend on it.

---
**Overlapping CIDR ranges across VPCs, accounts, and the office network.**

The cost is not paid on the day you allocate the range. It is paid on the day two networks need to be peered and cannot be, and by then real workloads depend on both.

---
**Debugging a name resolution problem with `ping` instead of `dig`.**

`ping` merges two questions, resolution and reachability, into one result. Separate them before trying to answer either.

---
**Testing only from localhost.**

`curl http://localhost` succeeding proves the process is running. It proves nothing about the firewall, the security group, or the bind address. A service bound to `127.0.0.1` passes every local test and is unreachable from every other machine on earth.

---
