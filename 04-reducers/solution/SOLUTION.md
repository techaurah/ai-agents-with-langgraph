# Solution 04

Append holds 4 messages: ["msg-1", "msg-2", "msg-3", "msg-4"]. A multi-item update is extended as a unit, in order.

Overwrite holds exactly ["msg-4"]: the middle node's two-message list replaced the first message, and then the third node's list replaced that. The overwrite version's final length (1) understates even the damage: for one super-step the state briefly held the two-message list before losing it too. The teaching point is that reducer semantics apply per update, not per item, and a node returning a batch is one update. If a channel must accumulate batches, append is the reducer that treats each batch as a contribution rather than a replacement.
