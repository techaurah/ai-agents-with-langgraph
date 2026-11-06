# Solution 23

The full-namespace prefix returns exactly 1 item (BrightPath Dental's profile): a prefix matches namespace element by element, so a two-element prefix selects exactly one company's partition. The upper-case query also returns 1 hit: the stand-in lowercases both the query and the stored JSON before matching, so case is not a filter. (Verify against the lab's store, whose profile values include company names; a profile without the word in its value cannot match any spelling of it.)

Together they pin the semantics the memory lessons rely on: namespaces select whose memory, queries select what about them, and neither silently widens. A prefix of ("leads",) is the wide search and should be a deliberate choice wherever it appears.
